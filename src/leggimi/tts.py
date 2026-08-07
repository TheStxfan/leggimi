from pathlib import Path

import edge_tts

from leggimi.models.models import Script


async def _sintetizza_testo(
    text: str,
    voice: str,
    output_audio: Path,
    output_srt: Path,
) -> None:
    """
    Genera audio e sottotitoli da un testo.
    """

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="-10%",
        volume="+0%",
        pitch="+0Hz",
    )

    submaker = edge_tts.SubMaker()

    with open(output_audio, "wb") as audio_file:

        async for chunk in communicate.stream():

            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])  # type: ignore

            elif chunk["type"] == "SentenceBoundary":
                submaker.feed(chunk)

    output_srt.write_text(
        submaker.get_srt(),
        encoding="utf-8",
    )


async def synthesize_script(
    script: Script,
    output_mp3: str,
    output_srt: str,
) -> None:
    """
    Genera mp3 e sottotitoli da uno Script.
    """

    mp3_path = Path(output_mp3)
    srt_path = Path(output_srt)

    if script.mode != "riassunto":
        raise NotImplementedError("Il dialogo non è ancora implementato.")

    text = script.plain_text

    await _sintetizza_testo(
        text=text,
        voice="it-IT-ElsaNeural",
        output_audio=mp3_path,
        output_srt=srt_path,
    )
