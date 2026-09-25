"""B.9 tests: the desktop GUI exposes quality score and open questions.

Verified BY EXECUTION against the real MainWindow (offscreen) and the real
compile path (controller.compile → compile_prompt): the fields built in
B.2–B.6 must actually reach the on-screen widgets, not just the exported
JSON. Non-blocking by design: the questions tab is information, the
clarify mode keeps owning any gating behaviour.
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from npsc_gui.main_window import MainWindow

pytestmark = pytest.mark.usefixtures("qapp")


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


_WEAK = "Hazlo rápido pero muy detallado, con {{modulo}} sin rellenar."
_COMPLETE = (
    "Necesito una app local para gestionar notas con tests automáticos, sin sudo. "
    "Quiero el resultado para codex. Criterios de aceptación: abre sin conexión y los tests pasan."
)


def _compile_and_render(window: MainWindow, prompt: str):
    """Drive the REAL compile path the GUI uses, then the REAL render path."""
    result = window.controller.compile(
        prompt=prompt, target="codex", profile="STANDARD",
        level="profile_default", strict=False, preserve_original=True,
    )
    window.result = result
    window._render_result()  # production render path (worker-finished slot calls this)
    return result


class TestQualityScoreVisible:
    def test_quality_label_shows_score_and_counts(self, qapp):
        w = MainWindow()
        _compile_and_render(w, _WEAK)
        text = w.simple_quality_label.text()
        assert text.startswith("Calidad: "), text
        assert "/100" in text
        assert "errores" in text and "avisos" in text
        w.close()

    def test_quality_tooltip_lists_top_issues(self, qapp):
        w = MainWindow()
        _compile_and_render(w, _WEAK)
        tooltip = w.simple_quality_label.toolTip()
        issues = w.result["quality_report"]["issues"]
        assert issues, "weak input must produce issues"
        first = issues[0]
        assert first["message"][:30] in tooltip
        w.close()

    def test_clean_input_still_shows_quality(self, qapp):
        w = MainWindow()
        _compile_and_render(w, _COMPLETE)
        assert "Calidad: " in w.simple_quality_label.text()
        w.close()


class TestOpenQuestionsVisible:
    def test_questions_tab_lists_ambiguities(self, qapp):
        w = MainWindow()
        _compile_and_render(w, _WEAK)
        body = w.simple_questions_tab.toPlainText()
        # the weak input has an unfilled variable → B.2 ambiguity must surface
        assert "{{modulo}}" in body
        assert "1." in body  # numbered list
        assert "Preguntas abiertas (1" in w.simple_tabs.tabText(
            w.simple_tabs.indexOf(w.simple_questions_tab)
        ) or "Preguntas abiertas (" in w.simple_tabs.tabText(
            w.simple_tabs.indexOf(w.simple_questions_tab)
        )
        w.close()

    def test_questions_tab_come_from_clarification_gate_first(self, qapp):
        w = MainWindow()
        result = _compile_and_render(w, _WEAK)
        clar = result["clarification"]
        body = w.simple_questions_tab.toPlainText()
        if clar["questions"]:
            first_q = clar["questions"][0]
            assert first_q in body or first_q[:40] in body
        else:
            assert "Sin preguntas abiertas" in body
        w.close()

    def test_complete_input_shows_clean_state(self, qapp):
        w = MainWindow()
        _compile_and_render(w, _COMPLETE)
        body = w.simple_questions_tab.toPlainText()
        assert "Sin preguntas abiertas" in body
        tab_title = w.simple_tabs.tabText(w.simple_tabs.indexOf(w.simple_questions_tab))
        assert "✓" in tab_title
        w.close()

    def test_legacy_result_without_b2_fields_degrades_cleanly(self, qapp):
        """A pre-B.2 result shape must not crash the GUI render path."""
        w = MainWindow()
        legacy = {
            "optimized_prompt": "x", "hybrid_markdown": "y",
            "context_loss_markdown": "z", "context_loss_report": {"score": 50},
            "applied_profile": "STANDARD", "original": "t", "privacy_mode": "full_original",
            "profile_status": {}, "semantic_ir": {}, "hybrid_json": {}, "seeds": [],
            "requested_profile": "STANDARD", "prompt_sha256": "0" * 64,
            "chosen_nsl": "", "reconstructed": "",
        }
        w.result = legacy
        w._render_b9_fields(legacy)
        assert "Sin preguntas abiertas" in w.simple_questions_tab.toPlainText()
        assert w.simple_quality_label.text() == ""
        w.close()


class TestInitialFocus:
    def test_prompt_editor_has_keyboard_focus_after_activation(self, qapp):
        """Opening the app and typing must land in the prompt editor.

        Qt assigns initial focus when the window is ACTIVATED (async, after
        show); the watcher then claims the editor. Wait on the condition
        with a bounded timeout instead of a fixed sleep.
        """
        from PySide6.QtTest import QTest

        w = MainWindow()
        w.show()
        target_editor = w._current_editor()
        deadline_ok = False
        for _ in range(100):  # up to ~5 s; converges in a few hundred ms
            qapp.processEvents()
            QTest.qWait(50)
            if w.focusWidget() is target_editor:
                deadline_ok = True
                break
        assert deadline_ok, (
            f"focus ended on {type(w.focusWidget()).__name__!r}, not the prompt editor "
            f"(mode={w._current_mode!r})"
        )
        w.close()
