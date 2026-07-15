from .models import Page


def extract_text(pdf_path: str) -> list[Page]:
    """
    Estrae il testo grezzo dal PDF, una stringa per pagina.

    Args:
        pdf_path: percorso al file PDF.

    Returns:
        Lista di stringhe, una per pagina.

    Raises:
        FileNotFoundError: se il file non esiste.
        NotImplementedError: implementazione non ancora disponibile.
    """
    raise NotImplementedError
