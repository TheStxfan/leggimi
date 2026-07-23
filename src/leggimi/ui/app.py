import asyncio

import flet as ft

from leggimi.pipeline import process_pdf
from leggimi.ui.ui_components import create_text, create_button
from leggimi.errors import FileSelectionError, UIInitializationError
from leggimi.ui.ui_components import (
    create_text,
    create_button,
    resize_ui,
    create_ui_size_slider,
)


async def main(page: ft.Page):
    """
    Inizializza l'interfaccia grafica dell'applicazione LeggiMi.

    Args:
        page: Pagina Flet utilizzata per costruire e visualizzare l'interfaccia.

    Returns:
        None.

    Raises:
        UIInitializationError: Se si verifica un errore durante l'inizializzazione
            dell'interfaccia grafica.
    """

    try:
        page.title = "LeggiMi"
        page.theme = ft.Theme(font_family="Roboto")
        page.fonts = {"Roboto": "fonts/Roboto-Regular.ttf"}

        file_picker = ft.FilePicker()
        page.services.append(file_picker)

    except Exception as exc:
        raise UIInitializationError(
            "Errore durante l'inizializzazione dell'interfaccia."
        ) from exc

    pdf_path: str | None = None

    selected_file_text: ft.Text | None = None
    processing_text: ft.Text | None = None

    start_button: ft.Button | None = None

    chapters_view: ft.ListView | None = None

    async def run_processes(e):
        """
        Elabora il PDF selezionato e visualizza i capitoli estratti.

        Args:
            e: Evento generato dal clic sul pulsante.

        Returns:
            None.
        """

        nonlocal processing_text, chapters_view

        if pdf_path is None:
            return

        if processing_text is None:
            processing_text = create_text("Processing...")

        if start_button is not None:
            start_button.disabled = True
            # start_button.color = "grey"

        if chapters_view is not None:
            page.remove(chapters_view)

        page.add(processing_text)
        page.update()

        chapters = await asyncio.to_thread(
            process_pdf,
            pdf_path,
        )

        chapters_view = ft.ListView(
            controls=[
                ft.ListTile(
                    title=create_text(chapter.title),
                    data=i,
                )
                for i, chapter in enumerate(chapters)
            ],
            expand=True,
        )

        page.add(chapters_view)
        page.update()

    async def select_pdf(e):
        """
        Apre il selettore di file e seleziona un PDF da elaborare.

        Args:
            e: Evento generato dal clic sul pulsante.

        Returns:
            None.

        Raises:
            FileSelectionError: Se si verifica un errore durante la selezione
                del file.
        """

        nonlocal pdf_path
        nonlocal selected_file_text
        nonlocal start_button

        try:
            file = await file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
            )

            if not file:
                return

            pdf_path = file[0].path

            if pdf_path is None:
                return

            if selected_file_text is not None:
                page.remove(selected_file_text)

            if processing_text is not None:
                page.remove(processing_text)

            if start_button is not None:
                start_button.disabled = False
                # start_button.color = "grey"
            else:
                start_button = create_button(
                    "Start",
                    ft.Icons.START,
                    run_processes,
                )

            if chapters_view is not None:
                page.remove(chapters_view)

            selected_file_text = create_text(f"File selezionato: {pdf_path}")

            page.add(selected_file_text)

            page.add(start_button)

            page.update()

        except Exception as exc:
            raise FileSelectionError("Errore durante la selezione del file.") from exc

    welcome_text: ft.Text = create_text("Benvenuto su LeggiMi!")

    select_pdf_button: ft.Button = create_button(
        "Seleziona un PDF",
        ft.Icons.UPLOAD_FILE,
        select_pdf,
    )

    ui_size_row, ui_size_text = create_ui_size_slider()

    page.add(ui_size_row)
    page.add(welcome_text)
    page.add(select_pdf_button)


ft.run(main)
