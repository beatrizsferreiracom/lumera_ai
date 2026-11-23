from pydantic import BaseModel, Field

class Book(BaseModel):
    """Representa um livro recuperado de fontes externas."""

    title: str = Field(
        min_length=1,
        description="Titulo do livro."
    )

    authors: list[str] = Field(
        default_factory=list,
        description="Autores do livro."
    )

    isbn: str | None = Field(
        default=None,
        description="Identificador ISBN da edicao."
    )

    pages: int | None = Field(
        default=None,
        ge=1,
        description="Quantidade de paginas."
    )

    genres: list[str] = Field(
        default_factory=list,
        description="Generos literarios do livro."
    )

    synopsis: str | None = Field(
        default=None,
        description="Sinopse do livro."
    )

    language: str | None = Field(
        default=None,
        description="Idioma da edicao."
    )

    series_name: str | None = Field(
        default=None,
        description="Nome da serie, quando aplicavel."
    )

    series_position: int | None = Field(
        default=None,
        ge=1,
        description="Posicao do livro na serie."
    )

    cover_url: str | None = Field(
        default=None,
        description="URL da imagem da capa."
    )

    source: str = Field(
        min_length=1,
        description="Fonte dos dados bibliograficos."
    )