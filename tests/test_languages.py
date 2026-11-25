import pytest

from lumera.utils.languages import to_open_library_language


@pytest.mark.parametrize(
    "language, expected",
    [
        ("pt-BR", "por"),
        ("pt", "por"),
        ("en", "eng"),
        ("es", "spa"),
        ("fr", "fre"),
        ("de", "ger"),
        ("it", "ita"),
        ("ja", "jpn"),
    ],
)
def test_to_open_library_language(language, expected):
    assert to_open_library_language(language) == expected


def test_unsupported_language():
    with pytest.raises(
        ValueError,
        match="Unsupported Open Library language",
    ):
        to_open_library_language("xx")