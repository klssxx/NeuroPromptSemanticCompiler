"""B.8 tests: GUI / service / CLI parity — verified by execution, not declared.

For the same input + target + profile (+ profile-default level), all three
entry points must agree on the semantic IR, the compiled artifacts, the
quality report and the four-layer separation. Volatile fields (run_id,
created_at) are excluded by design.
"""
from __future__ import annotations

import json
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from npsc_cli import run_cli
from npsc_service import CompileRequest, compile_prompt, compile_for_gui

_PROMPT = (
    "Necesito una app local para gestionar inventario, sin sudo, sin APIs externas. "
    "Quiero el resultado para codex. Criterios de aceptación: abre sin conexión y los tests pasan."
)

_SEMANTICS_FIELDS = (
    "goal", "tasks", "constraints", "priorities", "tools", "output", "style", "risks",
    "safety_constraints", "ambiguities", "contradictions", "assumptions", "confidence",
)


def _service_result():
    return compile_prompt(CompileRequest(original=_PROMPT, target="codex", profile="STANDARD"))


def _gui_result():
    return compile_for_gui(_PROMPT, target="codex", requested_profile="STANDARD",
                           requested_level="profile_default")


class TestServiceGuiParity:
    def test_semantics_identical(self):
        svc, gui = _service_result(), _gui_result()
        for field in _SEMANTICS_FIELDS:
            assert svc["semantics"][field] == gui["semantics"][field], f"semantics.{field} diverges"

    def test_compiled_artifacts_identical(self):
        svc, gui = _service_result(), _gui_result()

        def without_run_id(text: str) -> str:
            return "\n".join(line for line in text.splitlines() if not line.startswith("ID="))

        assert without_run_id(svc["chosen_nsl"]) == without_run_id(gui["nsl"]), "chosen NSL diverges"
        assert svc["optimized_prompt"] == gui["optimized"], "execution prompt diverges"
        # canonical aliases must point at the same objects (B.8 additive unification)
        assert gui["chosen_nsl"] == gui["nsl"]
        assert gui["optimized_prompt"] == gui["optimized"]

    def test_quality_report_identical(self):
        svc, gui = _service_result(), _gui_result()
        assert svc["quality_report"] == gui["quality_report"], "quality_report diverges"

    def test_four_layers_and_policy_identical(self):
        svc, gui = _service_result(), _gui_result()
        assert svc["four_layers"] == gui["four_layers"], "four_layers diverge"
        assert svc["policy_check"] == gui["policy_check"], "policy_check diverges"

    def test_profile_and_level_agree(self):
        svc, gui = _service_result(), _gui_result()
        assert svc["applied_profile"] == gui["applied_profile"]
        assert svc["chosen_level"] == gui["chosen_level"]
        assert svc["requested_profile"].upper() == gui["requested_profile"].upper()


class TestCliParity:
    def test_cli_routes_through_canonical_service(self):
        """CLI artifacts must be byte-identical to compile_prompt's for the same args."""
        svc = _service_result()
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "input.txt"
            out = Path(tmp) / "out"
            src.write_text(_PROMPT, encoding="utf-8")
            code = run_cli(["--input", str(src), "--out", str(out),
                            "--target", "codex", "--profile", "standard"])
            assert code == 0

            execution = (out / "optimized_prompt.txt").read_text(encoding="utf-8")
            nsl_file = (out / "canonical_nsl.nsl").read_text(encoding="utf-8")
            # IDs embedded in the NSL differ per run (trace metadata); everything else must match.
            def without_ids(text: str) -> str:
                return "\n".join(line for line in text.splitlines()
                                 if not line.startswith("ID=") and "run_id" not in line)
            assert without_ids(nsl_file) == without_ids(svc["chosen_nsl"]), "CLI NSL diverges from service"
            assert without_ids(execution) == without_ids(svc["optimized_prompt"]), \
                "CLI execution prompt diverges from service"

    def test_cli_audit_bundle_carries_extended_ir(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "input.txt"
            out = Path(tmp) / "out"
            src.write_text(_PROMPT, encoding="utf-8")
            run_cli(["--input", str(src), "--out", str(out),
                     "--target", "codex", "--profile", "standard"])
            bundle = json.loads((out / "hybrid_semantic_prompt.json").read_text(encoding="utf-8"))
            ir = bundle["audit_bundle"]["semantic_ir"]["semantic_ir"]
            assert ir["ambiguities"] == []
            assert isinstance(ir["confidence"], dict) and ir["confidence"]
