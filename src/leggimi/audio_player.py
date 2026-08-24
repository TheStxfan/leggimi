from pathlib import Path
import re

import miniaudio

from leggimi.errors import (
    AudioFileNotFoundError,
    AudioPlaybackError,
    AudioSeekError,
    SrtFileNotFoundError,
)


class AudioPlayer:
    def __init__(
        self,
        audio_path: Path,
        srt_path: Path,
    ):
        self.audio_path = audio_path
        self.srt_path = srt_path
        self.device = None
        self.stream = None

        if not audio_path.exists():
            raise AudioFileNotFoundError(f"File audio non trovato: {audio_path}")

        try:
            self.info = miniaudio.get_file_info(str(audio_path))
        except Exception as exc:
            raise AudioFileNotFoundError(
                f"Impossibile leggere il file audio: {audio_path}"
            ) from exc

        self.position = 0
        self.current_line = 0
        self.playing = False
        self.lines = self.load_srt()

    def load_srt(self) -> list[float]:
        """
        Carica i timestamp di inizio delle linee SRT.

        Returns:
            Lista dei timestamp di inizio espressi in secondi.

        Raises:
            SrtFileNotFoundError: Se il file SRT non esiste.
            AudioSeekError: Se il file SRT non può essere letto.
        """

        if not self.srt_path.exists():
            raise SrtFileNotFoundError(f"File SRT non trovato: {self.srt_path}")

        try:
            content = self.srt_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise AudioSeekError(
                f"Impossibile leggere il file SRT: {self.srt_path}"
            ) from exc

        pattern = re.compile(
            r"(\d+)\s*\n"
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*"
            r"(\d{2}:\d{2}:\d{2},\d{3})"
        )

        lines = []

        for match in pattern.finditer(content):
            start_timestamp = match.group(2)
            start_seconds = self.timestamp_to_seconds(start_timestamp)
            lines.append(start_seconds)

        return lines

    @staticmethod
    def timestamp_to_seconds(timestamp: str) -> float:
        """
        Converte HH:MM:SS,mmm in secondi.
        """

        try:
            hours, minutes, seconds = timestamp.split(":")
            seconds, milliseconds = seconds.split(",")

            return (
                int(hours) * 3600
                + int(minutes) * 60
                + int(seconds)
                + int(milliseconds) / 1000
            )
        except (ValueError, TypeError) as exc:
            raise AudioSeekError(f"Timestamp SRT non valido: {timestamp}") from exc

    def create_stream(self) -> None:
        """
        Crea lo stream audio a partire dalla posizione corrente.

        Raises:
            AudioPlaybackError: Se lo stream non può essere creato.
        """

        try:
            self.stream = miniaudio.stream_file(
                str(self.audio_path),
                output_format=miniaudio.SampleFormat.SIGNED16,
                nchannels=self.info.nchannels,
                sample_rate=self.info.sample_rate,
                frames_to_read=1024,
                seek_frame=self.position,
            )
        except Exception as exc:
            raise AudioPlaybackError("Impossibile creare lo stream audio.") from exc

    def create_device(self) -> None:
        """
        Crea il dispositivo audio predefinito del sistema operativo.

        Raises:
            AudioPlaybackError: Se il dispositivo non può essere creato.
        """

        try:
            self.device = miniaudio.PlaybackDevice(
                output_format=miniaudio.SampleFormat.SIGNED16,
                nchannels=self.info.nchannels,
                sample_rate=self.info.sample_rate,
            )
        except Exception as exc:
            raise AudioPlaybackError(
                "Impossibile inizializzare il dispositivo audio."
            ) from exc

    def play(self) -> None:
        """
        Avvia la riproduzione dalla posizione corrente.

        Raises:
            AudioPlaybackError: Se il playback non può essere avviato.
        """

        if self.playing:
            return

        try:
            if self.stream is None:
                self.create_stream()

            if self.device is None:
                self.create_device()

            self.device.start(self.stream)  # type: ignore
            self.playing = True

        except AudioPlaybackError:
            self.cleanup()
            raise

        except Exception as exc:
            self.cleanup()
            raise AudioPlaybackError(
                "Impossibile avviare la riproduzione audio."
            ) from exc

    def stop(self) -> None:
        """
        Arresta completamente la riproduzione e libera le risorse.

        Raises:
            AudioPlaybackError: Se il dispositivo non può essere arrestato.
        """

        if self.device is None:
            self.playing = False
            return

        try:
            self.device.stop()
        except Exception as exc:
            self.cleanup()
            raise AudioPlaybackError(
                "Impossibile arrestare la riproduzione audio."
            ) from exc
        finally:
            self.cleanup()

    def seek_to_line(self, line_index: int) -> None:
        """
        Sposta il playback all'inizio di una linea SRT.

        Raises:
            AudioSeekError: Se non è possibile effettuare il seek.
        """

        if not self.lines:
            raise AudioSeekError("Nessuna linea SRT disponibile.")

        line_index = max(0, min(line_index, len(self.lines) - 1))

        target_seconds = self.lines[line_index]
        target_frame = int(target_seconds * self.info.sample_rate)

        was_playing = self.playing

        try:
            self.cleanup()

            self.position = target_frame
            self.current_line = line_index

            if was_playing:
                self.play()

        except AudioSeekError:
            raise

        except AudioPlaybackError as exc:
            raise AudioSeekError("Impossibile spostare la riproduzione.") from exc

        except Exception as exc:
            raise AudioSeekError("Impossibile spostare la riproduzione.") from exc

    def next_line(self) -> None:
        """
        Vai alla linea SRT successiva.
        """

        next_index = self.current_line + 1

        if next_index >= len(self.lines):
            return

        self.seek_to_line(next_index)

    def previous_line(self) -> None:
        """
        Torna alla linea SRT precedente.
        """

        previous_index = self.current_line - 1

        if previous_index < 0:
            return

        self.seek_to_line(previous_index)

    def restart(self) -> None:
        """
        Riavvia l'audio dall'inizio.

        Raises:
            AudioSeekError: Se il riavvio non riesce.
        """

        was_playing = self.playing

        try:
            self.cleanup()
            self.position = 0
            self.current_line = 0

            if was_playing:
                self.play()

        except AudioPlaybackError as exc:
            raise AudioSeekError("Impossibile riavviare la riproduzione.") from exc

        except Exception as exc:
            raise AudioSeekError("Impossibile riavviare la riproduzione.") from exc

    def cleanup(self) -> None:
        """
        Chiude device e stream audio.

        Gli errori di cleanup vengono ignorati intenzionalmente,
        poiché questa funzione viene utilizzata anche durante
        la gestione di altri errori e alla chiusura dell'applicazione.
        """

        if self.device is not None:
            try:
                self.device.stop()
            except Exception:
                pass

            try:
                self.device.close()
            except Exception:
                pass

        if self.stream is not None:
            try:
                self.stream.close()
            except Exception:
                pass

        self.device = None
        self.stream = None
        self.playing = False
