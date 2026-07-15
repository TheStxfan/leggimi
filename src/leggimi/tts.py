def synthesize(script: Script, voices: dict) -> Path:
    """
    Sintetizza l'audio a partire dallo script e dalle voci.

    Args:
        script: lo script da sintetizzare.
        voices: un dizionario che mappa i personaggi alle voci.

    Returns:
        Path: il percorso al file audio sintetizzato.

    Raises:
        ScriptNotFoundError: se lo script non è stato trovato.
        VoiceNotFoundError: se una voce non è stata trovata.
        NotImplementedError: implementazione non ancora disponibile.
    """
    raise NotImplementedError
