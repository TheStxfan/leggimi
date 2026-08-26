#!/usr/bin/env bash

clear 2>/dev/null || true

set -euo pipefail

# Vai alla cartella del progetto (dove sta questo script)
cd "$(dirname "$0")" || exit 1

# Attiva il virtual environment locale
source .venv/bin/activate

# Rendi il package `leggimi` importabile da qualsiasi punto
export PYTHONPATH="src:${PYTHONPATH:-}"

# python -c "import flet as ft; import inspect; print(inspect.signature(ft.Dropdown))"
# python -c "import flet as ft; import inspect; print(inspect.signature(ft.Window))"
# python -c "import flet; print(flet.__version__)"
# python -c "import flet as ft; print([x for x in dir(ft.Page) if 'drop' in x.lower() or 'file' in x.lower()])"
# python -c "import flet as ft; import inspect; print(inspect.signature(ft.MultiView)); print(inspect.getsource(ft.MultiView))"
# python -c "import flet, pathlib; print(pathlib.Path(flet.__file__).parent)"
# python -c "import flet as ft, inspect; print(inspect.signature(ft.run)); print(ft.AppView); print(list(ft.AppView))"
# python -c "import flet, inspect; print(inspect.getsource(flet.run))"