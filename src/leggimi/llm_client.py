def complete(
    prompt: str, model: str = "gpt-4o-mini", system_prompt: str | None = None
) -> str:
    """
    Completa il prompt utilizzando un modello di linguaggio.

    Args:
        prompt: il prompt da completare.
        ...: altri argomenti opzionali per la configurazione del modello.

    Returns:
        La stringa completata dal modello.

    Raises:
        ModelNotFoundError: se il modello non è stato trovato.
        NoInternetConnectionError: se non c'è connessione a internet.
        ApiRequestLimitExceededError: se il limite di richieste all'API è stato superato.
        NotImplementedError: implementazione non ancora disponibile.
    """
    raise NotImplementedError
