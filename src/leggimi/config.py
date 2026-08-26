import os
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from leggimi.errors import LLMNonDisponibileError


def _get_base_dir() -> Path:
    """Restituisce la directory base dove cercare il file .env."""
    if getattr(sys, "frozen", False):
        # Eseguibile PyInstaller: usa la cartella dell'eseguibile
        return Path(sys.executable).parent
    else:
        # Sviluppo: risali fino alla root del progetto
        return Path(__file__).parent.parent.parent


def _load_env() -> None:
    """Carica il file .env dalla directory appropriata."""
    # 1. Prova nella cartella dell'eseguibile
    base_dir = _get_base_dir()
    env_path = base_dir / ".env"

    if env_path.exists():
        load_dotenv(env_path)
        print(f"[DEBUG] .env caricato da: {env_path}")
        return

    # 2. Prova nella cartella di lavoro corrente
    cwd_path = Path.cwd() / ".env"
    if cwd_path.exists():
        load_dotenv(cwd_path)
        print(f"[DEBUG] .env caricato da: {cwd_path}")
        return

    print("[DEBUG] .env non trovato in nessuna posizione.")


# Carica il .env all'avvio del modulo
_load_env()


def get_openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        # Stampa di debug per capire se la variabile è stata caricata
        print("[DEBUG] OPENROUTER_API_KEY non trovata nelle variabili d'ambiente.")
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
