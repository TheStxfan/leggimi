import hashlib
import json
from pathlib import Path

from leggimi.errors import ChapterCacheError
from leggimi.models.models import Chapter

CACHE_DIR = Path("./cache/chapters")


def _get_cache_path(pdf_path: str) -> Path:
    """
    Restituisce il percorso della cache associata al PDF.

    Args:
        pdf_path: Percorso del file PDF.

    Returns:
        Path: Percorso del file JSON di cache.
    """

    sha256 = hashlib.sha256()

    try:
        with open(pdf_path, "rb") as file:
            for chunk in iter(lambda: file.read(8192), b""):
                sha256.update(chunk)
    except OSError as exc:
        raise ChapterCacheError(
            f"Impossibile calcolare l'identificativo della cache: {pdf_path}"
        ) from exc

    return CACHE_DIR / f"{sha256.hexdigest()}.json"


def load_chapters(pdf_path: str) -> list[Chapter] | None:
    """
    Carica i capitoli dalla cache del PDF.

    Se la cache non esiste restituisce None.
    Se la cache è corrotta, viene eliminata e restituisce None.

    Args:
        pdf_path: Percorso del file PDF.

    Returns:
        list[Chapter] | None: Capitoli presenti nella cache, oppure None
        se la cache non è disponibile o non è valida.

    Raises:
        ChapterCacheError: Se si verifica un errore durante l'accesso
            alla cache.
    """

    cache_path = _get_cache_path(pdf_path)

    if not cache_path.exists():
        return None

    try:
        with open(cache_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError

        chapters = [
            Chapter(
                title=item["title"],
                text=item["text"],
            )
            for item in data
            if isinstance(item, dict)
            and isinstance(item.get("title"), str)
            and isinstance(item.get("text"), str)
        ]

        if len(chapters) != len(data):
            raise ValueError

        return chapters

    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        cache_path.unlink(missing_ok=True)
        return None

    except OSError as exc:
        raise ChapterCacheError(
            f"Impossibile leggere la cache dei capitoli: {cache_path}"
        ) from exc


def save_chapters(pdf_path: str, chapters: list[Chapter]) -> None:
    """
    Salva i capitoli estratti nella cache del PDF.

    Args:
        pdf_path: Percorso del file PDF.
        chapters: Capitoli estratti dal PDF.

    Raises:
        ChapterCacheError: Se si verifica un errore durante la scrittura
            della cache.
    """

    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        cache_path = _get_cache_path(pdf_path)

        data = [
            {
                "title": chapter.title,
                "text": chapter.text,
            }
            for chapter in chapters
        ]

        with open(cache_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    except ChapterCacheError:
        raise

    except (OSError, TypeError, ValueError) as exc:
        raise ChapterCacheError(
            f"Impossibile salvare la cache dei capitoli: {pdf_path}"
        ) from exc
