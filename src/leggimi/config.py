import os
from typing import Literal

from dotenv import load_dotenv
from leggimi.errors import LLMNonDisponibileError

load_dotenv()


def get_openrouter_key() -> str:
    """
    Recupera la chiave API di OpenRouter dalle variabili d'ambiente.

    Returns:
        str: La chiave API di OpenRouter.

    Raises:
        LLMNonDisponibileError: Se la chiave API non è presente
            nelle variabili d'ambiente.
    """

    key = os.environ.get("OPENROUTER_API_KEY")

    if not key:
        raise LLMNonDisponibileError(
            "Chiave API OpenRouter non trovata nelle variabili d'ambiente."
        )

    return key


def get_model(type: Literal["TEXT", "IMAGE"]) -> str:
    """
    Recupera l'identificativo del modello configurato in base al tipo.

    Args:
        type: Tipo di modello da recuperare, testuale o per immagini.

    Returns:
        str: L'identificativo del modello configurato.

    Raises:
        ModuleNotFoundError: Se l'identificativo del modello non è presente
            nelle variabili d'ambiente.
    """

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
