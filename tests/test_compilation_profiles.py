from __future__ import annotations

import json
import hashlib
import os
import shutil
import sys
import time
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from compilation_profiles import load_compilation_profiles
from npsc_service import CompileRequest, compile_prompt, compile_for_gui
from npsc_cli import run_cli
from profile_selector import auto_select_profile
from constraint_normalizer import normalize_constraints
from rop_template import REQUIRED_ROP_SECTIONS
from semantic_dictionary import validate_semantic_dictionary
from semantic_extractor import extract_semantics
from npsc_service import CompileRequest, compile_prompt


class CompilationProfileTests(unittest.TestCase):
    def _run(self, name: str, args: list[str]) -> Path:
        out_dir = ROOT / "outputs" / name
        if out_dir.exists():
            shutil.rmtree(out_dir)
        code = run_cli(["--out", str(out_dir), "--target", "codex", *args])
        self.assertEqual(code, 0)
        return out_dir

    def test_config_contains_required_profiles(self):
        config = load_compilation_profiles()
        for profile in ["FAST", "STANDARD", "ADVANCED", "ROP", "RESEARCH_MAX", "AUTO"]:
            self.assertIn(profile, config["profiles"])
        self.assertEqual(config["default_profile"], "STANDARD")

    def test_fast_generates_more_compact_output_than_advanced(self):
        prompt = "Reescribe este prompt simple para que sea claro y conserva no sudo."
        fast = self._run("test_profile_fast", ["--text", prompt, "--profile", "fast"])
        advanced = self._run("test_profile_advanced", ["--text", prompt, "--profile", "advanced"])

        fast_text = (fast / "optimized_prompt.txt").read_text(encoding="utf-8")
        advanced_text = (advanced / "optimized_prompt.txt").read_text(encoding="utf-8")
        self.assertLess(len(fast_text), len(advanced_text))
        self.assertIn("FAST", (fast / "profile_report.json").read_text(encoding="utf-8"))

    def test_standard_is_default_profile(self):
        out_dir = self._run("test_profile_default", ["--text", "Compila este prompt para Codex sin sudo."])
        report = json.loads((out_dir / "profile_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["applied_profile"], "STANDARD")
        self.assertTrue((out_dir / "hybrid_semantic_prompt.md").exists())

    def test_rop_includes_template_and_output_schema(self):
        prompt = "Decide la mejor estrategia de negocio con riesgos, probabilidades y escenarios. No uses sudo."
        out_dir = self._run("test_profile_rop", ["--text", prompt, "--profile", "rop"])
        optimized = (out_dir / "optimized_prompt.txt").read_text(encoding="utf-8").lower()
        hybrid = (out_dir / "hybrid_semantic_prompt.md").read_text(encoding="utf-8").lower()
        report = json.loads((out_dir / "context_loss_report.json").read_text(encoding="utf-8"))

        self.assertIn("reality_oriented_optimization_engine", optimized)
        self.assertIn("output_schema", optimized)
        self.assertIn("10.confidence_score[0-100]", optimized)
        self.assertIn("stop_if[", optimized)
        self.assertIn("expected_improvement", optimized)
        self.assertIn("complexity_cost", optimized)
        for section in REQUIRED_ROP_SECTIONS:
            self.assertIn(section.lower(), optimized)
        self.assertIn("rop integrado", hybrid)
        self.assertEqual(report["profile_status"], "pass")

    def test_research_max_uses_maximum_preservation(self):
        prompt = (
            "Necesito investigacion profunda con evidencia, riesgos, restricciones, hipotesis, "
            "planificacion compleja y contexto completo. Sin sudo, sin API, no destructivo."
        )
        out_dir = self._run("test_profile_research_max", ["--text", prompt, "--profile", "research_max"])
        optimized = (out_dir / "optimized_prompt.txt").read_text(encoding="utf-8")
        semantic = json.loads((out_dir / "semantic_analysis.json").read_text(encoding="utf-8"))

        self.assertIn("RESEARCH_MAX Semantic Prompt", optimized)
        self.assertIn("ORIGINAL PROMPT PRESERVED", optimized)
        self.assertIn("maximum_preservation", semantic["style"])

    def test_auto_select_examples(self):
        examples = [
            ("Reescribe este texto de forma clara.", "FAST"),
            ("Implementa una app Python con CLI, tests, arquitectura y documentacion.", "ADVANCED"),
            ("Compara dos estrategias de negocio con riesgos, dinero, futuro y probabilidades.", "ROP"),
            (
                "Haz una investigacion extensa con evidencia, hipotesis, riesgos importantes, "
                "planificacion compleja, multiagente y muchas restricciones criticas.",
                "RESEARCH_MAX",
            ),
        ]
        for prompt, expected in examples:
            with self.subTest(expected=expected):
                semantics = extract_semantics(prompt)
                selected = auto_select_profile(prompt, semantics)
                self.assertEqual(selected["auto_selected_profile"], expected)

    def test_original_prompt_and_critical_constraints_are_preserved(self):
        prompt = "Crea una herramienta local. No uses sudo, sin API y no destructiva. Mantente dentro del proyecto."
        out_dir = self._run("test_profile_preservation", ["--text", prompt, "--profile", "standard"])
        hybrid = (out_dir / "hybrid_semantic_prompt.md").read_text(encoding="utf-8")
        nsl = (out_dir / "canonical_nsl.nsl").read_text(encoding="utf-8")

        self.assertIn(prompt, hybrid)
        self.assertIn("no_sudo", nsl)
        self.assertIn("no_external_api", nsl)
        self.assertIn("no_destructive_actions", nsl)
        self.assertIn("stay_inside_project_root", nsl)

    def test_sha256_and_hybrid_json_schema(self):
        prompt = "Organiza una lista de tareas para esta semana."
        out_dir = self._run("test_profile_hybrid_json", ["--text", prompt, "--profile", "standard"])
        hybrid = json.loads((out_dir / "hybrid_semantic_prompt.json").read_text(encoding="utf-8"))
        expected_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        self.assertEqual(hybrid["schema_version"], "NPSC-HYBRID/1.0")
        self.assertEqual(hybrid["source"]["raw_prompt"], prompt)
        self.assertEqual(hybrid["source"]["sha256"], expected_hash)
        self.assertIn("canonical_nsl", hybrid)
        self.assertIn("optimized_prompt", hybrid)
        self.assertIn("semantic_ir", hybrid)

    def test_constraint_aliases_are_normalized(self):
        normalized = normalize_constraints(["stay_inside_root", "no_api", "no_destructive"])
        self.assertIn("stay_inside_project_root", normalized)
        self.assertIn("no_external_api", normalized)
        self.assertIn("no_destructive_actions", normalized)

    def test_cli_accepts_profile_and_keeps_level_compatibility(self):
        profile_out = self._run("test_profile_cli_arg", ["--text", "Optimiza un prompt tecnico.", "--profile", "advanced"])
        self.assertTrue((profile_out / "profile_report.json").exists())

        level_out = self._run("test_profile_level_compat", ["--text", "Optimiza un prompt tecnico.", "--level", "all"])
        self.assertTrue((level_out / "canonical_nsl.nsl").exists())
        report = json.loads((level_out / "profile_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["applied_profile"], "STANDARD")

    def test_gui_compile_path_uses_core_nsl(self):
        result = compile_for_gui(
            "Compara una estrategia con riesgos, probabilidades y escenarios. Sin sudo.",
            target="codex",
            requested_profile="ROP",
            requested_level="profile_default",
        )
        self.assertIn("NSL/0.1", result["nsl"])
        self.assertNotIn("NSL-GUI/0.1", result["nsl"])
        self.assertIn("Hybrid Semantic Prompt", result["hybrid"])
        self.assertEqual(result["profile_status"]["applied_profile"], "ROP")

    def test_qt_gui_smoke_uses_core_offscreen(self):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        config_home = ROOT / "outputs" / f"test_qt_config_{os.getpid()}"
        data_home = ROOT / "outputs" / f"test_qt_data_{os.getpid()}"
        os.environ["NPSC_CONFIG_HOME"] = str(config_home)
        os.environ["NPSC_DATA_HOME"] = str(data_home)
        try:
            from PySide6.QtWidgets import QApplication
            from npsc_gui.main_window import MainWindow
        except ModuleNotFoundError as exc:
            self.skipTest(f"PySide6 no disponible en este interprete: {exc}")

        app = QApplication.instance() or QApplication([])
        window = MainWindow()
        profiles = [window.profile_combo.itemText(index) for index in range(window.profile_combo.count())]
        for profile in ["AUTO", "FAST", "STANDARD", "ADVANCED", "ROP", "RESEARCH_MAX"]:
            self.assertIn(profile, profiles)
        self.assertEqual(window.profile_combo.currentText(), "AUTO")
        self.assertFalse(window.windowIcon().isNull())
        self.assertFalse(window.profile_combo.toolTip())
        self.assertTrue(window.compile_button.toolTip())
        self.assertTrue(window.cancel_button.toolTip())
        expected_tabs = [
            "Resumen",
            "Prompt listo para usar",
            "Informe completo",
            "Prompt original",
            "Validación",
            "NSL compacto",
            "JSON para programas",
            "Reglas semánticas",
            "Restricciones y origen",
            "Perfil aplicado",
        ]
        actual_tabs = [window.tabs.tabText(index) for index in range(window.tabs.count())]
        self.assertEqual(actual_tabs, expected_tabs)
        self.assertTrue(all(not window.tabs.tabToolTip(index) for index in range(window.tabs.count())))
        self.assertFalse(window._current_mode == "extreme")
        # Default is simple mode; NSL compacto tab is only in extreme mode
        window._switch_to_mode("extreme")
        self.assertEqual(window.status_mode.text(), "Modo: Extremo")
        self.assertTrue(window.tabs.isTabVisible(actual_tabs.index("NSL compacto")))
        self.assertEqual(window._combo_value(window.level_combo), "profile_default")
        window.level_combo.setCurrentIndex(3)
        self.assertEqual(window._combo_value(window.level_combo), "aggressive")
        window.privacy_combo.setCurrentIndex(1)
        self.assertEqual(window._combo_value(window.privacy_combo), "hash_only")
        window.prompt_edit.setPlainText("Evalúa estrategia con riesgos y probabilidad. Sin sudo.")
        window.profile_combo.setCurrentText("ROP")
        window.compile_current()
        deadline = time.time() + 5
        while window.result is None and time.time() < deadline:
            app.processEvents()
            time.sleep(0.01)
        self.assertIsNotNone(window.result)
        self.assertFalse(window.cancel_button.isVisible() and window.cancel_button.isEnabled())
        self.assertIn("NSL/0.1", window.result["chosen_nsl"])
        self.assertNotIn("NSL-GUI/0.1", window.result["chosen_nsl"])
        self.assertIn("Hybrid Semantic Prompt", window.hybrid_text.toPlainText())
        self.assertIn("Reality_Oriented_Optimization_Engine".lower(), window.optimized_text.toPlainText().lower())
        window.copy_recommended()
        self.assertEqual(app.clipboard().text(), window.optimized_text.toPlainText())
        window.copy_json()
        self.assertIn("NPSC-HYBRID/1.0", app.clipboard().text())
        window.close()
        settings_file = config_home / "settings.json"
        self.assertTrue(settings_file.exists())
        settings_data = json.loads(settings_file.read_text(encoding="utf-8"))
        self.assertEqual(settings_data["theme"], "dark")
        self.assertTrue(settings_data["advanced_mode"])

    def test_fast_simple_prompt_has_no_internal_contamination_and_is_compact(self):
        prompt = "Corrige la ortografía de este correo."
        result = compile_prompt(CompileRequest(original=prompt, target="codex", profile="fast"))
        forbidden = {"extract_semantics", "map_seeds", "compile_nsl", "reconstruct_prompt", "verify_context_loss", "export_reports"}
        self.assertTrue(forbidden.isdisjoint(set(result["semantics"]["tasks"])))
        self.assertLessEqual(result["context_loss_report"]["expansion_ratio_execution_prompt"], 1.2)
        self.assertEqual(result["context_loss_report"]["profile_status"], "pass")

    def test_hash_only_privacy_removes_sensitive_text_from_serialized_outputs(self):
        sensitive = "Texto sensible secreto 12345. Corrige este texto."
        result = compile_prompt(CompileRequest(original=sensitive, target="codex", profile="auto", privacy_mode="hash_only", preserve_original=False))
        serialized = json.dumps(
            {
                "hybrid_json": result["hybrid_json"],
                "semantic_ir": result["semantic_ir"],
                "markdown": result["hybrid_markdown"],
                "nsl": result["chosen_nsl"],
                "execution": result["optimized_prompt"],
                "semantics": result["semantics"],
                "public_result_original": result["original"],
            },
            ensure_ascii=False,
        )
        self.assertNotIn("Texto sensible secreto 12345", serialized)
        self.assertNotIn("Corrige este texto", serialized)
        self.assertEqual(result["semantic_ir"]["source"]["privacy_mode"], "hash_only")

    def test_seed_dictionary_has_minimum_validated_size(self):
        report = validate_semantic_dictionary()
        self.assertTrue(report["valid"], report)
        self.assertGreaterEqual(report["count"], 150)

    def test_new_artifacts_and_custom_model_name(self):
        prompt = "Redacta un correo breve para confirmar una reunión."
        out_dir = self._run("test_custom_model_artifacts", [
            "--text", prompt,
            "--profile", "standard",
            "--target", "custom",
            "--custom-model-name", "MiModeloLocal-7B",
        ])
        for name in ["canonical_nsl.nsl", "optimized_prompt.txt", "hybrid_semantic_prompt.md", "hybrid_semantic_prompt.json"]:
            self.assertTrue((out_dir / name).exists(), name)
        data = json.loads((out_dir / "semantic_ir.json").read_text(encoding="utf-8"))
        self.assertEqual(data["target_adapter_layer"]["model_name"], "MiModeloLocal-7B")


if __name__ == "__main__":
    unittest.main()
