import flet as ft

from leggimi.models.models import Chapter
from leggimi.ui.ui_config import UI_SIZE, THEME
from leggimi.ui.ui_theme import (
    set_theme_mode,
    theme_config,
)

current_ui_size = UI_SIZE


def resize_ui(
    control: ft.Control,
    new_size: float,
    exclude: ft.Control | None = None,
) -> None:
    """
    Ridimensiona ricorsivamente i componenti UI.

    Args:
        control: Controllo Flet da ridimensionare.
        new_size: Nuova dimensione base dell'interfaccia.
        exclude: Controllo da escludere dal ridimensionamento.

    Returns:
        None.
    """

    if control is exclude:
        return

    button_scale = new_size ** (1 / 16) - 0.2

    if isinstance(control, ft.Text):
        control.size = new_size

    elif isinstance(control, ft.Button):
        control.scale = button_scale

        if isinstance(control.content, ft.Text):
            control.content.size = new_size

        if control.icon is not None:
            control.icon.size = new_size  # type: ignore

        if isinstance(control.tooltip, ft.Tooltip):
            control.tooltip.text_style = ft.TextStyle(
                size=new_size * 0.7,
                color=theme_config.primary_text_color,
            )

    elif isinstance(control, ft.ListTile):
        if isinstance(control.title, ft.Control):
            resize_ui(
                control.title,
                new_size,
                exclude,
            )

    elif isinstance(control, ft.Dropdown):
        if control.page:
            dropdown_width, dropdown_menu_height = get_dropdown_dimensions(
                control.page,
                new_size,
            )

            # Dropdown impostazioni globali
            if control.label in ("Modalità", "Livello"):
                control.width = new_size * 8
                control.height = new_size * 2.2
                menu_width = new_size * 7

            # Dropdown capitoli
            else:
                control.width = dropdown_width
                control.height = new_size * 2.2
                menu_width = dropdown_width

            control.text_style = ft.TextStyle(
                size=new_size,
                color=theme_config.primary_text_color,
            )

            control.label_style = ft.TextStyle(
                color=theme_config.primary_text_color,
                size=new_size * 0.7 * 0.8,
            )

            if control.leading_icon:
                control.leading_icon.size = new_size * 1.2  # type: ignore

            if control.trailing_icon:
                control.trailing_icon.size = new_size  # type: ignore

            if control.selected_trailing_icon:
                control.selected_trailing_icon.size = new_size  # type: ignore

            control.menu_style = ft.MenuStyle(
                fixed_size=ft.Size(
                    width=menu_width,
                    height=dropdown_menu_height,
                ),
            )

            for option in control.options:
                option.style = ft.ButtonStyle(
                    color=theme_config.primary_text_color,
                    text_style=ft.TextStyle(
                        size=new_size,
                    ),
                )

    if hasattr(control, "controls"):
        for child in control.controls:  # type: ignore
            resize_ui(child, new_size, exclude)

    content = getattr(control, "content", None)

    if isinstance(content, ft.Control):
        resize_ui(
            content,
            new_size,
            exclude,
        )


