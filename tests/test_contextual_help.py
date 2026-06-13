from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class ContextualHelpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        try:
            from PySide6.QtWidgets import QApplication
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest(f"PySide6 no disponible: {exc}")
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        from npsc_gui.main_window import MainWindow

        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self) -> None:
        self.window.close()
        self.app.processEvents()

    def test_section_help_buttons_exist(self):
        expected = [
            "Compilador",
            "Resultados",
            "Validación",
            "Perfiles",
            "Glosario",
            "Configuración",
        ]
        for key in expected:
            with self.subTest(key=key):
                button = self.window.section_help_buttons[key]
                self.assertEqual(button.text(), "?")
                self.assertEqual(button.objectName(), "HelpIconButton")
                self.assertTrue(button.accessibleName())

    def test_popover_word_wrap_and_width(self):
        button = self.window.section_help_buttons["Compilador"]
        self.assertTrue(button.popover.body_label.wordWrap())
        self.assertLessEqual(button.popover.maximumWidth(), 380)
        self.assertGreaterEqual(button.popover.minimumWidth(), 240)

    def test_privacy_help_has_distinct_modes(self):
        title = self.window.option_help_buttons["privacy"].popover.title_label.text()
        body = self.window.option_help_buttons["privacy"].popover.body_label.text()
        self.assertIn("Privacidad", title)
        self.assertIn("Guardar original completo", body)
        self.assertIn("Guardar solo huella digital", body)
        self.assertIn("Guardar vista parcial recortada", body)
        self.assertEqual(self.window.option_help_buttons["privacy"].glossary_id, "privacy")

    def test_no_long_tooltips_on_invasive_containers(self):
        self.assertFalse(self.window.tabs.toolTip())
        self.assertTrue(all(not self.window.tabs.tabToolTip(i) for i in range(self.window.tabs.count())))
        self.assertFalse(self.window.prompt_edit.toolTip())
        self.assertFalse(self.window.hybrid_text.toolTip())
        self.assertFalse(self.window.validation_detail.toolTip())
        for button in self.window.nav_items.values():
            self.assertFalse(button.toolTip())

    def test_help_opens_and_escape_closes(self):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QKeyEvent
        from PySide6.QtCore import QEvent

        button = self.window.section_help_buttons["Compilador"]
        button._show()
        self.app.processEvents()
        self.assertTrue(button.popover.isVisible())
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)
        self.app.sendEvent(button, event)
        self.app.processEvents()
        self.assertFalse(button.popover.isVisible())


if __name__ == "__main__":
    unittest.main()
