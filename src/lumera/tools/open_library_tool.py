import json
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel

from lumera.services.open_library import search_open_library
from lumera.tools.book_search_input import BookSearchInput


class OpenLibraryTool(BaseTool):
    """Ferramenta de pesquisa na Open Library."""

    name: str = "open_library_search"

    description: str = (
        "Pesquisa livros reais no catalogo Open Library. "
        "Utilize para encontrar obras e edicoes por genero, "
        "tema, titulo ou autor. "
        "Aceita consultas como subject:fantasy. "
        "Retorna dados bibliograficos e assuntos literarios, "
        "incluindo ISBN, paginas e sinopse, quando disponiveis."
    )

    args_schema: Type[BaseModel] = BookSearchInput

    def _run(
        self,
        query: str,
        language: str = "pt-BR",
        max_results: int = 5,
    ) -> str:
        """Executa a pesquisa na Open Library."""

        try:
            books = search_open_library(
                query=query,
                language=language,
                max_results=max_results,
            )

        except (ValueError, RuntimeError) as error:
            return json.dumps(
                {
                    "source": "open_library",
                    "status": "error",
                    "error": str(error),
                    "books": [],
                },
                ensure_ascii=False,
            )

        return json.dumps(
            {
                "source": "open_library",
                "status": "success",
                "total": len(books),
                "books": [
                    book.model_dump(mode="json")
                    for book in books
                ],
            },
            ensure_ascii=False,
        )