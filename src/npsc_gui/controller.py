from __future__ import annotations

from pathlib import Path
from typing import Any

from npsc_service import CompileRequest, compile_prompt, export_artifacts


class CompileController:
    def __init__(self) -> None:
        self.last_result: dict[str, Any] | None = None
        self.last_output_dir: Path | None = None

    def compile(
        self,
        *,
        prompt: str,
        target: str,
        profile: str,
        level: str,
        strict: bool,
        preserve_original: bool,
        privacy_mode: str = "full_original",
        custom_model_name: str = "",
    ) -> dict[str, Any]:
        request = CompileRequest(
            original=prompt,
            target=target,
            profile=profile,
            level=None if level == "profile_default" else level,
            strict=strict,
            preserve_original=preserve_original,
            privacy_mode=privacy_mode,
            custom_model_name=custom_model_name,
        )
        self.last_result = compile_prompt(request)
        return self.last_result

    def save_all(self, out_dir: str | Path) -> list[str]:
        if not self.last_result:
            raise ValueError("No hay resultado para guardar.")
        self.last_output_dir = Path(out_dir)
        return export_artifacts(self.last_result, self.last_output_dir)
