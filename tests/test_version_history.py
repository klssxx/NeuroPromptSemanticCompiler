"""Tests for version_history.py.

Coverage lineage (A.6 integrity audit):
- Restored: the real-API coverage the historical suite asserted
  (create_version, list_all, get, delete, persistence across reload,
  compute_diff / compute_unified_diff). The PR had replaced it with tests
  for a dict-based API (save_version/list_versions/get_version returning
  dicts) that no implementation ever provided.
- Kept from the PR (P1-4 intent, adapted to the real PromptVersion API):
  field-level JSON round-trip integrity, id/created_at stability across
  reload, and valid-JSON on disk.
"""
from __future__ import annotations

import json
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from version_history import VersionHistory, compute_diff, compute_unified_diff


@pytest.fixture()
def history(tmp_path):
    return VersionHistory(storage_dir=tmp_path)


class TestVersionHistoryBasic:
    def test_empty_on_init(self, history):
        assert history.list_all() == []
        assert history.count() == 0

    def test_create_version(self, history):
        ver = history.create_version(name="Test", content="Hello world")
        assert ver.id
        assert ver.name == "Test"
        assert history.count() == 1

    def test_list_all_after_saves(self, history):
        for i in range(3):
            history.create_version(name=f"V{i}", content=f"Content {i}")
        versions = history.list_all()
        assert len(versions) == 3

    def test_get_version_returns_correct_data(self, history):
        ver = history.create_version(
            name="my prompt",
            content="my result",
            informal_input="my prompt",
            profile="STANDARD",
            target="codex",
        )
        entry = history.get(ver.id)
        assert entry is not None
        assert entry.informal_input == "my prompt"
        assert entry.content == "my result"

    def test_delete_version(self, history):
        ver = history.create_version(name="ToDelete", content="Bye")
        assert history.delete(ver.id) is True
        assert history.count() == 0

    def test_persistence_across_reload(self, tmp_path):
        h1 = VersionHistory(storage_dir=tmp_path)
        h1.create_version(name="Persist", content="Data")
        h2 = VersionHistory(storage_dir=tmp_path)
        assert h2.count() == 1


class TestVersionHistoryRoundTrip:
    """P1-4: field-level serialisation round-trip.

    Rationale: a count-only assertion would miss bugs where a field is
    silently dropped or coerced during JSON serialisation (int -> string,
    list -> None, etc.). Every field written by create_version must come
    back with its exact value after persistence + reload.
    """

    _KWARGS = {
        "name": "Write a FastAPI endpoint that streams a file download.",
        "content": "[compiled] FastAPI streaming endpoint with Range header support.",
        "informal_input": "hazme un endpoint que descargue ficheros",
        "target": "codex",
        "profile": "ADVANCED",
        "level": "safe",
        "notes": "round-trip probe",
        "variables_used": {"endpoint": "/download"},
        "template_id": "tpl-probe",
    }

    def test_all_fields_survive_round_trip(self, tmp_path):
        h1 = VersionHistory(storage_dir=tmp_path)
        ver = h1.create_version(**self._KWARGS)

        h2 = VersionHistory(storage_dir=tmp_path)
        reloaded = h2.get(ver.id)
        assert reloaded is not None, "get() returned None after reload."
        for field_name, expected in self._KWARGS.items():
            got = getattr(reloaded, field_name, None)
            assert got == expected, (
                f"Field '{field_name}' corrupted by round-trip: "
                f"expected {expected!r}, got {got!r}"
            )

    def test_id_and_timestamp_stable_across_reload(self, tmp_path):
        h1 = VersionHistory(storage_dir=tmp_path)
        ver = h1.create_version(name="stable", content="stable body")
        v1 = h1.list_all()[0]

        h2 = VersionHistory(storage_dir=tmp_path)
        v2 = h2.list_all()[0]

        assert v1.id == v2.id, "Version id changed after reload."
        assert v1.created_at == v2.created_at, "created_at changed after reload."

    def test_serialised_files_are_valid_json(self, tmp_path):
        h = VersionHistory(storage_dir=tmp_path)
        h.create_version(name="json probe", content="body")
        json_files = list(tmp_path.rglob("*.json"))
        assert json_files, "No JSON file written by VersionHistory."
        for jf in json_files:
            parsed = json.loads(jf.read_text(encoding="utf-8"))  # raises if invalid
            assert isinstance(parsed, (dict, list))


class DiffTests:
    def test_compute_diff_additions(self):
        result = compute_diff("line1\nline2", "line1\nline2\nline3")
        assert result["added"] == ["line3"]
        assert result["removed"] == []

    def test_compute_diff_removals(self):
        result = compute_diff("line1\nline2\nline3", "line1\nline3")
        assert result["removed"] == ["line2"]

    def test_compute_diff_identical(self):
        result = compute_diff("same\nsame", "same\nsame")
        assert result["added"] == []
        assert result["removed"] == []

    def test_unified_diff_output(self):
        diff = compute_unified_diff("a\nb", "a\nc", old_label="v1", new_label="v2")
        assert isinstance(diff, str)
        assert "-b" in diff and "+c" in diff
