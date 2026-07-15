from .models import Page, Chapter


def split_chapters(pages: list[Page]) -> list[Chapter]:
    """
    Divide le pagine in capitoli basandosi sui titoli.

    Args:
        pages: Lista di oggetti Page.

    Returns:
        Lista di oggetti Chapter.

    Raises:
        ChaptersNotFoundError: se i capitoli non esistono.
        NotImplementedError: implementazione non ancora disponibile.
    """
    raise NotImplementedError
