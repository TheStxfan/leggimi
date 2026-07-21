import asyncio

import flet as ft

from leggimi.pipeline import process_pdf


async def main(page: ft.Page):
    page.title = "LeggiMi"

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    selected_pdf_path: str | None = None

    async def run_processes(e):
        if selected_pdf_path is None:
            return

        page.add(ft.Text("Processing..."))

        chapters = await asyncio.to_thread(
            process_pdf,
            selected_pdf_path,
        )

        ### Testing

        page.add(ft.Text(f"Capitoli trovati: {len(chapters)}"))

        page.add()
        for chapter in chapters:
            page.add(ft.Text(f"{chapter.title}\n{chapter.text}\n\n"))

    async def on_pdf_selected(e):
        nonlocal selected_pdf_path

        file = await file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
        )

        if not file:
            return

        selected_pdf_path = file[0].path

        if selected_pdf_path is None:
            return

        page.add(ft.Text(f"File selezionato: {selected_pdf_path}"))

        page.add(
            ft.Button(
                content="Start",
                icon=ft.Icons.START,
                on_click=run_processes,
            )
        )

    page.add(ft.Text("Benvenuto su LeggiMi!"))

    page.add(
        ft.Button(
            content="Seleziona un PDF",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=on_pdf_selected,
        )
    )


ft.run(main)
