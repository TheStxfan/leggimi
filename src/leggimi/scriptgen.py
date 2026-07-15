def to_script(
    chapter_text: str,
    mode: Literal["riassunto", "dialogo"] = "riassunto",
    livello: str = "superiori",
) -> Script:
    """
    Crea uno script a partire dal testo di un capitolo.

    Args:
        chapter_text: il testo del capitolo.
        mode: la modalità di generazione (riassunto o dialogo).
        livello: il livello di difficoltà.

    Returns:
        Script: lo script generato, list[Line].

    Raises:
        ChapterTextNotFoundError: se il testo del capitolo non è stato trovato.
        MalformedLLMOutputError: se l'output del modello non è nel formato corretto.
        NotImplementedError: implementazione non ancora disponibile.
    """
    raise NotImplementedError
