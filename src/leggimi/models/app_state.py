from dataclasses import dataclass

import asyncio
from pathlib import Path
from typing import cast
from typing_extensions import Literal

import flet as ft

from leggimi.errors import FileSelectionError
from leggimi.models.models import Chapter
from leggimi.pipeline import (
    process_pdf,
    generate_chapter_audio,
)
from leggimi.ui.ui_components import (
    create_button,
    create_chapters_dropdown,
    create_text,
)


@dataclass
class AppState:
    """
    Gestisce lo stato dell'applicazione e le operazioni principali
    dell'interfaccia grafica.
    """

    page: ft.Page
    file_picker: ft.FilePicker
    main_content: ft.Container

    mode_dropdown: ft.Dropdown | None = None
    level_dropdown: ft.Dropdown | None = None
    chapter_dropdown: ft.Dropdown | None = None

    pdf_path: str | None = None
    selected_file_text: ft.Text | None = None
    processing_text: ft.Text | None = None
    start_button: ft.Button | None = None
    chapters_view: ft.Container | None = None
    chapters: list[Chapter] | None = None
    generate_button: ft.Button | None = None
    audio_processing_text: ft.Text | None = None

    def remove_control(
        self,
        control: ft.Control | None,
    ) -> None:
        """
        Rimuove un controllo dal contenuto principale dell'interfaccia.

        Args:
            control: Controllo Flet da rimuovere.

        """

        if control is not None and control in self.main_content.content.controls:  # type: ignore
            self.main_content.content.controls.remove(control)  # type: ignore

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

        self.main_content.content.controls.append(  # type: ignore
            self.processing_text,
        )

        self.page.update()

        chapters = await asyncio.to_thread(
            process_pdf,
            self.pdf_path,
        )

        self.chapters = chapters

        self.remove_control(self.processing_text)

        self.chapters_view, self.chapter_dropdown = create_chapters_dropdown(
            chapters,
            self.page,
        )

        if self.generate_button is None:
            self.generate_button = create_button(
                "Genera mp3",
                ft.Icons.SPATIAL_AUDIO_OFF,
                self.generate_audio,
                tooltip_text="Genera riassunto/dialogo dal capitolo selezionato",
            )

        self.main_content.content.controls.append(  # type: ignore
            self.chapters_view,
        )

        self.main_content.content.controls.append(  # type: ignore
            self.generate_button,
        )

        self.page.update()

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
            or self.level_dropdown is None
            or self.pdf_path is None
        ):
            return

        if self.audio_processing_text is None:
            self.audio_processing_text = create_text(
                "Dando voce al caos ordinato...",
            )

        if self.generate_button is not None:
            self.generate_button.disabled = True

        self.main_content.content.controls.append(  # type: ignore
            self.audio_processing_text,
        )

        self.page.update()

        try:
            chapter_index = int(self.chapter_dropdown.value)

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

            self.audio_processing_text.value = "Audio pronto! 🎧"
            self.page.update()

            await asyncio.sleep(5)

        finally:
            self.remove_control(self.audio_processing_text)

            if self.generate_button is not None:
                self.generate_button.disabled = False

            self.page.update()

    async def select_pdf(self, e) -> None:
        """
        Apre il selettore file e carica il percorso del PDF selezionato.

        Args:
            e: Evento generato dall'interazione con il controllo UI.

        Raises:
            FileSelectionError: Se si verifica un errore durante la selezione
                del file.
        """

        try:
            files = await self.file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
            )

            if not files:
                return

            self.pdf_path = files[0].path

            if self.pdf_path is None:
                return

            for control in [
                self.selected_file_text,
                self.processing_text,
                self.chapters_view,
                self.start_button,
            ]:
                self.remove_control(control)

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
