import json
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel

from lumera.services.google_books import search_google_books
from lumera.tools.book_search_input import BookSearchInput


class GoogleBooksTool(BaseTool):
    """Ferramenta de pesquisa na Google Books."""

    name: str = "google_books_search"

    description: str = (
        "Pesquisa livros reais no catalogo Google Books. "
        "Utilize para encontrar livros por genero, tema, "
        "titulo ou autor. "
        "Retorna dados bibliograficos como titulo, autores, "
        "paginas, ISBN, idioma e sinopse, quando disponiveis."
    )

    args_schema: Type[BaseModel] = BookSearchInput

    def _run(
            self,
            query: str,
            language: str = "pt-BR",
            max_results: int = 5,
    ) -> str:
        """Executa a pesquisa no Google Books."""

        try:
            books = search_google_books(
                query=query,
                language=language,
                max_results=max_results,
            )

        except (ValueError, RuntimeError) as error:
            return json.dumps(
                {
                    "source": "google_books",
                    "status": "error",
                    "error": str(error),
                    "books": [],
                },
                ensure_ascii=False,
            )

        return json.dumps(
            {
                "source": "google_books",
                "status": "success",
                "total": len(books),
                "books": [
                    book.model_dump(mode="json")
                    for book in books
                ],
            },
            ensure_ascii=False,
        )