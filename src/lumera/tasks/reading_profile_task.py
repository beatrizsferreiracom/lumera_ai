from crewai import Agent, Task
from lumera.models import ReadingProfile


def create_reading_profile_task(agent: Agent) -> Task:
    """Cria a tarefa de extracao do perfil de leitura."""

    return Task(
        description=(
            "Analise a seguinte solicitacao do usuario:\n"
            "{user_request}\n\n"

            "Extraia as preferencias literarias seguindo "
            "rigorosamente as regras abaixo:\n"

            "1. genres: identifique os generos literarios "
            "solicitados. Se nao informados, retorne [].\n"

            "2. themes: identifique temas e caracteristicas "
            "desejadas. Se nao informados, retorne [].\n"

            "3. min_pages: identifique a quantidade minima "
            "de paginas. Se nao informada, retorne null.\n"

            "4. max_pages: identifique a quantidade maxima "
            "de paginas. Se nao informada, retorne null.\n"

            "5. series_preference: utilize 'standalone' "
            "para livros unicos e 'series' para series. "
            "Se o usuario nao informar essa preferencia, "
            "retorne obrigatoriamente [].\n"

            "6. language: utilize codigos padronizados "
            "de idioma, como 'pt-BR' para portugues brasileiro, "
            "'en' para ingles, 'es' para espanhol e "
            "'fr' para frances. "
            "Se nao informado, utilize 'pt-BR'.\n"

            "Nao invente preferencias nao informadas. "
            "Respeite os valores padrao definidos acima."
        ),
        expected_output=(
            "Um objeto ReadingProfile contendo as preferencias "
            "literarias identificadas, respeitando os formatos "
            "e valores padrao especificados."
        ),
        agent=agent,
        output_pydantic=ReadingProfile,
    )