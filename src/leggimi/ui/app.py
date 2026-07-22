import asyncio

import flet as ft

from leggimi.pipeline import process_pdf
from leggimi.ui.ui_components import create_text, create_button
from leggimi.errors import FileSelectionError, UIInitializationError


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

    async def run_processes(e):
        """
        Elabora il PDF selezionato e visualizza i capitoli estratti.

        Args:
            e: Evento generato dal clic sul pulsante.

        Returns:
            None.
        """

        if pdf_path is None:
            return

        page.add(create_text("Processing..."))
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

            page.add(create_text(f"File selezionato: {pdf_path}"))

            page.add(create_button("Start", ft.Icons.START, run_processes))

            page.update()

        except Exception as exc:
            raise FileSelectionError("Errore durante la selezione del file.") from exc

    page.add(create_text("Benvenuto su LeggiMi!"))

    page.add(create_button("Seleziona un PDF", ft.Icons.UPLOAD_FILE, select_pdf))


ft.run(main)
