from unittest.mock import patch

import pytest
import requests

from lumera.models import Book
from lumera.services.open_library import (
    parse_open_library_book,
    enrich_open_library_book,
    get_open_library_edition,
    search_open_library,
)


def test_parse_open_library_book():
    item = {
        "title": "The Hobbit",
        "author_name": ["J.R.R. Tolkien"],
        "subject": ["Fantasy", "Adventure"],
        "editions": {
            "docs": [
                {
                    "key": "/books/OL123M",
                    "title": "The Hobbit",
                    "language": ["eng"],
                },
                {
                    "key": "/books/OL456M",
                    "title": "O Hobbit",
                    "language": ["por"],
                },
            ]
        },
    }

    result = parse_open_library_book(
        item,
        language="pt",
        language_code="por",
    )

    assert result is not None

    book, edition_key = result

    assert isinstance(book, Book)
    assert book.title == "O Hobbit"
    assert book.authors == ["J.R.R. Tolkien"]
    assert book.genres == ["Fantasy", "Adventure"]
    assert book.language == "pt"
    assert book.source == "open_library"
    assert edition_key == "/books/OL456M"


def test_parse_book_without_matching_language():
    item = {
        "title": "The Hobbit",
        "editions": {
            "docs": [
                {
                    "title": "The Hobbit",
                    "language": ["eng"],
                }
            ]
        },
    }

    result = parse_open_library_book(
        item,
        language="pt",
        language_code="por",
    )

    assert result is None


def test_parse_book_without_editions():
    result = parse_open_library_book(
        {"title": "Example Book"},
        language="pt",
        language_code="por",
    )

    assert result is None


def test_parse_book_without_title():
    item = {
        "editions": {
            "docs": [
                {
                    "language": ["por"],
                }
            ]
        }
    }

    result = parse_open_library_book(
        item,
        language="pt",
        language_code="por",
    )

    assert result is None


def test_enrich_open_library_book():
    book = Book(
        title="Example Book",
        language="pt",
        source="open_library",
    )

    edition = {
        "isbn_13": ["9788595086081"],
        "isbn_10": ["8595086087"],
        "number_of_pages": 320,
        "covers": [14849956],
        "description": {
            "value": "Example description."
        },
    }

    enriched = enrich_open_library_book(
        book,
        edition,
    )

    assert enriched.title == book.title
    assert enriched.language == book.language
    assert enriched.isbn == "9788595086081"
    assert enriched.pages == 320
    assert enriched.synopsis == "Example description."

    assert enriched.cover_url == (
        "https://covers.openlibrary.org/b/id/"
        "14849956-M.jpg"
    )

    assert book.isbn is None
    assert book.pages is None


def test_enrich_book_with_missing_data():
    book = Book(
        title="Example Book",
        source="open_library",
    )

    enriched = enrich_open_library_book(book, {})

    assert enriched == book


def test_enrich_book_with_isbn_10():
    book = Book(
        title="Example Book",
        source="open_library",
    )

    edition = {
        "isbn_10": ["8595086087"],
    }

    enriched = enrich_open_library_book(
        book,
        edition,
    )

    assert enriched.isbn == "8595086087"


def test_enrich_book_with_invalid_pages_and_cover():
    book = Book(
        title="Example Book",
        source="open_library",
    )

    edition = {
        "number_of_pages": -10,
        "covers": [-1, 0],
    }

    enriched = enrich_open_library_book(
        book,
        edition,
    )

    assert enriched.pages is None
    assert enriched.cover_url is None


def test_enrich_book_with_string_description():
    book = Book(
        title="Example Book",
        source="open_library",
    )

    edition = {
        "description": "Example synopsis."
    }

    enriched = enrich_open_library_book(
        book,
        edition,
    )

    assert enriched.synopsis == "Example synopsis."


