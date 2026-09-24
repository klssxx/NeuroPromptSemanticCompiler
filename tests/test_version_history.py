"""Tests for version_history.py.

P1-4 addition: field-level round-trip serialisation test.
Verifies that every field written by save_version is recoverable with its
exact value after a full JSON round-trip — not just that the count matches.
"""
from __future__ import annotations

import json
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from version_history import VersionHistory


@pytest.fixture()
def history(tmp_path):
    return VersionHistory(storage_dir=tmp_path)


class TestVersionHistoryBasic:
    def test_empty_on_init(self, history):
        assert history.list_versions() == []

    def test_save_and_list(self, history):
        history.save_version("prompt A", "result A", profile="STANDARD", target="codex")
        versions = history.list_versions()
        assert len(versions) == 1

    def test_multiple_versions_ordered(self, history):
        for i in range(3):
            history.save_version(f"prompt {i}", f"result {i}", profile="STANDARD", target="codex")
        versions = history.list_versions()
        assert len(versions) == 3

    def test_get_version_returns_correct_data(self, history):
        history.save_version("my prompt", "my result", profile="STANDARD", target="codex")
        versions = history.list_versions()
        version_id = versions[0]["id"]
        entry = history.get_version(version_id)
        assert entry is not None
        assert entry["original"] == "my prompt"


class TestVersionHistoryRoundTrip:
    """P1-4: field-level serialisation round-trip.

    Rationale: the previous test only asserted count == 1 after persistence.
    That would miss bugs where a field is silently dropped or coerced during
    JSON serialisation (e.g. int -> string, list -> None).
    """

    _FIELDS = {
        "original": "Write a FastAPI endpoint that streams a file download.",
        "result": "[compiled] FastAPI streaming endpoint with Range header support.",
        "profile": "ADVANCED",
        "target": "codex",
    }

    def test_all_fields_survive_round_trip(self, history):
        history.save_version(**self._FIELDS)
        versions = history.list_versions()
        assert len(versions) == 1, "Expected exactly one saved version."
        vid = versions[0]["id"]
        entry = history.get_version(vid)
        assert entry is not None, "get_version returned None after save."
        for field, expected in self._FIELDS.items():
            assert field in entry, f"Field '{field}' missing after round-trip."
            assert entry[field] == expected, (
                f"Field '{field}' corrupted: expected {expected!r}, got {entry[field]!r}"
            )

    def test_id_and_timestamp_stable_across_reload(self, tmp_path):
        """Re-instantiating VersionHistory from the same dir must yield identical id/timestamp."""
        h1 = VersionHistory(storage_dir=tmp_path)
        h1.save_version(**self._FIELDS)
        v1 = h1.list_versions()[0]

        h2 = VersionHistory(storage_dir=tmp_path)
        v2 = h2.list_versions()[0]

        assert v1["id"] == v2["id"], "Version id changed after reload."
        assert v1.get("timestamp") == v2.get("timestamp"), "Timestamp changed after reload."

    def test_serialised_file_is_valid_json(self, tmp_path):
        """The on-disk representation must be parseable JSON with no extra encoding."""
        h = VersionHistory(storage_dir=tmp_path)
        h.save_version(**self._FIELDS)
        json_files = list(tmp_path.rglob("*.json"))
        assert json_files, "No JSON file written by VersionHistory."
        for jf in json_files:
            content = jf.read_text(encoding="utf-8")
            parsed = json.loads(content)  # raises if invalid
            assert isinstance(parsed, (dict, list))
