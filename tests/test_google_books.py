from unittest.mock import patch
import pytest
import requests

from lumera.services.google_books import (
    normalize_language,
    parse_google_book,
    search_google_books,
)


@pytest.mark.parametrize(
    "language, expected",
    [
        ("pt-BR", "pt"),
        ("pt_BR", "pt"),
        ("pt", "pt"),
        ("EN", "en"),
        ("en-US", "en"),
        (None, None),
    ],
)
def test_normalize_language(language, expected):
    assert normalize_language(language) == expected


def test_parse_google_book():
    item = {
        "volumeInfo": {
            "title": "Example Fantasy Book",
            "authors": ["Example Author"],
            "pageCount": 350,
            "categories": ["Fantasy"],
            "description": "A fantasy adventure.",
            "language": "en",
            "industryIdentifiers": [
                {
                    "type": "ISBN_13",
                    "identifier": "9780547851396",
                }
            ],
            "imageLinks": {
                "thumbnail": "https://example.com/cover.jpg"
            },
        }
    }

    book = parse_google_book(item)

    assert book is not None
    assert book.title == "Example Fantasy Book"
    assert book.authors == ["Example Author"]
    assert book.pages == 350
    assert book.language == "en"
    assert book.isbn == "9780547851396"
    assert book.source == "google_books"


def test_parse_book_with_missing_fields():
    item = {
        "volumeInfo": {
            "title": "Example Book"
        }
    }

    book = parse_google_book(item)

    assert book is not None
    assert book.authors == []
    assert book.pages is None
    assert book.isbn is None
    assert book.language is None
    assert book.series_name is None


def test_parse_book_without_title():
    item = {"volumeInfo": {}}

    assert parse_google_book(item) is None


@patch("lumera.services.google_books.requests.get")
def test_search_filters_language(mock_get, monkeypatch):
    monkeypatch.setenv(
        "GOOGLE_BOOKS_API_KEY", "fake-key"
    )

    mock_get.return_value.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "English Book",
                    "language": "en",
                }
            },
            {
                "volumeInfo": {
                    "title": "Livro Brasileiro",
                    "language": "pt-BR",
                }
            },
            {
                "volumeInfo": {
                    "title": "Livro Portugues",
                    "language": "pt",
                }
            },
            {
                "volumeInfo": {
                    "title": "Unknown Language Book"
                }
            },
        ]
    }

    books = search_google_books(
        query="fantasia",
        language="pt-BR",
        max_results=5,
    )

    assert len(books) == 2

    assert books[0].title == "Livro Brasileiro"
    assert books[1].title == "Livro Portugues"

    mock_get.assert_called_once()

    params = mock_get.call_args.kwargs["params"]

    assert params["langRestrict"] == "pt"
    assert params["maxResults"] == 40


@patch("lumera.services.google_books.requests.get")
def test_search_respects_max_results(mock_get, monkeypatch):
    monkeypatch.setenv(
        "GOOGLE_BOOKS_API_KEY", "fake-key"
    )

    mock_get.return_value.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": f"Livro {index}",
                    "language": "pt",
                }
            }
            for index in range(10)
        ]
    }

    books = search_google_books(
        query="fantasia",
        language="pt-BR",
        max_results=3,
    )

    assert len(books) == 3


def test_search_empty_query():
    with pytest.raises(
        ValueError,
        match="Search query cannot be empty",
    ):
        search_google_books(query="   ")


@pytest.mark.parametrize("max_results", [0, 41])
def test_search_invalid_max_results(max_results):
    with pytest.raises(
        ValueError,
        match="max_results must be between 1 and 40",
    ):
        search_google_books(
            query="fantasia",
            max_results=max_results,
        )


def test_search_missing_api_key(monkeypatch):
    monkeypatch.delenv(
        "GOOGLE_BOOKS_API_KEY",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="GOOGLE_BOOKS_API_KEY is not configured",
    ):
        search_google_books(query="fantasia")


@patch("lumera.services.google_books.requests.get")
def test_search_connection_error(mock_get, monkeypatch):
    monkeypatch.setenv(
        "GOOGLE_BOOKS_API_KEY", "fake-key"
    )

    mock_get.side_effect = requests.Timeout()

    with pytest.raises(
        RuntimeError,
        match="Failed to connect to Google Books API",
    ):
        search_google_books(query="fantasia")