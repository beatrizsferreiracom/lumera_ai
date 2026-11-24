import os 
from crewai import LLM
from dotenv import load_dotenv 

load_dotenv()

def get_llm() -> LLM:
    """Cria o modelo de linguagem utilizado pelos agentes."""

    return LLM(
        model=os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini"),
        temperature=0,
        max_tokens=500,
    )