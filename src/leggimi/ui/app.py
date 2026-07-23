import asyncio

import flet as ft

from leggimi.errors import (
    FileSelectionError,
    UIInitializationError,
)
from leggimi.pipeline import process_pdf
from leggimi.ui.ui_components import (
    create_button,
    create_text,
    create_ui_size_slider,
)


async def main(page: ft.Page):
    """
    Inizializza l'interfaccia grafica dell'applicazione LeggiMi.

    Args:
        page: Pagina Flet utilizzata per costruire e visualizzare
            l'interfaccia.

    Returns:
        None.

    Raises:
        UIInitializationError: Se si verifica un errore durante
            l'inizializzazione dell'interfaccia grafica.
    """

    try:
        page.title = "LeggiMi"
        page.theme = ft.Theme(
            font_family="Roboto",
        )
        page.fonts = {
            "Roboto": "fonts/Roboto-Regular.ttf",
        }
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "black"

        file_picker = ft.FilePicker()
        page.services.append(file_picker)

    except Exception as exc:
        raise UIInitializationError(
            "Errore durante l'inizializzazione dell'interfaccia.",
        ) from exc

    pdf_path: str | None = None

    selected_file_text: ft.Text | None = None
    processing_text: ft.Text | None = None

    start_button: ft.Button | None = None

    chapters_view: ft.ListView | None = None

    main_content = ft.Column(
        expand=True,
    )

    def remove_control(
        control: ft.Control | None,
    ) -> None:
        """
        Rimuove un controllo dal contenuto principale, se presente.

        Args:
            control: Controllo da rimuovere.

        Returns:
            None.
        """

        if control is not None and control in main_content.controls:
            main_content.controls.remove(control)

    async def run_processes(e):
        """
        Elabora il PDF selezionato e visualizza i capitoli estratti.

        Args:
            e: Evento generato dal clic sul pulsante.

        Returns:
            None.
        """

        nonlocal processing_text
        nonlocal chapters_view

        if pdf_path is None:
            return

        if processing_text is None:
            processing_text = create_text(
                "Processing...",
            )

        if start_button is not None:
            start_button.disabled = True

        remove_control(chapters_view)

        main_content.controls.append(
            processing_text,
        )

        page.update()

        chapters = await asyncio.to_thread(
            process_pdf,
            pdf_path,
        )

        remove_control(processing_text)

        chapters_view = ft.ListView(
            controls=[
                ft.ListTile(
                    title=create_text(
                        chapter.title,
                    ),
                    data=i,
                )
                for i, chapter in enumerate(chapters)
            ],
            expand=True,
        )

        main_content.controls.append(
            chapters_view,
        )

        page.update()

    async def select_pdf(e):
        """
        Apre il selettore di file e seleziona un PDF da elaborare.

        Args:
            e: Evento generato dal clic sul pulsante.

        Returns:
            None.

        Raises:
            FileSelectionError: Se si verifica un errore durante
                la selezione del file.
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

            remove_control(selected_file_text)
            remove_control(processing_text)
            remove_control(chapters_view)
            remove_control(start_button)

            if start_button is None:
                start_button = create_button(
                    "Start",
                    ft.Icons.START,
                    run_processes,
                    tooltip_text="Converti il file PDF selezionato in audio",
                )

            start_button.disabled = False

            selected_file_text = create_text(
                f"File selezionato: {pdf_path}",
            )

            main_content.controls.append(selected_file_text)
            main_content.controls.append(start_button)

            page.update()

        except Exception as exc:
            raise FileSelectionError(
                "Errore durante la selezione del file.",
            ) from exc

    select_pdf_button = create_button(
        "Seleziona un PDF",
        ft.Icons.UPLOAD_FILE,
        select_pdf,
        tooltip_text="Seleziona un file PDF da convertire in audio",
    )

    ui_size_row, ui_size_text = create_ui_size_slider()

    main_content.controls.append(select_pdf_button)

    page.add(
        ft.Column(
            expand=True,
            controls=[
                main_content,
                ui_size_row,
            ],
        ),
    )


ft.run(main)
