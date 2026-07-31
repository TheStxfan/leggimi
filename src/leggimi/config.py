import os
from typing import Literal

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


def get_model(type: Literal["TEXT", "IMAGE"]) -> str:
    if type == "IMAGE":
        model = os.environ.get("MODEL")
    elif type == "TEXT":
        model = ""

    model = (
        os.environ.get("TEXT_MODEL")
        if type == "TEXT"
        else os.environ.get("IMAGE_MODEL")
    )

    if not model:
        raise ModuleNotFoundError("Modello non trovato nelle variabili d'ambiente.")

    return model
