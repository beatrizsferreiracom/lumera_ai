import pytest
from pydantic import ValidationError

from lumera.models import Book, ReadingProfile


def test_valid_reading_profile():
    profile = ReadingProfile(
        genres=["Fantasy", "Romance"],
        min_pages=300,
        max_pages=500,
        series_preference=["standalone"],
    )

    assert profile.min_pages == 300
    assert profile.max_pages == 500
    assert profile.language == "pt-BR"


def test_invalid_page_range():
    with pytest.raises(ValidationError):
        ReadingProfile(
            min_pages=500,
            max_pages=300,
        )


def test_invalid_series_preference():
    with pytest.raises(ValidationError):
        ReadingProfile(
            series_preference=["unknown"]
        )


def test_valid_book():
    book = Book(
        title="Example Book",
        authors=["Example Author"],
        pages=350,
        source="google_books",
    )

    assert book.title == "Example Book"
    assert book.pages == 350
    assert book.isbn is None