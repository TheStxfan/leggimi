from dataclasses import dataclass
import asyncio
from pathlib import Path
from typing import Literal, cast

import flet as ft

from leggimi.audio_player import AudioPlayer
from leggimi.errors import AudioPlaybackError, FileSelectionError, LeggiMiError
from leggimi.models.models import Chapter
from leggimi.pipeline import (
    generate_chapter_audio,
    process_pdf,
)
from leggimi.ui.ui_components import (
    create_back_button,
    create_button,
    create_chapters_dropdown,
    create_error_popup,
    create_playback_button,
    create_next_line_button,
    create_previous_line_button,
    create_restart_button,
    create_text,
    update_playback_button_tooltip,
)
from leggimi.ui.playback_lines import PlaybackLines
from leggimi.ui.ui_config import UI_SIZE
from leggimi.ui.ui_theme import theme_config


@dataclass
class AppState:
    """
    Gestisce lo stato dell'applicazione e le operazioni principali
    dell'interfaccia grafica.
    """

    page: ft.Page
    file_picker: ft.FilePicker
    main_content: ft.Container
    app_stack: ft.Stack
    bottom_bar: ft.Container
    ui_size_row: ft.Row

    mode_dropdown: ft.Dropdown | None = None
    level_dropdown: ft.Dropdown | None = None
    chapter_dropdown: ft.Dropdown | None = None

    playback_content: ft.Container | None = None
    playback_lines: PlaybackLines | None = None
    audio_player: AudioPlayer | None = None
    playback_button: ft.IconButton | None = None
    previous_line_button: ft.IconButton | None = None
    next_line_button: ft.IconButton | None = None
    restart_audio_button: ft.IconButton | None = None

    pdf_path: str | None = None

    selected_file_text: ft.Text | None = None
    processing_text: ft.Text | None = None
    start_button: ft.Button | None = None
    chapters_view: ft.Container | None = None
    chapters: list[Chapter] | None = None

    generate_button: ft.Button | None = None
    audio_processing_text: ft.Text | None = None
    error_popup: ft.Container | None = None
    audio_ready_button: ft.Button | None = None

    text_generation_id: int = 0
    position_update_task: asyncio.Task | None = None
    playback_time: float = 0.0

    def _get_audio_paths(self) -> tuple[Path, Path] | None:
        """
        Restituisce i percorsi MP3 e SRT relativi alla selezione corrente.

        Returns:
            Una tupla contenente il percorso MP3 e SRT, oppure None se
            la selezione corrente non è valida.
        """

        if (
            self.pdf_path is None
            or self.chapter_dropdown is None
            or self.chapter_dropdown.value is None
            or self.chapters is None
            or self.mode_dropdown is None
            or self.mode_dropdown.value is None
            or self.level_dropdown is None
            or self.level_dropdown.value is None
        ):
            return None

        chapter_index = int(self.chapter_dropdown.value)

        if not 0 <= chapter_index < len(self.chapters):
            return None

        chapter = self.chapters[chapter_index]

        mode = cast(
            Literal["riassunto", "dialogo"],
            self.mode_dropdown.value,
        )

        level = cast(
            Literal["base", "intermedio", "avanzato"],
            self.level_dropdown.value,
        )

        output_name = (
            f"{Path(self.pdf_path).stem}_" f"{chapter.title}_" f"{mode}_" f"{level}"
        ).replace(" ", "_")

        output_dir = Path("./output")

        return (
            output_dir / f"{output_name}.mp3",
            output_dir / f"{output_name}.srt",
        )

    def _stop_position_updates(self) -> None:
        """
        Ferma il task di aggiornamento della posizione audio.
        """
        if self.position_update_task and not self.position_update_task.done():
            self.position_update_task.cancel()
            self.position_update_task = None

    def _start_position_updates(self) -> None:
        """
        Avvia il task di aggiornamento della posizione audio.
        """
        self._stop_position_updates()
        self.position_update_task = asyncio.create_task(
            self._update_playback_position()
        )

    async def _update_playback_position(self) -> None:
        """
        Aggiorna periodicamente la linea corrente durante la riproduzione.
        """
        last_time = asyncio.get_event_loop().time()

        while self.audio_player and self.audio_player.playing:
            await asyncio.sleep(0.1)

            now = asyncio.get_event_loop().time()
            delta = now - last_time
            last_time = now

            self.playback_time += delta

            if self.playback_lines:
                current_line = self.playback_lines.get_line_at_timestamp(
                    self.playback_time
                )

                if current_line != self.playback_lines.current_line:
                    self.playback_lines.update_current_line(current_line)
                    await self.playback_lines.scroll_to_line(current_line)
                    self.audio_player.current_line = current_line
                    self.page.update()

    def show_playback_view(self, e) -> None:
        """
        Mostra la schermata di riproduzione audio.
        """

        audio_paths = self._get_audio_paths()

        if audio_paths is None:
            return

        output_mp3, output_srt = audio_paths

        if not output_mp3.exists() or not output_srt.exists():
            return

        try:
            if (
                self.audio_player is None
                or self.audio_player.audio_path != output_mp3
                or self.audio_player.srt_path != output_srt
            ):
                if self.audio_player is not None:
                    self.audio_player.cleanup()

                self.audio_player = AudioPlayer(
                    output_mp3,
                    output_srt,
                )

                if self.playback_button is not None:
                    self.playback_button.icon = ft.Icons.PLAY_ARROW
                    update_playback_button_tooltip(
                        self.playback_button,
                        "Riproduci audio",
                    )

                if (
                    self.playback_lines is None
                    or self.playback_lines.srt_path != output_srt
                ):
                    self.playback_lines = PlaybackLines(
                        srt_path=output_srt,
                        ui_size=UI_SIZE,
                        text_color=theme_config.primary_text_color,
                        background_color=theme_config.tooltip_bgcolor,
                    )
                    self.playback_time = 0.0

        except Exception:
            self.page.run_task(
                self._show_error,
                LeggiMiError("Errore durante il caricamento dell'audio."),
            )
            return

        # Crea i pulsanti una sola volta.
        if self.restart_audio_button is None:
            self.restart_audio_button = create_restart_button(
                self.restart_audio,
            )

        if self.previous_line_button is None:
            self.previous_line_button = create_previous_line_button(
                self.previous_audio_line,
            )

        if self.playback_button is None:
            self.playback_button = create_playback_button(
                self.toggle_audio,
            )

        if self.next_line_button is None:
            self.next_line_button = create_next_line_button(
                self.next_audio_line,
            )

        # Bottom bar del playback.
        self.bottom_bar.content = ft.Row(
            controls=[
                self.restart_audio_button,
                self.previous_line_button,
                self.playback_button,
                self.next_line_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        if self.playback_content is None:
            back_button = create_back_button(
                self.show_main_view,
            )

            self.playback_content = ft.Container(
                expand=True,
                padding=ft.Padding.only(
                    top=UI_SIZE * 0.4,
                    bottom=80,
                ),
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        (
                            self.playback_lines.container
                            if self.playback_lines
                            else ft.Container()
                        ),
                        ft.Container(
                            content=back_button,
                            left=10,
                            top=10,
                        ),
                    ],
                ),
            )

        self.main_content.visible = False
        self.playback_content.visible = True

        if self.playback_content not in self.app_stack.controls:
            self.app_stack.controls.insert(
                0,
                self.playback_content,
            )

        self.page.update()

    def toggle_audio(self, e) -> None:
        """
        Avvia o arresta la riproduzione audio.
        """

        if self.audio_player is None:
            self.page.run_task(
                self._show_error,
                LeggiMiError("Player audio non disponibile."),
            )
            return

        try:
            if self.audio_player.playing:
                self.audio_player.stop()
                self._stop_position_updates()

                if self.playback_button is not None:
                    self.playback_button.icon = ft.Icons.PLAY_ARROW
                    update_playback_button_tooltip(
                        self.playback_button,
                        "Riproduci audio",
                    )

            else:
                self.audio_player.play()
                self._start_position_updates()

                if self.playback_button is not None:
                    self.playback_button.icon = ft.Icons.PAUSE
                    update_playback_button_tooltip(
                        self.playback_button,
                        "Metti in pausa",
                    )

            self.page.update()

        except AudioPlaybackError as exc:
            self.page.run_task(
                self._show_error,
                exc,
            )

    async def restart_audio(self, e) -> None:
        """
        Riavvia l'audio dall'inizio.
        """

        if self.audio_player is None:
            self.page.run_task(
                self._show_error,
                LeggiMiError("Player audio non disponibile."),
            )
            return

        try:
            was_playing = self.audio_player.playing
            self.audio_player.restart()

            self.playback_time = 0.0

            if self.playback_lines is not None:
                self.playback_lines.update_current_line(0)
                await self.playback_lines.scroll_to_line(0)
                self.audio_player.current_line = 0

            if self.playback_button is not None:
                self.playback_button.icon = (
                    ft.Icons.PAUSE if was_playing else ft.Icons.PLAY_ARROW
                )

                update_playback_button_tooltip(
                    self.playback_button,
                    ("Metti in pausa" if was_playing else "Riproduci audio"),
                )

            if was_playing:
                self._start_position_updates()

            self.page.update()

        except Exception:
            self.page.run_task(
                self._show_error,
                LeggiMiError("Errore durante il riavvio dell'audio."),
            )

    async def previous_audio_line(self, e) -> None:
        """
        Torna alla linea SRT precedente.
        """

        if self.audio_player is None:
            self.page.run_task(
                self._show_error,
                LeggiMiError("Player audio non disponibile."),
            )
            return

        try:
            self.audio_player.previous_line()
            line_idx = self.audio_player.current_line

            if self.playback_lines is not None:
                if line_idx < len(self.playback_lines.timestamps):
                    self.playback_time = self.playback_lines.timestamps[line_idx]
                self.playback_lines.update_current_line(line_idx)
                await self.playback_lines.scroll_to_line(line_idx)

            self.page.update()

        except Exception:
            self.page.run_task(
                self._show_error,
                LeggiMiError(
                    "Errore durante il passaggio alla linea precedente.",
                ),
            )

    async def next_audio_line(self, e) -> None:
        """
        Passa alla linea SRT successiva.
        """

        if self.audio_player is None:
            self.page.run_task(
                self._show_error,
                LeggiMiError("Player audio non disponibile."),
            )
            return

        try:
            self.audio_player.next_line()
            line_idx = self.audio_player.current_line

            if self.playback_lines is not None:
                if line_idx < len(self.playback_lines.timestamps):
                    self.playback_time = self.playback_lines.timestamps[line_idx]
                self.playback_lines.update_current_line(line_idx)
                await self.playback_lines.scroll_to_line(line_idx)

            self.page.update()

        except Exception:
            self.page.run_task(
                self._show_error,
                LeggiMiError(
                    "Errore durante il passaggio alla linea successiva.",
                ),
            )

    def show_main_view(self, e) -> None:
        """
        Torna alla schermata principale dell'applicazione.

        Args:
            e: Evento generato dal clic sul pulsante indietro.
        """

        if self.audio_player is not None:
            self.audio_player.stop()
            self._stop_position_updates()

        if self.playback_button is not None:
            self.playback_button.icon = ft.Icons.PLAY_ARROW

        self.main_content.visible = True

        if self.playback_content is not None:
            self.playback_content.visible = False

        self.bottom_bar.content = self.ui_size_row

        self.page.update()

    def remove_control(
        self,
        control: ft.Control | None,
    ) -> None:
        """
        Rimuove un controllo dal contenuto principale dell'interfaccia.

        Args:
            control: Controllo Flet da rimuovere.
        """

        if (
            control is not None
            and control in self.main_content.content.controls  # type: ignore
        ):
            self.main_content.content.controls.remove(control)  # type: ignore

    def _update_audio_button(self) -> None:
        """
        Aggiorna i pulsanti audio in base alla presenza dei file MP3 e SRT
        relativi alla selezione corrente.
        """

        audio_paths = self._get_audio_paths()

        if audio_paths is None:
            return

        output_mp3, output_srt = audio_paths

        audio_ready = output_mp3.exists() and output_srt.exists()

        if self.generate_button is not None:
            self.generate_button.visible = not audio_ready

        if self.audio_ready_button is not None:
            self.audio_ready_button.visible = audio_ready

        self.page.update()

    async def _show_error(
        self,
        error: LeggiMiError,
    ) -> None:
        """
        Mostra un errore applicativo tramite un popup temporaneo.

        Args:
            error: Errore applicativo da mostrare.
        """

        error_popup = create_error_popup(error)

        self.app_stack.controls.append(error_popup)

        self.page.update()

        await asyncio.sleep(4)

        if error_popup in self.app_stack.controls:
            self.app_stack.controls.remove(error_popup)
            self.page.update()

    async def run_processes(self, e) -> None:
        """
        Elabora il file PDF selezionato ed aggiorna l'interfaccia con
        i capitoli estratti.

        Args:
            e: Evento generato dall'interazione con il controllo UI.
        """

        if self.pdf_path is None:
            return

        if self.processing_text is None:
            self.processing_text = create_text(
                "Messa in ordine del caos cartaceo...",
            )

        if self.start_button is not None:
            self.start_button.disabled = True

        self.remove_control(self.chapters_view)
        self.remove_control(self.processing_text)

        self.main_content.content.controls.append(  # type: ignore
            self.processing_text,
        )

        self.page.update()

        try:
            chapters = await asyncio.to_thread(
                process_pdf,
                self.pdf_path,
            )

            self.chapters = chapters

            self.remove_control(self.processing_text)

            self.chapters_view, self.chapter_dropdown = create_chapters_dropdown(
                chapters,
                self.page,
                on_select=lambda e: self._update_audio_button(),
            )

            if self.generate_button is None:
                self.generate_button = create_button(
                    "Genera mp3",
                    ft.Icons.SPATIAL_AUDIO_OFF,
                    self.generate_audio,
                    tooltip_text=(
                        "Genera riassunto/dialogo " "dal capitolo selezionato"
                    ),
                )

            if self.audio_ready_button is None:
                self.audio_ready_button = create_button(
                    "Audio pronto",
                    ft.Icons.HEADPHONES,
                    self.show_playback_view,
                    tooltip_text="Riproduci l'audio generato",
                )

                self.audio_ready_button.visible = False

            # Evita di inserire due volte gli stessi controlli.
            self.remove_control(self.chapters_view)
            self.remove_control(self.generate_button)
            self.remove_control(self.audio_ready_button)

            self.main_content.content.controls.append(  # type: ignore
                self.chapters_view,
            )

            self.main_content.content.controls.append(  # type: ignore
                self.generate_button,
            )

            self.main_content.content.controls.append(  # type: ignore
                self.audio_ready_button,
            )

            if self.start_button is not None:
                self.start_button.disabled = False

            self._update_audio_button()

            self.page.update()

        except LeggiMiError as exc:
            self.remove_control(self.processing_text)

            if self.start_button is not None:
                self.start_button.disabled = False

            self.page.update()

            await self._show_error(exc)

    async def generate_audio(self, e) -> None:
        """
        Genera lo script audio e i sottotitoli per il capitolo selezionato.

        Args:
            e: Evento generato dall'interazione con il controllo UI.
        """

        if (
            self.chapter_dropdown is None
            or self.chapter_dropdown.value is None
            or self.chapters is None
            or self.mode_dropdown is None
            or self.mode_dropdown.value is None
            or self.level_dropdown is None
            or self.level_dropdown.value is None
            or self.pdf_path is None
        ):
            return

        self.text_generation_id += 1
        text_generation_id = self.text_generation_id

        if self.audio_processing_text is not None:
            self.remove_control(self.audio_processing_text)

        self.audio_processing_text = create_text(
            "Dando voce al caos ordinato...",
        )

        audio_processing_text = self.audio_processing_text

        if self.generate_button is not None:
            self.generate_button.disabled = True

        self.main_content.content.controls.append(  # type: ignore
            audio_processing_text,
        )

        self.page.update()

        try:
            chapter_index = int(self.chapter_dropdown.value)

            if not 0 <= chapter_index < len(self.chapters):
                return

            chapter = self.chapters[chapter_index]

            mode = cast(
                Literal["riassunto", "dialogo"],
                self.mode_dropdown.value,
            )

            level = cast(
                Literal["base", "intermedio", "avanzato"],
                self.level_dropdown.value,
            )

            await generate_chapter_audio(
                Path(self.pdf_path).stem,
                chapter,
                mode,
                level,
            )

            if self.text_generation_id != text_generation_id:
                return

            if self.generate_button is not None:
                self.generate_button.disabled = False

            self._update_audio_button()

        except LeggiMiError as exc:
            if self.text_generation_id == text_generation_id:
                await self._show_error(exc)

                if self.generate_button is not None:
                    self.generate_button.disabled = False

                self.page.update()

        finally:
            if self.text_generation_id == text_generation_id:
                self.remove_control(audio_processing_text)

                if self.audio_processing_text is audio_processing_text:
                    self.audio_processing_text = None

                self.page.update()

    async def select_pdf(self, e) -> None:
        """
        Apre il selettore file e carica il percorso del PDF selezionato.

        Args:
            e: Evento generato dall'interazione con il controllo UI.

        Raises:
            FileSelectionError: Se si verifica un errore durante la
                selezione del file.
        """

        try:
            files = await self.file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
            )

            if not files:
                return

            pdf_path = files[0].path

            if pdf_path is None:
                return

            # Ferma e libera il vecchio player.
            if self.audio_player is not None:
                self.audio_player.cleanup()
                self.audio_player = None

            self._stop_position_updates()
            self.playback_time = 0.0

            # Reset della schermata playback.
            if self.playback_content is not None:
                self.playback_content.visible = False

            self.main_content.visible = True

            self.bottom_bar.content = self.ui_size_row

            # Invalida eventuali operazioni audio precedenti.
            self.text_generation_id += 1

            for control in [
                self.selected_file_text,
                self.processing_text,
                self.chapters_view,
                self.start_button,
                self.generate_button,
                self.audio_ready_button,
                self.audio_processing_text,
            ]:
                self.remove_control(control)

            self.pdf_path = pdf_path

            self.selected_file_text = None
            self.processing_text = None
            self.chapters_view = None
            self.start_button = None
            self.generate_button = None
            self.audio_processing_text = None
            self.audio_ready_button = None
            self.chapter_dropdown = None
            self.chapters = None
            self.playback_lines = None

            self.playback_button = None

            if self.start_button is None:
                self.start_button = create_button(
                    "Extract Chapters",
                    ft.Icons.AUTO_STORIES_SHARP,
                    self.run_processes,
                    tooltip_text=("Converti il file PDF selezionato in audio"),
                )

            self.start_button.disabled = False

            self.selected_file_text = create_text(
                f"File: {Path(self.pdf_path).name}",
            )

            self.main_content.content.controls.append(  # type: ignore
                self.selected_file_text,
            )

            self.main_content.content.controls.append(  # type: ignore
                self.start_button,
            )

            self.page.update()

        except Exception as exc:
            raise FileSelectionError(
                "Errore durante la selezione del file.",
            ) from exc
