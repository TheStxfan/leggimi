import httpx
import pytest

from dataclasses import dataclass
from openai import APIConnectionError, NotFoundError, RateLimitError
from leggimi import config
from leggimi import llm_client
from leggimi import scriptgen
from leggimi.errors import (
    ApiRequestLimitExceededError,
    InvalidScriptFormatError,
    ModelNotFoundError,
    NoInternetConnectionError,
)
from leggimi.models.models import Line, Script
from leggimi.scriptgen import (
    _generate_chunk_script,
    chunk_text,
    to_script,
)


@dataclass
class FakeMessage:
    content: str


@dataclass
class FakeChoice:
    message: FakeMessage


@dataclass
class FakeResponse:
    content: str

    def __post_init__(self):
        self.choices = [
            FakeChoice(
                message=FakeMessage(
                    content=self.content,
                ),
            ),
        ]


def test_chunk_text_basic():
    """Verifica che il testo venga suddiviso correttamente in blocchi."""

    text = "parola " * 2000

    chunks = chunk_text(
        text,
        max_words=1000,
        overlap=100,
    )

    assert len(chunks) == 3
    assert len(chunks[0].split()) == 1000
    assert len(chunks[1].split()) == 1000
    assert len(chunks[2].split()) == 200


def test_to_script_riassunto_success(monkeypatch):
    """Verifica la generazione di uno script valido in modalità riassunto."""

    content = (
        "SPEAKER: Speaker1\n"
        "TEXT: Benvenuti a questa lezione sul sistema solare.\n"
        "SPEAKER: Speaker1\n"
        "TEXT: Il sole è al centro del nostro sistema."
    )

    monkeypatch.setattr(
        "leggimi.scriptgen._call_with_retry",
        lambda **kwargs: FakeResponse(content),
    )

    result = to_script(
        chapter_text="Il sistema solare è composto dal sole e dai pianeti.",
        mode="riassunto",
        livello="base",
    )

    assert isinstance(result, Script)
    assert result.mode == "riassunto"
    assert len(result.lines) == 2

    assert result.lines[0] == Line(
        speaker="Speaker1",
        text="Benvenuti a questa lezione sul sistema solare.",
    )

    assert result.lines[1] == Line(
        speaker="Speaker1",
        text="Il sole è al centro del nostro sistema.",
    )


def test_to_script_dialogo_success(monkeypatch):
    """Verifica la generazione di uno script valido in modalità dialogo."""

    content = (
        "SPEAKER: Speaker1\n"
        "TEXT: Oggi parliamo di fotosintesi.\n"
        "SPEAKER: Speaker2\n"
        "TEXT: Di cosa si tratta esattamente?"
    )

    monkeypatch.setattr(
        "leggimi.scriptgen._call_with_retry",
        lambda **kwargs: FakeResponse(content),
    )

    result = to_script(
        chapter_text="La fotosintesi clorofilliana...",
        mode="dialogo",
        livello="intermedio",
    )

    assert isinstance(result, Script)
    assert result.mode == "dialogo"
    assert len(result.lines) == 2

    assert result.lines[0].speaker == "Speaker1"
    assert result.lines[1].speaker == "Speaker2"


def test_generate_chunk_script_retry_on_bad_format(monkeypatch):
    """
    Verifica il retry interno se il modello restituisce
    prima un formato errato.
    """

    responses = [
        FakeResponse("SPEAKER: Speaker1"),
        FakeResponse("SPEAKER: Speaker1\n" "TEXT: Testo riassuntivo corretto."),
    ]

    call_count = 0

    def fake_call_with_retry(**kwargs):
        nonlocal call_count

        response = responses[call_count]
        call_count += 1

        return response

    monkeypatch.setattr(
        "leggimi.scriptgen._call_with_retry",
        fake_call_with_retry,
    )

    lines = _generate_chunk_script(
        chapter_text="Testo di prova",
        mode="riassunto",
        livello="base",
        model=config.get_model("TEXT"),
        system_prompt="Prompt",
    )

    assert len(lines) == 1
    assert lines[0].text == "Testo riassuntivo corretto."
    assert call_count == 2


def test_generate_chunk_script_invalid_speaker_for_mode(monkeypatch):
    """
    Verifica che Speaker2 non sia consentito in modalità riassunto.
    """

    invalid_content = "SPEAKER: Speaker2\n" "TEXT: Non consentito nel riassunto."

    monkeypatch.setattr(
        "leggimi.scriptgen._call_with_retry",
        lambda **kwargs: FakeResponse(invalid_content),
    )

    with pytest.raises(InvalidScriptFormatError):
        _generate_chunk_script(
            chapter_text="Testo capitolo",
            mode="riassunto",
            livello="base",
            model=config.get_model("TEXT"),
            system_prompt=None,
        )


def test_generate_chunk_script_dialogue_missing_speaker(monkeypatch):
    """
    Verifica che un dialogo contenente un solo speaker
    venga considerato non valido.
    """

    invalid_content = "SPEAKER: Speaker1\n" "TEXT: Testo del dialogo."

    monkeypatch.setattr(
        "leggimi.scriptgen._call_with_retry",
        lambda **kwargs: FakeResponse(invalid_content),
    )

    with pytest.raises(InvalidScriptFormatError):
        _generate_chunk_script(
            chapter_text="Testo capitolo",
            mode="dialogo",
            livello="base",
            model="google/gemma-4-26b-a4b-it:free",
            system_prompt=None,
        )


def test_to_script_parsing(monkeypatch):

    fake = "SPEAKER: Speaker1\n" "TEXT: Ciao a tutti"

    monkeypatch.setattr(
        "leggimi.scriptgen._call_with_retry",
        lambda *args, **kwargs: FakeResponse(fake),
    )

    script = to_script(
        "Testo del capitolo",
        mode="riassunto",
        livello="intermedio",
    )

    assert isinstance(script, Script)
    assert script.lines
    assert script.lines[0].text == "Ciao a tutti"
