from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class GlossaryResourceTests(unittest.TestCase):
    def test_glossary_resource_exists_and_loads(self):
        from npsc_gui.glossary import load_glossary, validate_glossary

        self.assertTrue((SRC / "npsc_resources" / "configs" / "ui_glossary_es.json").exists())
        entries = load_glossary()
        self.assertGreaterEqual(len(entries), 45)
        self.assertEqual(validate_glossary(entries), [])

    def test_required_terms_exist(self):
        from npsc_gui.glossary import get_entry

        required = [
            "Prompt",
            "Prompt original",
            "Prompt listo para usar",
            "Mejorar prompt",
            "Compilar",
            "Modelo de destino",
            "AUTO",
            "Modo sencillo",
            "Modo avanzado",
            "Resultado",
            "Archivo generado",
            "Artefacto",
            "Guardar resultados",
            "Carpeta de resultados",
            "execution_prompt.txt",
            "Informe completo",
            "Audit bundle",
            "audit_bundle.md",
            "audit_bundle.json",
            "Markdown",
            "JSON",
            "JSON para programas",
            "JSON machine-oriented",
            "NSL",
            "NSL compacto",
            "compact_nsl.nsl",
            "Perfil semántico",
            "Tipo de mejora",
            "FAST",
            "STANDARD",
            "ADVANCED",
            "ROP",
            "RESEARCH_MAX",
            "Compresión técnica",
            "Nivel de detalle técnico",
            "profile_default",
            "safe",
            "balanced",
            "aggressive",
            "all",
            "Privacidad",
            "full_original",
            "hash_only",
            "redacted_preview",
            "SHA-256",
            "Huella digital",
            "Validación",
            "Validación estricta",
            "strict",
            "Advertencia",
            "Bloqueado",
            "Preservación semántica",
            "retention_score",
            "precision_score",
            "unsupported_addition_score",
            "contradiction_score",
            "constraint_traceability_score",
            "nsl_size_ratio",
            "execution_size_ratio",
            "overhead",
            "expansión intencionada",
            "Seed",
            "Seeds",
            "Regla semántica",
            "Constraint",
            "Restricción",
            "Restricciones y origen",
            "Core",
            "CLI",
            "Offline",
            "Local-first",
            "IR",
            "NPSC-HYBRID",
        ]
        missing = [term for term in required if get_entry(term) is None]
        self.assertEqual(missing, [])

    def test_search_case_accent_alias_and_category(self):
        from npsc_gui.glossary import search_glossary

        self.assertTrue(any(item["id"] == "artifact" for item in search_glossary("ARTEFACTO")))
        self.assertTrue(any(item["id"] == "semantic_preservation" for item in search_glossary("preservacion semantica")))
        self.assertTrue(any(item["id"] == "hash_only" for item in search_glossary("solo hash")))
        privacy = search_glossary("", "Privacidad")
        self.assertTrue(privacy)
        self.assertTrue(all(item["category"] == "Privacidad" for item in privacy))

    def test_glossary_docs_are_generated_from_source(self):
        path = ROOT / "docs" / "GLOSARIO_ES.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("Este documento se genera desde", text)
        self.assertIn("Prompt listo para usar", text)
        self.assertIn("JSON para programas", text)


class GlossaryGuiTests(unittest.TestCase):
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

    def test_sidebar_order_and_simple_mode_labels(self):
        self.window._switch_to_mode("simple")
        names = list(self.window.nav_items.keys())
        self.assertIn("glosario", names)
        # In the new layout, "ayuda" and "acerca de" are no longer separate pages
        # Switch to extreme mode to check tabs
        self.window._switch_to_mode("extreme")
        visible_tabs = [
            self.window.tabs.tabText(index)
            for index in range(self.window.tabs.count())
            if self.window.tabs.isTabVisible(index)
        ]
        self.assertEqual(
            visible_tabs,
            ["Resumen", "Prompt listo para usar", "Informe completo", "Prompt original", "Validación", "NSL compacto", "JSON para programas", "Reglas semánticas", "Restricciones y origen", "Perfil aplicado"],
        )
        forbidden = {"Audit bundle", "Compact NSL", "JSON machine-oriented", "Seeds", "Constraints y origen"}
        self.assertTrue(forbidden.isdisjoint(set(visible_tabs)))

    def test_advanced_mode_exposes_human_technical_labels(self):
        self.window._switch_to_mode("extreme")
        tabs = [self.window.tabs.tabText(index) for index in range(self.window.tabs.count())]
        for label in ["NSL compacto", "JSON para programas", "Reglas semánticas", "Restricciones y origen"]:
            self.assertIn(label, tabs)

    def test_visible_labels_map_to_internal_values(self):
        self.window.level_combo.setCurrentIndex(0)
        self.assertEqual(self.window._combo_value(self.window.level_combo), "profile_default")
        self.window.level_combo.setCurrentIndex(1)
        self.assertEqual(self.window._combo_value(self.window.level_combo), "safe")
        self.window.level_combo.setCurrentIndex(2)
        self.assertEqual(self.window._combo_value(self.window.level_combo), "balanced")
        self.window.level_combo.setCurrentIndex(3)
        self.assertEqual(self.window._combo_value(self.window.level_combo), "aggressive")
        self.window.level_combo.setCurrentIndex(4)
        self.assertEqual(self.window._combo_value(self.window.level_combo), "all")
        self.window.privacy_combo.setCurrentIndex(0)
        self.assertEqual(self.window._combo_value(self.window.privacy_combo), "full_original")
        self.window.privacy_combo.setCurrentIndex(1)
        self.assertEqual(self.window._combo_value(self.window.privacy_combo), "hash_only")
        self.window.privacy_combo.setCurrentIndex(2)
        self.assertEqual(self.window._combo_value(self.window.privacy_combo), "redacted_preview")

    def test_context_help_can_open_glossary_term(self):
        button = self.window.option_help_buttons["privacy"]
        self.assertEqual(button.glossary_id, "privacy")
        self.window.open_glossary_term(button.glossary_id)
        self.assertIs(self.window.stack.currentWidget(), self.window.pages["glosario"])
        self.assertIn("Privacidad", self.window.glossary_detail.toPlainText())

    def test_no_long_tooltips_on_panels_after_glossary_addition(self):
        self.assertFalse(self.window.tabs.toolTip())
        self.assertFalse(self.window.glossary_detail.toolTip())
        self.assertFalse(self.window.glossary_list.toolTip())


if __name__ == "__main__":
    unittest.main()
