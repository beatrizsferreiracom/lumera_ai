from crewai import Crew, Process

from lumera.models import ReadingProfile
from lumera.agents.reading_profile_agent import(create_reading_profile_agent)
from lumera.tasks.reading_profile_task import(create_reading_profile_task)


def create_reading_profile_crew() -> Crew:
    """Cria a equipe responsavel pelo perfil do leitor."""

    agent = create_reading_profile_agent()
    task = create_reading_profile_task(agent)

    return Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )

def extract_reading_profile(user_request: str) -> ReadingProfile:
    """Extrai o perfil de leitura a partir de uma solicitacao."""

    if not user_request.strip():
        raise ValueError("User request cannot be empty")

    crew = create_reading_profile_crew()

    result = crew.kickoff(
        inputs={"user_request": user_request}
    )

    profile = result.pydantic

    if not isinstance(profile, ReadingProfile):
        raise ValueError(
            "The agent did not return a valid reading profile"
        )

    print("\nConsumo de tokens:")
    print(result.token_usage)

    return profile