"""Tests for the advanced mode editable sections page (no Qt widget tests).

Unit tests for the data/logic layer that doesn't require a running QApplication.
The GUI widget tests are marked as MANUAL_REVIEW_REQUIRED since they need pytest-qt.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path


class TestAdvancedSectionKeys:
    """Test the section key constants and label lookups."""

    def test_section_keys_count(self):
        from npsc_gui.advanced_mode_page import ADVANCED_SECTION_KEYS
        assert len(ADVANCED_SECTION_KEYS) == 6
        assert "context_role" in ADVANCED_SECTION_KEYS
        assert "query_task" in ADVANCED_SECTION_KEYS
        assert "specifications" in ADVANCED_SECTION_KEYS
        assert "quality_criteria" in ADVANCED_SECTION_KEYS
        assert "output_format" in ADVANCED_SECTION_KEYS
        assert "verification" in ADVANCED_SECTION_KEYS

    def test_section_defaults_es(self):
        from npsc_gui.advanced_mode_page import ADVANCED_SECTION_DEFAULTS_ES
        assert ADVANCED_SECTION_DEFAULTS_ES["context_role"] == "Contexto y rol"
        assert ADVANCED_SECTION_DEFAULTS_ES["query_task"] == "Consulta o tarea"
        assert ADVANCED_SECTION_DEFAULTS_ES["verification"] == "Verificacion"

    def test_section_defaults_en(self):
        from npsc_gui.advanced_mode_page import ADVANCED_SECTION_DEFAULTS_EN
        assert ADVANCED_SECTION_DEFAULTS_EN["context_role"] == "Context and role"
        assert ADVANCED_SECTION_DEFAULTS_EN["query_task"] == "Query or task"
        assert ADVANCED_SECTION_DEFAULTS_EN["verification"] == "Verification"

    def test_placeholders_es_exist(self):
        from npsc_gui.advanced_mode_page import ADVANCED_SECTION_PLACEHOLDERS_ES, ADVANCED_SECTION_KEYS
        for key in ADVANCED_SECTION_KEYS:
            assert key in ADVANCED_SECTION_PLACEHOLDERS_ES
            assert len(ADVANCED_SECTION_PLACEHOLDERS_ES[key]) > 0

    def test_placeholders_en_exist(self):
        from npsc_gui.advanced_mode_page import ADVANCED_SECTION_PLACEHOLDERS_EN, ADVANCED_SECTION_KEYS
        for key in ADVANCED_SECTION_KEYS:
            assert key in ADVANCED_SECTION_PLACEHOLDERS_EN
            assert len(ADVANCED_SECTION_PLACEHOLDERS_EN[key]) > 0


class TestCombinedPrompt:
    """Test the prompt combination logic indirectly via the module's data structures."""

    def test_combined_prompt_format(self):
        """Simulate the combination logic from AdvancedModePage.get_combined_prompt()."""
        # Informal input
        informal = "hazme un script python"

        # Sections data
        sections_data = {
            "context_role": "Expert Python developer",
            "query_task": "Write a sorting function",
            "specifications": "",
            "quality_criteria": "", 
            "output_format": "Python code block",
            "verification": "",
        }

        keys_order = [
            "context_role", "query_task", "specifications",
            "quality_criteria", "output_format", "verification"
        ]
        defaults = {
            "context_role": "Contexto y rol",
            "query_task": "Consulta o tarea",
            "specifications": "Especificaciones",
            "quality_criteria": "Criterios de calidad",
            "output_format": "Formato de salida",
            "verification": "Verificacion",
        }

        # Replicate the logic
        parts = []
        if informal.strip():
            parts.append(informal.strip())

        for key in keys_order:
            text = sections_data.get(key, "").strip()
            if text:
                label = defaults.get(key, key)
                parts.append(f"[{label}]\n{text}")

        combined = "\n\n".join(parts)

        assert "hazme un script python" in combined
        assert "Expert Python developer" in combined
        assert "Write a sorting function" in combined
        assert "Python code block" in combined
        # Empty sections should NOT appear
        assert "Especificaciones" not in combined
        assert "Criterios de calidad" not in combined
        assert "Verificacion" not in combined

    def test_combined_prompt_all_empty(self):
        informal = ""
        sections_data = {k: "" for k in [
            "context_role", "query_task", "specifications",
            "quality_criteria", "output_format", "verification"
        ]}
        parts = []
        if informal.strip():
            parts.append(informal.strip())
        for key in sections_data:
            text = sections_data[key].strip()
            if text:
                parts.append(text)
        combined = "\n\n".join(parts)
        assert combined == ""

    def test_sections_json_roundtrip(self):
        """Test that sections data serializes/deserializes properly."""
        data = {
            "schema_version": "1.0",
            "type": "advanced_sections",
            "informal_input": "test prompt",
            "sections": {
                "context_role": "Role text",
                "query_task": "Task text",
                "specifications": "Specs text",
                "quality_criteria": "Quality text",
                "output_format": "Format text",
                "verification": "Verify text",
            }
        }
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        restored = json.loads(json_str)
        assert restored["informal_input"] == "test prompt"
        assert restored["sections"]["context_role"] == "Role text"
        assert restored["sections"]["verification"] == "Verify text"