@patch("lumera.services.open_library.time.sleep")
@patch("lumera.services.open_library.requests.get")
def test_get_open_library_edition(mock_get, mock_sleep):
    mock_get.return_value.json.return_value = {
        "number_of_pages": 320,
    }

    headers = {
        "User-Agent": "Lumera Test"
    }

    result = get_open_library_edition(
        "/books/OL123M",
        headers,
    )

    assert result == {"number_of_pages": 320}

    mock_get.assert_called_once_with(
        "https://openlibrary.org/books/OL123M.json",
        headers=headers,
        timeout=15,
    )

    mock_sleep.assert_called_once_with(1)


@patch("lumera.services.open_library.requests.get")
def test_get_edition_with_invalid_key(mock_get):
    result = get_open_library_edition(
        "/invalid/key",
        {},
    )

    assert result == {}

    mock_get.assert_not_called()


@patch("lumera.services.open_library.time.sleep")
@patch("lumera.services.open_library.requests.get")
def test_get_edition_connection_error(mock_get, mock_sleep):
    mock_get.side_effect = requests.Timeout()

    result = get_open_library_edition(
        "/books/OL123M",
        {},
    )

    assert result == {}



@patch("lumera.services.open_library.get_open_library_edition")
@patch("lumera.services.open_library.requests.get")
def test_search_open_library(mock_get, mock_edition):
    mock_get.return_value.json.return_value = {
        "docs": [
            {
                "author_name": ["Example Author"],
                "subject": ["Fantasy"],
                "editions": {
                    "docs": [
                        {
                            "key": "/books/OL123M",
                            "title": "English Book",
                            "language": ["eng"],
                        }
                    ]
                },
            },
            {
                "author_name": ["Example Author"],
                "subject": ["Fantasy"],
                "editions": {
                    "docs": [
                        {
                            "key": "/books/OL456M",
                            "title": "Livro Brasileiro",
                            "language": ["por"],
                        }
                    ]
                },
            },
        ]
    }

    mock_edition.return_value = {
        "number_of_pages": 300,
        "isbn_13": ["9788595086081"],
    }

    books = search_open_library(
        query="subject:fantasy",
        language="pt-BR",
        max_results=5,
    )

    assert len(books) == 1
    assert books[0].title == "Livro Brasileiro"
    assert books[0].language == "pt"
    assert books[0].pages == 300
    assert books[0].isbn == "9788595086081"

    params = mock_get.call_args.kwargs["params"]

    assert params["q"] == (
        "(subject:fantasy) AND language:por"
    )

    assert params["lang"] == "pt"

    mock_edition.assert_called_once()


@patch("lumera.services.open_library.requests.get")
def test_search_respects_max_results(mock_get):
    mock_get.return_value.json.return_value = {
        "docs": [
            {
                "editions": {
                    "docs": [
                        {
                            "title": f"Livro {index}",
                            "language": ["por"],
                        }
                    ]
                }
            }
            for index in range(10)
        ]
    }

    books = search_open_library(
        query="fantasia",
        max_results=3,
    )

    assert len(books) == 3


@patch("lumera.services.open_library.requests.get")
def test_search_without_results(mock_get):
    mock_get.return_value.json.return_value = {
        "docs": []
    }

    assert search_open_library("fantasia") == []


def test_search_empty_query():
    with pytest.raises(
        ValueError,
        match="Search query cannot be empty",
    ):
        search_open_library("   ")


@pytest.mark.parametrize("max_results", [0, 41])
def test_search_invalid_max_results(max_results):
    with pytest.raises(
        ValueError,
        match="max_results must be between 1 and 40",
    ):
        search_open_library(
            query="fantasia",
            max_results=max_results,
        )


@patch("lumera.services.open_library.requests.get")
def test_search_connection_error(mock_get):
    mock_get.side_effect = requests.Timeout()

    with pytest.raises(
        RuntimeError,
        match="Failed to connect to Open Library API",
    ):
        search_open_library("fantasia")