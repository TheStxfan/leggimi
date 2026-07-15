from dotenv import load_dotenv
import os

load_dotenv()


def get_openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "OPENROUTER_API_KEY non trovata. " "Aggiungi la chiave nel file .env"
        )
    return key
