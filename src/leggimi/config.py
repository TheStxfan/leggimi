import os

from dotenv import load_dotenv
from leggimi.errors import LLMNonDisponibileError, ModelNotFoundError

load_dotenv()


def get_openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")

    if not key:
        raise LLMNonDisponibileError(
            "Chiave API OpenRouter non trovata nelle variabili d'ambiente."
        )

    return key


def get_model() -> str:
    model = os.environ.get("MODEL")

    if not model:
        raise ModuleNotFoundError("Modello non trovato nelle variabili d'ambiente.")

    return model
