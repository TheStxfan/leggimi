import os
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from leggimi.errors import LLMNonDisponibileError


def _get_base_dir() -> Path:
    """Restituisce la directory base dove cercare il file .env."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent.parent


def _load_env() -> None:
    """Carica il file .env dalla directory appropriata."""
    base_dir = _get_base_dir()
    env_path = base_dir / ".env"

    if env_path.exists():
        load_dotenv(env_path)
        return

    cwd_path = Path.cwd() / ".env"
    if cwd_path.exists():
        load_dotenv(cwd_path)
        return


_load_env()


def get_openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise LLMNonDisponibileError(
            "Chiave API OpenRouter non trovata nelle variabili d'ambiente."
        )
    return key


def get_model(type: Literal["TEXT", "IMAGE"]) -> str:
    model = os.environ.get("TEXT_MODEL" if type == "TEXT" else "IMAGE_MODEL")
    if not model:
        print(f"[DEBUG] Modello {type} non trovato nelle variabili d'ambiente.")
        raise ModuleNotFoundError("Modello non trovato nelle variabili d'ambiente.")
    return model
