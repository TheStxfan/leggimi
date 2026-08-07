from pathlib import Path
import subprocess
import shutil

import edge_tts

from leggimi.errors import VoiceNotFoundError
from leggimi.models.models import Script

TEMP_DIR = Path("./temp")
OUTPUT_DIR = Path("./output")


VOICES = {
    "Speaker1": "it-IT-ElsaNeural",
    "Speaker2": "it-IT-DiegoNeural",
}


def _ensure_directories() -> None:
    TEMP_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def _timestamp_to_seconds(timestamp: str) -> float:
    """
    Converte timestamp SRT in secondi.
    """

    hours, minutes, seconds = timestamp.replace(",", ".").split(":")

    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _seconds_to_timestamp(seconds: float) -> str:
    """
    Converte secondi in timestamp SRT.
    """

    milliseconds = int((seconds % 1) * 1000)

    total_seconds = int(seconds)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    return f"{hours:02d}:" f"{minutes:02d}:" f"{secs:02d}," f"{milliseconds:03d}"


def _shift_srt(
    srt_content: str,
    offset: float,
) -> str:
    """
    Applica un offset temporale a un file SRT.
    """

    lines = srt_content.splitlines()

    result = []

    for line in lines:

        if "-->" in line:

            start, end = line.split(" --> ")

            start_time = _timestamp_to_seconds(start)
            end_time = _timestamp_to_seconds(end)

            result.append(
                f"{_seconds_to_timestamp(start_time + offset)} --> "
                f"{_seconds_to_timestamp(end_time + offset)}"
            )

        else:
            result.append(line)

    return "\n".join(result)


def _get_audio_duration(path: Path) -> float:
    """
    Recupera la durata di un mp3 tramite ffprobe.
    """

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


async def _sintetizza_segmento(
    text: str,
    voice: str,
    output_audio: Path,
    output_srt: Path,
) -> None:
    """
    Genera un segmento audio con relativo SRT.
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


async def _sintetizza_dialogo(
    script: Script,
    output_mp3: Path,
    output_srt: Path,
) -> None:
    """
    Genera un dialogo con più voci.
    """

    temp_files: list[Path] = []

    srt_parts: list[str] = []

    offset = 0.0

    for index, line in enumerate(script.lines):

        if line.speaker not in VOICES:
            raise VoiceNotFoundError(f"Voce non trovata: {line.speaker}")

        audio_path = TEMP_DIR / f"segment_{index:03d}.mp3"
        srt_path = TEMP_DIR / f"segment_{index:03d}.srt"

        await _sintetizza_segmento(
            text=line.text,
            voice=VOICES[line.speaker],
            output_audio=audio_path,
            output_srt=srt_path,
        )

        temp_files.append(audio_path)

        duration = _get_audio_duration(audio_path)

        srt_parts.append(
            _shift_srt(
                srt_path.read_text(
                    encoding="utf-8",
                ),
                offset,
            )
        )

        offset += duration

    concat_file = TEMP_DIR / "concat.txt"

    concat_file.write_text(
        "\n".join(f"file '{file.resolve()}'" for file in temp_files),
        encoding="utf-8",
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(output_mp3),
        ],
        check=True,
    )

    output_srt.write_text(
        "\n\n".join(srt_parts),
        encoding="utf-8",
    )


async def synthesize_script(
    script: Script,
    output_name: str,
) -> None:
    """
    Genera mp3 e srt da uno Script.
    """

    _ensure_directories()

    output_mp3 = OUTPUT_DIR / f"{output_name}.mp3"
    output_srt = OUTPUT_DIR / f"{output_name}.srt"

    try:
        if script.mode == "riassunto":

            await _sintetizza_segmento(
                text=script.plain_text,
                voice="it-IT-ElsaNeural",
                output_audio=output_mp3,
                output_srt=output_srt,
            )

        elif script.mode == "dialogo":

            await _sintetizza_dialogo(
                script,
                output_mp3,
                output_srt,
            )

        else:
            raise ValueError(f"Modalità non supportata: {script.mode}")

    finally:
        _clean_temp()


def _clean_temp() -> None:
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
