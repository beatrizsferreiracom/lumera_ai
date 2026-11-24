from crewai import Agent
from lumera.llm import get_llm


def create_reading_profile_agent() -> Agent:
    """Cria o agente responsavel por interpretar preferencias."""

    return Agent(
        role= "Reading Profile Specialist",
        goal=(
            "Interpretar as preferencias literarias do usuario "
            "e transforma-las em dados estruturados."
        ),
        backstory=(
            "Voce e um especialista em literatura e analise "
            "de preferencias de leitura. Sua responsabilidade "
            "e identificar generos, temas, quantidade de paginas, "
            "preferencia por series e idioma. "
            "Nunca invente preferencias nao informadas."
        ),
        llm=get_llm(),
        verbose=False,
        allow_delegation=False,
    )