"""Tests for version_history.py.

P1 fix: test_persistence now validates serialised content, not just count.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from version_history import VersionHistory


_PROMPT_A = "Analyse the request pipeline and optimise for latency."
_PROMPT_B = "Refactor the database layer to use connection pooling."
_PROMPT_C = "Add input validation to all public API endpoints."


@pytest.fixture()
def tmp_history_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


class TestVersionHistoryPersistence:
    """P1 fix — test_persistence: verify serialised content, not just count."""

    def test_save_and_reload_preserves_entry_count(self, tmp_history_file: Path):
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.add(_PROMPT_A)
        vh.add(_PROMPT_B)
        vh.save()

        reloaded = VersionHistory(storage_path=tmp_history_file)
        reloaded.load()
        assert len(reloaded.entries) == 2

    def test_save_and_reload_preserves_prompt_text(self, tmp_history_file: Path):
        """Core invariant: reloaded entries must match originals exactly."""
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.add(_PROMPT_A)
        vh.add(_PROMPT_B)
        vh.save()

        reloaded = VersionHistory(storage_path=tmp_history_file)
        reloaded.load()
        texts = [e.prompt if hasattr(e, "prompt") else e.get("prompt", e) for e in reloaded.entries]
        assert _PROMPT_A in texts
        assert _PROMPT_B in texts

    def test_serialised_file_is_valid_json(self, tmp_history_file: Path):
        """The persisted file must be deserializable JSON."""
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.add(_PROMPT_A)
        vh.save()
        raw = tmp_history_file.read_text(encoding="utf-8")
        parsed = json.loads(raw)  # raises if invalid
        assert parsed  # non-empty

    def test_entry_fields_survive_roundtrip(self, tmp_history_file: Path):
        """Each entry must expose at least a prompt/text field after reload."""
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.add(_PROMPT_C)
        vh.save()

        reloaded = VersionHistory(storage_path=tmp_history_file)
        reloaded.load()
        entry = reloaded.entries[0]
        # Accept both dataclass (entry.prompt) and dict (entry['prompt']) shapes.
        text = entry.prompt if hasattr(entry, "prompt") else entry.get("prompt", entry)
        assert _PROMPT_C in str(text)

    def test_save_without_load_does_not_corrupt(self, tmp_history_file: Path):
        vh1 = VersionHistory(storage_path=tmp_history_file)
        vh1.add(_PROMPT_A)
        vh1.save()

        vh2 = VersionHistory(storage_path=tmp_history_file)
        vh2.load()
        vh2.add(_PROMPT_B)
        vh2.save()

        vh3 = VersionHistory(storage_path=tmp_history_file)
        vh3.load()
        assert len(vh3.entries) == 2

    def test_reload_without_save_returns_empty(self, tmp_history_file: Path):
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.load()  # file does not exist yet
        assert vh.entries == []


class TestVersionHistoryDelete:
    def test_delete_removes_entry(self, tmp_history_file: Path):
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.add(_PROMPT_A)
        vh.add(_PROMPT_B)
        initial_count = len(vh.entries)
        vh.delete(0)
        assert len(vh.entries) == initial_count - 1

    def test_delete_removes_correct_entry(self, tmp_history_file: Path):
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.add(_PROMPT_A)
        vh.add(_PROMPT_B)
        vh.delete(0)
        remaining_texts = [
            e.prompt if hasattr(e, "prompt") else e.get("prompt", e)
            for e in vh.entries
        ]
        assert _PROMPT_A not in remaining_texts
        assert _PROMPT_B in remaining_texts

    def test_delete_out_of_range_raises_or_noops(self, tmp_history_file: Path):
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.add(_PROMPT_A)
        try:
            vh.delete(99)
        except (IndexError, ValueError):
            pass  # Both behaviours are acceptable — must not silently corrupt state.
        assert len(vh.entries) <= 1


class TestVersionHistoryClear:
    def test_clear_empties_entries(self, tmp_history_file: Path):
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.add(_PROMPT_A)
        vh.add(_PROMPT_B)
        vh.clear()
        assert vh.entries == []

    def test_clear_and_save_persists_empty_state(self, tmp_history_file: Path):
        vh = VersionHistory(storage_path=tmp_history_file)
        vh.add(_PROMPT_A)
        vh.save()
        vh.clear()
        vh.save()
        reloaded = VersionHistory(storage_path=tmp_history_file)
        reloaded.load()
        assert reloaded.entries == []