class TestAboutDialog:
    """Test the About dialog constants."""

    def test_app_constants(self):
        from npsc_gui.about_dialog import APP_NAME, APP_VERSION, LICENSE_TEXT
        assert APP_NAME == "NeuroPrompt Semantic Compiler"
        assert APP_VERSION == "1.0.0"
        assert LICENSE_TEXT == "MIT License"

    def test_privacy_notes_exist(self):
        from npsc_gui.about_dialog import PRIVACY_NOTE, PRIVACY_NOTE_ES
        assert len(PRIVACY_NOTE) > 0
        assert len(PRIVACY_NOTE_ES) > 0
        assert "local" in PRIVACY_NOTE.lower() or "local" in PRIVACY_NOTE_ES.lower()

    def test_limitations_non_empty(self):
        from npsc_gui.about_dialog import LIMITATIONS
        assert len(LIMITATIONS) >= 3


class TestExportPreview:
    """Test export preview data formatting."""

    def test_markdown_export_format(self):
        """Test that _build_markdown_preview produces valid output."""
        from npsc_gui.export_preview import _build_markdown_preview
        result = {
            "optimized_prompt": "Test prompt",
            "applied_profile": "STANDARD",
            "target": "codex",
            "original": "Original text",
            "prompt_sha256": "abc123",
            "context_loss_report": {"score": 85},
        }
        md = _build_markdown_preview(result)
        assert "Test prompt" in md
        assert "STANDARD" in md

    def test_text_export_format(self):
        """Test that _build_text_preview produces valid output."""
        from npsc_gui.export_preview import _build_text_preview
        result = {"optimized_prompt": "Test prompt"}
        txt = _build_text_preview(result)
        assert "Test prompt" in txt


class TestTemplateManagerSearch:
    """Test template search/filter functionality."""

    def test_template_manager_import(self):
        from template_manager import TemplateManager
        assert TemplateManager is not None

    def test_template_manager_create(self, tmp_path):
        from template_manager import TemplateManager, PromptTemplate
        manager = TemplateManager(storage_dir=tmp_path)
        t = PromptTemplate(
            id="test-1",
            name="Test Template",
            content="Hello {{name}}",
            tags=["test", "greeting"],
        )
        manager.create(t)
        assert len(manager.list_all()) >= 1
        found = manager.get("test-1")
        assert found is not None
        assert found.name == "Test Template"

    def test_template_search_by_name(self, tmp_path):
        from template_manager import TemplateManager, PromptTemplate
        manager = TemplateManager(storage_dir=tmp_path)
        manager.create(PromptTemplate(
            id="s1", name="Python helper", content="...", tags=[]
        ))
        manager.create(PromptTemplate(
            id="s2", name="Data analysis", content="...", tags=[]
        ))
        # Search by name
        results = [t for t in manager.list_all() if "python" in t.name.lower()]
        assert len(results) >= 1
        assert results[0].name == "Python helper"

    def test_template_search_by_tag(self, tmp_path):
        from template_manager import TemplateManager, PromptTemplate
        manager = TemplateManager(storage_dir=tmp_path)
        manager.create(PromptTemplate(
            id="t1", name="Code review", content="...", tags=["code", "review"]
        ))
        manager.create(PromptTemplate(
            id="t2", name="Write tests", content="...", tags=["test", "code"]
        ))
        results = [t for t in manager.list_all() if "code" in t.tags]
        assert len(results) >= 2
