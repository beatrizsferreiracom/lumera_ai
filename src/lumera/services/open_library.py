import os 
import requests
import re
import time
from dotenv import load_dotenv

from lumera.models import Book
from lumera.utils.languages import(
    normalize_language,
    to_open_library_language,
)

load_dotenv()

BASE_URL = "https://openlibrary.org/search.json"
COVER_URL = "https://covers.openlibrary.org/b/id"
EDITION_BASE_URL = "https://openlibrary.org"


def search_open_library(
    query: str,
    language: str = "pt-BR",
    max_results: int = 10,
) -> list[Book]:
    """Pesquisa livros utilizando a Open Library API."""

    if not query.strip():
        raise ValueError("Search query cannot be empty")

    if not 1 <= max_results <= 40:
        raise ValueError("max_results must be between 1 and 40")

    normalized_language = normalize_language(language)

    language_code = to_open_library_language(language)

    contact_email = os.getenv("OPEN_LIBRARY_CONTACT_EMAIL")

    user_agent = "Lumera/0.1.0"

    if contact_email:
        user_agent += f" ({contact_email})"

    headers = {
        "Use-Agent": user_agent,
        "Accept": "application/json",
    }

    params = {
        "q": f"({query}) AND language:{language_code}",
        "lang": normalized_language,
        "limit": 40,
        "fields": (
            "key,title,author_name,subject,"
            "editions,editions.key,editions.title,"
            "editions.language"
        ),
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

    except requests.HTTPError as error:
        raise RuntimeError(
            f"Open Library API returned HTTP "
            f"{error.response.status_code}"
        ) from None

    except requests.RequestException:
        raise RuntimeError(
            "Failed to connect to Open Library API"
        ) from None

    
    books = []

    for item in data.get("docs", []):
        parsed = parse_open_library_book(
            item,
            normalized_language,
            language_code,
        )

        if parsed is None:
            continue

        book, edition_key = parsed

        if edition_key:
            edition = get_open_library_edition(
                edition_key,
                headers,
            )

            book = enrich_open_library_book(
                book,
                edition,
            )

        books.append(book)

        if len(books) >= max_results:
            break

    return books


def parse_open_library_book(
    item: dict,
    language: str,
    language_code: str,
) -> tuple[Book, str | None] | None:
    """Converte um resultado da Open Library em Book."""

    editions = item.get("editions", {}).get("docs", [])

    matching_edition = next(
        (
            edition
            for edition in editions
            if language_code in (
                edition.get("language") or []
            )
        ),
        None,
    )

    if matching_edition is None:
        return None

    title = matching_edition.get("title")

    if not title or not title.strip():
        return None

    authors = item.get("author_name") or []

    subjects = item.get("subject") or []

    book = Book(
        title=title,
        authors=authors,
        genres=subjects[:15],
        language=language,
        source="open_library",
    )

    edition_key = matching_edition.get("key")

    return book, edition_key


def get_open_library_edition(
    edition_key : str,
    headers: dict[str, str],
) -> dict:
    """Recupera os dados de uma edicao especifica."""

    if not re.fullmatch(r"/books/OL\d+M", edition_key):
        return{}

    url = f"{EDITION_BASE_URL}{edition_key}.json"

    # Respeita o intervalo entre requisicoes sequenciais.
    time.sleep(1)

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException:
        return{}


def enrich_open_library_book(
        book: Book,
        edition: dict,
) -> Book:
    """Complementa os dados bibliograficos de um livro."""

    isbn_13 = edition.get("isbn_13") or []
    isbn_10 = edition.get("isbn_10") or []

    isbn = next(iter(isbn_13), None)

    if isbn is None:
        isbn = next(iter(isbn_10), None)

    pages = edition.get("number_of_pages")

    if type(pages) is not int or pages <= 0:
        pages = None

    covers = edition.get("covers") or []

    cover_id = next(
        (
            cover
            for cover in covers
            if type(cover) is int and cover > 0
        ),
        None
    )

    cover_url = None

    if cover_id is not None:
        cover_url = f"{COVER_URL}/{cover_id}-M.jpg"

    description = edition.get("description")

    if isinstance(description, dict):
        description = description.get("value")

    if not isinstance(description, str):
        description = None

    return Book(
        **{
            **book.model_dump(),
            "isbn": isbn or book.isbn,
            "pages": pages or book.pages,
            "cover_url": cover_url or book.cover_url,
            "synopsis": description or book.synopsis,
        }
    )