def create_ui_size_slider(
    min_size: float = 35,
    max_size: float = 80,
) -> ft.Row:
    """
    Crea lo slider per modificare la dimensione dell'interfaccia.

    Args:
        min_size: Dimensione minima dell'interfaccia.
        max_size: Dimensione massima dell'interfaccia.

    Returns:
        Una tupla contenente il Row dello slider e il testo
        utilizzato per visualizzare l'etichetta "UI Size".
    """

    ui_size_text = create_text("UI Size")

    def resize_ui_handler(e):
        """
        Aggiorna la dimensione dell'interfaccia in base al valore
        selezionato nello slider.

        Args:
            e: Evento generato dalla modifica del valore dello slider.

        Returns:
            None.
        """

        global current_ui_size

        new_size = e.control.value
        current_ui_size = new_size

        percentage = (new_size - min_size) / (max_size - min_size) * 100

        e.control.label = f"{percentage:.0f}%"

        resize_ui(
            e.page,
            new_size,
            exclude=ui_size_text,
        )

        e.page.update()

    initial_percentage = (UI_SIZE - min_size) / (max_size - min_size) * 100

    ui_size_slider = ft.Slider(
        min=min_size,
        max=max_size,
        divisions=10,
        thumb_color=theme_config.primary_text_color,
        active_color=theme_config.primary_text_color,
        value=UI_SIZE,
        tooltip=(
            ft.Tooltip(
                message="Modifica la scala interfaccia",
                text_style=ft.TextStyle(
                    size=current_ui_size * 0.8,
                    color=theme_config.primary_text_color,
                ),
                bgcolor=theme_config.tooltip_bgcolor,
            )
        ),
        label=f"{initial_percentage:.0f}%",
        width=300,
        on_change=resize_ui_handler,
    )

    row = ft.Row(
        margin=ft.Margin.only(top=15),
        controls=[
            ui_size_text,
            ui_size_slider,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return row


def create_global_settings_row() -> tuple[ft.Row, ft.Dropdown, ft.Dropdown]:
    """
    Crea la barra delle impostazioni globali dell'applicazione.
    """

    def create_setting_dropdown(
        label: str,
        options: list[tuple[str, str]],
        value: str,
    ) -> ft.Dropdown:
        return ft.Dropdown(
            color=theme_config.primary_text_color,
            width=current_ui_size * 8,
            height=current_ui_size * 2.2,
            border=ft.InputBorder.OUTLINE,
            border_color=theme_config.primary_text_color,
            border_width=2,
            border_radius=10,
            align=ft.Alignment.CENTER,
            label=label,
            value=value,
            text_style=ft.TextStyle(
                size=current_ui_size,
                color=theme_config.primary_text_color,
            ),
            label_style=ft.TextStyle(
                size=current_ui_size * 0.7,
                color=theme_config.primary_text_color,
            ),
            menu_style=ft.MenuStyle(
                fixed_size=ft.Size(
                    width=320,
                    height=current_ui_size * 4,
                ),
            ),
            options=[
                ft.DropdownOption(
                    key=key,
                    text=text,
                    style=ft.ButtonStyle(
                        color=theme_config.primary_text_color,
                        text_style=ft.TextStyle(
                            size=current_ui_size,
                            color=theme_config.primary_text_color,
                        ),
                    ),
                )
                for key, text in options
            ],
            trailing_icon=ft.Icon(
                ft.Icons.ARROW_DROP_DOWN,
                color=theme_config.primary_text_color,
                size=current_ui_size,
            ),
            selected_trailing_icon=ft.Icon(
                ft.Icons.ARROW_DROP_UP,
                color=theme_config.primary_text_color,
                size=current_ui_size,
            ),
            tooltip=ft.Tooltip(
                message=f"Imposta {label.lower()}",
                text_style=ft.TextStyle(
                    size=current_ui_size * 0.7,
                    color=theme_config.primary_text_color,
                ),
                bgcolor=theme_config.tooltip_bgcolor,
            ),
        )

    mode_dropdown = create_setting_dropdown(
        "Modalità",
        [
            ("riassunto", "riassunto"),
            ("dialogo", "dialogo"),
        ],
        "riassunto",
    )

    level_dropdown = create_setting_dropdown(
        "Livello",
        [
            ("base", "base"),
            ("intermedio", "intermedio"),
            ("avanzato", "avanzato"),
        ],
        "base",
    )

    return (
        ft.Row(
            controls=[
                mode_dropdown,
                level_dropdown,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        ),
        mode_dropdown,
        level_dropdown,
    )


def create_button(
    text: str,
    icon,
    on_click,
    tooltip_text: str | None = None,
    size: float | None = None,
) -> ft.Button:
    """
    Crea un pulsante Flet con testo e icona.

    Args:
        text: Testo visualizzato nel pulsante.
        icon: Icona visualizzata nel pulsante.
        on_click: Funzione eseguita al clic sul pulsante.
        size: Dimensione del testo e dell'icona.

    Returns:
        Pulsante Flet configurato.
    """

    if size is None:
        size = current_ui_size

    button_scale = current_ui_size ** (1 / 16) - 0.2

    return ft.Button(
        content=ft.Text(text, size=size),
        icon=ft.Icon(icon, size=size),  # type: ignore
        scale=button_scale,
        color=theme_config.primary_text_color,
        on_click=on_click,
        tooltip=(
            ft.Tooltip(
                message=tooltip_text,
                text_style=ft.TextStyle(
                    size=current_ui_size * 0.7,
                    color=theme_config.primary_text_color,
                ),
                bgcolor=theme_config.tooltip_bgcolor,
            )
            if tooltip_text is not None
            else None
        ),
        align=ft.Alignment.CENTER,
        style=ft.ButtonStyle(
            side={
                ft.ControlState.FOCUSED: ft.BorderSide(
                    width=3,
                    color=ft.Colors.AMBER,
                ),
            },
        ),
    )


def create_text(
    text: str,
    size: float | None = None,
) -> ft.Text:
    """
    Crea un controllo di testo Flet.

    Args:
        text: Testo da visualizzare.
        size: Dimensione del testo. Se non specificata, viene utilizzata
            la dimensione corrente dell'interfaccia.

    Returns:
        Controllo di testo Flet configurato.
    """

    return ft.Text(
        text,
        color=theme_config.primary_text_color,
        size=(current_ui_size if size is None else size),
        align=ft.Alignment.CENTER,
    )


def get_dropdown_dimensions(
    page: ft.Page,
    size: float,
) -> tuple[float, float]:
    dropdown_scale = size ** (1 / 4)

    page_width = page.width or 1500
    page_height = page.height or 750

    dropdown_width = page_width * 0.2 * dropdown_scale
    dropdown_menu_height = page_height * 0.15 * dropdown_scale

    return dropdown_width, dropdown_menu_height


def create_chapters_dropdown(
    chapters: list[Chapter],
    # tooltip_text: str | None = None,
    page: ft.Page,
    size: float | None = None,
) -> tuple[ft.Container, ft.Dropdown]:
    """
    Crea un menu Dropdown Flet con testo e icona.

    Args:
        chapters: Lista di capitoli contenenti titolo e testo.
        size: Dimensione del testo e dell'icona.

    Returns:
        Pulsante Flet configurato.
    """

    if size is None:
        size = current_ui_size

    dropdown_width, dropdown_menu_height = get_dropdown_dimensions(
        page,
        current_ui_size,
    )

    dropdown = ft.Dropdown(
        color=theme_config.primary_text_color,
        autofocus=True,
        border=ft.InputBorder.UNDERLINE,
        border_color=theme_config.primary_text_color,
        border_width=2,
        width=dropdown_width,
        height=current_ui_size * 2.2,
        align=ft.Alignment.CENTER,
        label="Seleziona un capitolo",
        text_style=ft.TextStyle(
            size=current_ui_size,
            color=theme_config.primary_text_color,
        ),
        menu_style=ft.MenuStyle(
            fixed_size=ft.Size(
                width=dropdown_width,
                height=dropdown_menu_height,
            ),
        ),
        options=[
            ft.DropdownOption(
                key=str(idx),
                text=chapter.title,
                style=ft.ButtonStyle(
                    color=theme_config.primary_text_color,
                    text_style=ft.TextStyle(
                        size=current_ui_size,
                    ),
                ),
            )
            for idx, chapter in enumerate(chapters)
        ],
        label_style=ft.TextStyle(
            color=theme_config.primary_text_color,
            size=current_ui_size * 0.7,
        ),
        value="0",
        leading_icon=ft.Icon(
            ft.Icons.SEARCH,
            color=theme_config.primary_text_color,
            size=current_ui_size * 1.2,
        ),
        trailing_icon=ft.Icon(
            ft.Icons.ARROW_DROP_DOWN,
            color=theme_config.primary_text_color,
            size=current_ui_size,
        ),
        selected_trailing_icon=ft.Icon(
            ft.Icons.ARROW_DROP_UP,
            color=theme_config.primary_text_color,
            size=current_ui_size,
        ),
    )

    return (
        ft.Container(
            margin=ft.Margin.only(
                top=current_ui_size * 0.3,
            ),
            content=dropdown,
        ),
        dropdown,
    )


def update_text_theme(control: ft.Control) -> None:
    """
    Aggiorna ricorsivamente i colori dei testi.
    """

    if isinstance(control, ft.Text):
        control.color = theme_config.primary_text_color

    if isinstance(control, ft.Button):
        control.color = theme_config.primary_text_color

        if isinstance(control.content, ft.Text):
            control.content.color = theme_config.primary_text_color

        elif isinstance(control, ft.Dropdown):
            control.color = theme_config.primary_text_color
            control.border_color = theme_config.primary_text_color

            control.text_style = ft.TextStyle(
                size=current_ui_size,
                color=theme_config.primary_text_color,
            )

            control.label_style = ft.TextStyle(
                size=current_ui_size * 0.7 * 0.8,
                color=theme_config.primary_text_color,
            )

            # freccette dropdown
            if control.trailing_icon:
                control.trailing_icon.color = theme_config.primary_text_color  # type: ignore

            if control.selected_trailing_icon:
                control.selected_trailing_icon.color = theme_config.primary_text_color  # type: ignore

            # opzioni del menu
            for option in control.options:
                option.style = ft.ButtonStyle(
                    color=theme_config.primary_text_color,
                    text_style=ft.TextStyle(
                        size=current_ui_size,
                        color=theme_config.primary_text_color,
                    ),
                )

    if hasattr(control, "controls"):
        for child in control.controls:  # type: ignore
            update_text_theme(child)

    content = getattr(control, "content", None)

    if isinstance(content, ft.Control):
        update_text_theme(content)


def update_controls_theme(control: ft.Control) -> None:
    """
    Aggiorna colori e stili dei controlli dopo cambio tema.
    """

    if isinstance(control, ft.Text):
        control.color = theme_config.primary_text_color

    elif isinstance(control, ft.Button):
        control.color = theme_config.primary_text_color

        if isinstance(control.content, ft.Text):
            control.content.color = theme_config.primary_text_color

        if control.icon:
            control.icon.color = theme_config.primary_text_color  # type: ignore

    elif isinstance(control, ft.IconButton):
        control.icon_color = theme_config.primary_text_color

    elif isinstance(control, ft.Slider):
        control.thumb_color = theme_config.primary_text_color
        control.active_color = theme_config.primary_text_color

        if isinstance(control.tooltip, ft.Tooltip):
            control.tooltip.bgcolor = theme_config.tooltip_bgcolor
            control.tooltip.text_style = ft.TextStyle(
                size=current_ui_size * 0.8,
                color=theme_config.primary_text_color,
            )

    elif isinstance(control, ft.Dropdown):
        control.color = theme_config.primary_text_color
        control.border_color = theme_config.primary_text_color

        control.text_style = ft.TextStyle(
            size=current_ui_size,
            color=theme_config.primary_text_color,
        )

        for option in control.options:
            option.style = ft.ButtonStyle(
                color=theme_config.primary_text_color,
                text_style=ft.TextStyle(
                    size=current_ui_size,
                    color=theme_config.primary_text_color,
                ),
            )

        control.label_style = ft.TextStyle(
            size=current_ui_size * 0.7 * 0.8,
            color=theme_config.primary_text_color,
        )

        if control.leading_icon:
            control.leading_icon.color = theme_config.primary_text_color  # type: ignore

        if control.trailing_icon:
            control.trailing_icon.color = theme_config.primary_text_color  # type: ignore

        if control.selected_trailing_icon:
            control.selected_trailing_icon.color = theme_config.primary_text_color  # type: ignore

    if isinstance(control.tooltip, ft.Tooltip):
        control.tooltip.bgcolor = theme_config.tooltip_bgcolor
        control.tooltip.text_style = ft.TextStyle(
            size=current_ui_size * 0.7,
            color=theme_config.primary_text_color,
        )

    if hasattr(control, "controls"):
        for child in control.controls:  # type: ignore
            update_controls_theme(child)

    content = getattr(control, "content", None)

    if isinstance(content, ft.Control):
        update_controls_theme(content)


def create_theme_switch_button() -> ft.IconButton:
    """
    Crea un pulsante icona per alternare tema chiaro e scuro.
    """

    def switch_theme(e) -> None:
        current_theme = e.page.theme_mode

        new_theme = "light" if current_theme == ft.ThemeMode.DARK else "dark"

        set_theme_mode(
            e.page,
            new_theme,
        )

        e.control.icon = (
            ft.Icons.DARK_MODE if new_theme == "light" else ft.Icons.LIGHT_MODE
        )

        e.control.icon_color = theme_config.primary_text_color

        e.control.style = ft.ButtonStyle(
            bgcolor=theme_config.tooltip_bgcolor,
            side=ft.BorderSide(
                width=1,
                color=theme_config.primary_text_color,
            ),
        )

        e.page.theme = ft.Theme(
            font_family="Roboto",
            scrollbar_theme=ft.ScrollbarTheme(
                thumb_color=theme_config.primary_text_color,
            ),
        )

        update_text_theme(e.page)
        update_controls_theme(e.page)
        update_tooltips_theme(e.page)

        e.page.update()

    is_dark = THEME == "dark"

    return ft.IconButton(
        icon=(ft.Icons.LIGHT_MODE if is_dark else ft.Icons.DARK_MODE),
        icon_color=theme_config.primary_text_color,
        icon_size=current_ui_size * 1.3,
        tooltip=ft.Tooltip(
            message="Cambia tema",
            text_style=ft.TextStyle(
                size=current_ui_size * 0.7,
                color=theme_config.primary_text_color,
            ),
            bgcolor=theme_config.tooltip_bgcolor,
        ),
        style=ft.ButtonStyle(
            bgcolor=theme_config.tooltip_bgcolor,
            shape=ft.CircleBorder(),
            side=ft.BorderSide(
                width=1,
                color=theme_config.primary_text_color,
            ),
        ),
        on_click=switch_theme,
    )


def update_tooltips_theme(control: ft.Control) -> None:
    """
    Aggiorna i tooltip ricorsivamente in base al tema corrente.
    """

    if isinstance(control.tooltip, ft.Tooltip):
        control.tooltip.text_style = ft.TextStyle(
            size=current_ui_size * 0.7,
            color=theme_config.primary_text_color,
        )
        control.tooltip.bgcolor = theme_config.tooltip_bgcolor

    if hasattr(control, "controls"):
        for child in control.controls:  # type: ignore
            update_tooltips_theme(child)

    if hasattr(control, "content") and isinstance(
        control.content,  # type: ignore
        ft.Control,
    ):
        update_tooltips_theme(control.content)  # type: ignore
