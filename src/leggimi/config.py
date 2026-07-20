import os

from dotenv import load_dotenv
from leggimi.errors import LLMNonDisponibileError

load_dotenv()


def get_openrouter_key() -> str:
    try:
        key = get_openrouter_key()
    except EnvironmentError as exc:
        raise LLMNonDisponibileError("OPENROUTER_API_KEY mancante") from exc

    return key
