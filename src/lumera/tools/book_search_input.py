from pydantic import BaseModel, Field

class BookSearchInput(BaseModel):
    """Define os parametros de pesquisa das ferramentas."""

    query: str = Field(
        min_length=1,
        description=(
            "Consulta de pesquisa contendo generos, "
            "temas, titulos ou autores."
        ),
    )

    language: str = Field(
        default="pt-BR",
        description=(
            "Codigo do idioma desejado, como "
            "pt-BR, en, es ou fr."
        ),
    )

    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description=(
            "Quantidade maxima de livros retornados "
            "pela ferramenta."
        ),
    )    