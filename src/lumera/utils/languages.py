OPEN_LIBRARY_LANGUAGE_CODES = {
    "pt": "por",
    "en": "eng",
    "es": "spa",
    "fr": "fre",
    "de": "ger",
    "it": "ita",
    "ja": "jpn",
}

def normalize_language(language: str | None) -> str | None:
    """Normaliza o codigo de idioma para comparacao."""

    if not language:
        return None

    return language.strip().replace("_", "-").split("-")[0].lower()

def to_open_library_language(language: str) -> str:
    """Converte um idioma para o formato da Open Library."""

    normalized = normalize_language(language)

    code = OPEN_LIBRARY_LANGUAGE_CODES.get(normalized)

    if code is None:
        raise ValueError("Unsupported Open Library language")

    return code