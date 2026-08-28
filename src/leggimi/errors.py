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


class VoiceNotFoundError(LeggiMiError):
    """La voce richiesta non è disponibile."""


class ChapterCacheError(LeggiMiError):
    """Errore durante la lettura o la scrittura della cache dei capitoli."""


class AudioPlayerError(LeggiMiError):
    """Errore durante la riproduzione o la gestione dell'audio."""


class AudioFileNotFoundError(AudioPlayerError):
    """Il file audio richiesto non esiste."""


class SrtFileNotFoundError(AudioPlayerError):
    """Il file SRT richiesto non esiste."""


class AudioPlaybackError(AudioPlayerError):
    """Errore durante l'avvio, la pausa o l'arresto della riproduzione."""


class AudioSeekError(AudioPlayerError):
    """Errore durante lo spostamento della posizione di riproduzione."""


class OCRModelIncompatibleError(LeggiMiError):
    """Il modello scelto non è compatibile con l'OCR delle immagini."""
