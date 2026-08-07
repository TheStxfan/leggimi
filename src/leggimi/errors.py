class LeggiMiError(Exception):
    """Base di tutti gli errori dell'app."""


class PdfIlleggibileError(LeggiMiError):
    """Il PDF non può essere aperto o non contiene testo utile."""


class LLMNonDisponibileError(LeggiMiError):
    """Provider LLM non configurato o non raggiungibile."""


class TTSNonDisponibileError(LeggiMiError):
    """Sintesi vocale non disponibile."""


class ChaptersNotFoundError(LeggiMiError):
    """Nessun capitolo trovato."""


class PdfScansionatoError(PdfIlleggibileError):
    """Scansione (immagine): serve percorso OCR/AI."""


class ModelNotFoundError(LLMNonDisponibileError):
    """404: modello non trovato."""


class NoInternetConnectionError(LLMNonDisponibileError):
    """Connessione all'API fallita."""


class ApiRequestLimitExceededError(LLMNonDisponibileError):
    """429: limite richieste superato."""


class UIInitializationError(LeggiMiError):
    """Errore durante l'inizializzazione dell'interfaccia utente."""


class FileSelectionError(LeggiMiError):
    """Errore durante la selezione di un file."""


class InvalidScriptFormatError(LeggiMiError):
    """La risposta del modello non rispetta il formato dello script."""


class VoiceNotFoundError(Exception):
    """La voce richiesta non è disponibile."""
