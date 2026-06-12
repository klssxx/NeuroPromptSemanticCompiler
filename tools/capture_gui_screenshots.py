#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from npsc_gui.main_window import MainWindow

    out_dir = ROOT / "artifacts" / "gui_qa"
    out_dir.mkdir(parents=True, exist_ok=True)

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.resize(1320, 860)
    window.show()
    app.processEvents()

    def save_window(path: Path) -> None:
        window.grab().save(str(path))

    def save_screen(path: Path) -> None:
        screen = app.primaryScreen()
        pixmap = screen.grabWindow(0) if screen else window.grab()
        if pixmap.isNull():
            pixmap = window.grab()
        pixmap.save(str(path))

    def capture_help(name: str, page: str, button) -> None:
        window._select_page(page)
        app.processEvents()
        button.popover.show_near(button)
        app.processEvents()
        path = out_dir / f"{name}.png"
        save_screen(path)
        captured.append(str(path))
        button.popover.hide_now()
        app.processEvents()

    pages = [
        ("dashboard", "Panel principal"),
        ("compiler_human_labels", "Compilador"),
        ("profiles", "Perfiles"),
    ]
    captured: list[str] = []
    for name, page in pages:
        window._select_page(page)
        app.processEvents()
        path = out_dir / f"{name}.png"
        save_window(path)
        captured.append(str(path))

    capture_help("context_help_compiler", "Compilador", window.section_help_buttons["Compilador"])
    capture_help("context_help_privacy", "Compilador", window.option_help_buttons["privacy"])

    window._select_page("Glosario")
    window.glossary_search.clear()
    app.processEvents()
    path = out_dir / "glossary_empty.png"
    save_window(path)
    captured.append(str(path))

    for name, query in [
        ("glossary_search_artifact", "artefacto"),
        ("glossary_search_nsl", "nsl"),
        ("glossary_privacy_hash_only", "hash_only"),
    ]:
        window.glossary_search.setText(query)
        app.processEvents()
        path = out_dir / f"{name}.png"
        save_window(path)
        captured.append(str(path))

    window.advanced_mode.setChecked(True)
    window._select_page("Compilador")
    app.processEvents()
    path = out_dir / "compiler_advanced.png"
    save_window(path)
    captured.append(str(path))

    window.prompt_edit.setPlainText("Corrige la ortografía de este correo.")
    window.profile_combo.setCurrentText("FAST")
    window.compile_current()
    for _ in range(200):
        app.processEvents()
        if window.result:
            break
    tab_captures = {
        "results_advanced_labels": None,
        "prompt_ready": "Prompt listo para usar",
        "compact_nsl": "NSL compacto",
        "json": "JSON para programas",
        "constraints_origin": "Restricciones y origen",
    }
    for name, tab_name in tab_captures.items():
        page = "Resultados"
        window._select_page(page)
        if tab_name:
            for index in range(window.tabs.count()):
                if window.tabs.tabText(index) == tab_name:
                    window.tabs.setCurrentIndex(index)
                    break
        app.processEvents()
        path = out_dir / f"{name}.png"
        save_window(path)
        captured.append(str(path))

    capture_help("context_help_results", "Resultados", window.section_help_buttons["Resultados"])

    window.advanced_mode.setChecked(False)
    window._select_page("Resultados")
    app.processEvents()
    path = out_dir / "results_simple_labels.png"
    save_window(path)
    captured.append(str(path))

    window._select_page("Validación")
    app.processEvents()
    path = out_dir / "validation.png"
    save_window(path)
    captured.append(str(path))

    window.target_combo.setCurrentText("custom")
    window.custom_model_edit.setText("MiModeloLocal-7B")
    window._select_page("Compilador")
    app.processEvents()
    path = out_dir / "custom_model.png"
    save_window(path)
    captured.append(str(path))

    window.target_combo.setCurrentText("codex")
    window.strict_check.setChecked(True)
    window.profile_combo.setCurrentText("STANDARD")
    window.prompt_edit.setPlainText("Organiza una lista de tareas para esta semana.")
    window.compile_current()
    for _ in range(200):
        app.processEvents()
        if window.result and window.result["context_loss_report"].get("strict_status") == "blocked":
            break
    window._select_page("Resultados")
    app.processEvents()
    path = out_dir / "strict_blocked.png"
    save_window(path)
    captured.append(str(path))

    window._select_page("Ayuda")
    app.processEvents()
    path = out_dir / "help_restructured.png"
    save_window(path)
    captured.append(str(path))

    window.open_glossary_term("privacy")
    app.processEvents()
    path = out_dir / "context_help_to_glossary.png"
    save_window(path)
    captured.append(str(path))

    window.resize(1366, 768)
    window._select_page("Glosario")
    app.processEvents()
    path = out_dir / "glossary_1366x768.png"
    save_window(path)
    captured.append(str(path))
    window.resize(1366, 768)
    window._select_page("Compilador")
    app.processEvents()
    path = out_dir / "compiler_1366x768.png"
    save_window(path)
    captured.append(str(path))
    window.option_help_buttons["profile"].popover.show_near(window.option_help_buttons["profile"])
    app.processEvents()
    path = out_dir / "context_help_1366x768.png"
    save_screen(path)
    captured.append(str(path))
    window.option_help_buttons["profile"].popover.hide_now()

    (out_dir / "README.txt").write_text(
        "Capturas generadas en modo offscreen. Revisar visualmente en una sesión con DISPLAY antes de publicar.\n"
        + "\n".join(captured)
        + "\n",
        encoding="utf-8",
    )
    window.close()
    app.quit()
    print("\n".join(captured))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
