import json
from unittest.mock import patch
import pytest
from pydantic import ValidationError

from lumera.models import Book
from lumera.tools import GoogleBooksTool, OpenLibraryTool
from lumera.tools.book_search_input import BookSearchInput


TOOL_CASES = [
    (
        GoogleBooksTool,
        "lumera.tools.google_books_tool.search_google_books",
        "google_books",
    ),
    (
        OpenLibraryTool,
        "lumera.tools.open_library_tool.search_open_library",
        "open_library",
    ),
]


def test_valid_book_search_input():
    search_input = BookSearchInput(
        query="subject:fantasy",
        language="en",
        max_results=3,
    )

    assert search_input.query == "subject:fantasy"
    assert search_input.language == "en"
    assert search_input.max_results == 3


def test_book_search_input_defaults():
    search_input = BookSearchInput(
        query="fantasia",
    )

    assert search_input.language == "pt-BR"
    assert search_input.max_results == 5


def test_book_search_input_empty_query():
    with pytest.raises(ValidationError):
        BookSearchInput(query="")


@pytest.mark.parametrize("max_results", [0, 11])
def test_book_search_input_invalid_max_results(max_results):
    with pytest.raises(ValidationError):
        BookSearchInput(
            query="fantasia",
            max_results=max_results,
        )


@pytest.mark.parametrize(
    "tool_class, service_path, source",
    TOOL_CASES,
)
def test_tool_success(tool_class, service_path, source):
    book = Book(
        title="O Hobbit",
        authors=["J.R.R. Tolkien"],
        pages=320,
        language="pt",
        isbn="9788595086081",
        source=source,
    )

    with patch(service_path) as mock_search:
        mock_search.return_value = [book]

        tool = tool_class()

        result = tool.run(
            query="subject:fantasy",
            language="pt-BR",
            max_results=3,
        )

        data = json.loads(result)

        assert data["status"] == "success"
        assert data["source"] == source
        assert data["total"] == 1
        assert len(data["books"]) == 1

        assert data["books"][0] == book.model_dump(
            mode="json"
        )

        mock_search.assert_called_once_with(
            query="subject:fantasy",
            language="pt-BR",
            max_results=3,
        )


@pytest.mark.parametrize(
    "tool_class, service_path, source",
    TOOL_CASES,
)
def test_tool_without_results(
    tool_class,
    service_path,
    source,
):
    with patch(service_path) as mock_search:
        mock_search.return_value = []

        tool = tool_class()

        result = tool.run(
            query="example query",
        )

        data = json.loads(result)

        assert data["status"] == "success"
        assert data["source"] == source
        assert data["total"] == 0
        assert data["books"] == []

        mock_search.assert_called_once_with(
            query="example query",
            language="pt-BR",
            max_results=5,
        )


@pytest.mark.parametrize(
    "tool_class, service_path, source",
    TOOL_CASES,
)
@pytest.mark.parametrize(
    "error_type, error_message",
    [
        (
            RuntimeError,
            "Failed to connect to API",
        ),
        (
            ValueError,
            "Invalid search parameters",
        ),
    ],
)
def test_tool_service_error(
    tool_class,
    service_path,
    source,
    error_type,
    error_message,
):
    with patch(service_path) as mock_search:
        mock_search.side_effect = error_type(
            error_message
        )

        tool = tool_class()

        result = tool.run(
            query="fantasia",
        )

        data = json.loads(result)

        assert data["status"] == "error"
        assert data["source"] == source
        assert data["error"] == error_message
        assert data["books"] == []


@pytest.mark.parametrize(
    "tool_class, expected_name",
    [
        (GoogleBooksTool, "google_books_search"),
        (OpenLibraryTool, "open_library_search"),
    ],
)
def test_tool_configuration(
    tool_class,
    expected_name,
):
    tool = tool_class()

    assert tool.name == expected_name
    assert tool.description.strip()
    assert tool.args_schema is BookSearchInput