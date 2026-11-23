from typing import Literal

from pydantic import BaseModel, Field, model_validator

class ReadingProfile(BaseModel):
    """Representa as preferencias de leitura do usuario."""

    genres: list[str] = Field(
        default_factory=list,
        description="Generos literarios desejados pelo usuario."
    )

    themes: list[str] = Field(
        default_factory=list,
        description="Temas e caracteristicas de interesse."
    )

    min_pages: int | None = Field(
        default=None,
        ge=1,
        description="Quantidade minima de paginas."
    )

    max_pages: int | None = Field(
        default=None,
        ge=1,
        description="Quantidade maxima de paginas."
    )

    series_preference: list[
        Literal["standalone", "series"]
    ] = Field(
        default_factory=list,
        description="Preferencia por livro unico ou serie."
    )

    language: str = Field(
        default="pt-BR",
        description="Idioma preferido para leitura."
    )

    @model_validator(mode="after")
    def validate_page_range(self):
        if (
            self.min_pages is not None
            and self.max_pages is not None
            and self.min_pages > self.max_pages
        ):
            raise ValueError(
                "min_pages cannot be greater than max_pages"
            )

        return self