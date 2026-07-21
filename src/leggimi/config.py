import os

from dotenv import load_dotenv
from leggimi.errors import LLMNonDisponibileError

load_dotenv()


def get_openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")

    if not key:
        raise LLMNonDisponibileError(
            "Chiave API OpenRouter non trovata nelle variabili d'ambiente."
        )

    return key
