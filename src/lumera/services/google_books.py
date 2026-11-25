import os
import requests
from dotenv import load_dotenv

from lumera.models import Book

load_dotenv()

BASE_URL = "https://www.googleapis.com/books/v1/volumes"

def normalize_language(language: str | None) -> str | None:
    """Normaliza o codigo de idioma para comparacao."""

    if not language: 
        return None

    return language.strip().replace("_", "-").split("-")[0].lower()


def search_google_books(
    query: str,
    language: str = "pt-BR",
    max_results: int = 10,
) -> list[Book]:
    """Pesquisa livros utilizando a Google Books API."""

    if not query.strip():
        raise ValueError("Search query cannot be empty")

    if not 1 <= max_results <= 40:
        raise ValueError("max_results must be between 1 and 40")

    api_key = os.getenv("GOOGLE_BOOKS_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_BOOKS_API_KEY is not configured")

    requested_language = normalize_language(language)

    params = {
        "q": query,
        "langRestrict": requested_language,
        "maxResults": 40,
        "printType": "books",
        "orderBy": "relevance",
        "key": api_key,
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

    except requests.HTTPError as error:
        raise RuntimeError(
            f"Google Books API returned HTTP "
            f"{error.response.status_code}"
        ) from None

    except requests.RequestException:
        raise RuntimeError(
            "Failed to connect to Google Books API"
        ) from None

    books = []

    for item in data.get("items", []):
        book = parse_google_book(item)

        if book is None:
            continue

        if normalize_language(book.language) != requested_language:
            continue

        books.append(book)

        if len(books) >= max_results:
            break

    return books

def parse_google_book(item: dict) -> Book | None:
    """Converte um resultado da API em um objeto Book."""

    info = item.get("volumeInfo", {})

    title = info.get("title")

    if not title or not title.strip():
        return None

    identifiers = info.get("industryIdentifiers", [])

    isbn = next(
        (
            identifier.get("identifier")
            for identifier in identifiers
            if identifier.get("type") == "ISBN_13"
        ),
        None
    )

    if isbn is None:
        isbn = next (
            (
                identifier.get("identifier")
                for identifier in identifiers
                if identifier.get("type") == "ISBN_10"
            ),
            None,
        )

    pages = info.get("pageCount")

    if not isinstance(pages, int) or pages <= 0:
        pages = None

    image_links = info.get("imageLinks", {})

    return Book(
        title=title,
        authors=info.get("authors", []),
        isbn=isbn,
        pages=pages,
        genres=info.get("categories", []),
        synopsis=info.get("description"),
        language=info.get("language"),
        cover_url=image_links.get("thumbnail"),
        source="google_books", 
    )