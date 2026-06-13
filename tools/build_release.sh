#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

VERSION="$($PYTHON - <<'PY'
import tomllib
from pathlib import Path
data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
print(data["project"]["version"])
PY
)"
NAME="neuro-prompt-semantic-compiler-${VERSION}"
STAGING_ROOT="staging/release"
STAGING="${STAGING_ROOT}/${NAME}"
ARCHIVE="dist/${NAME}.tar.gz"
WHEEL_DIR="dist"
DEB_STAGING="staging/debian/neuroprompt-semantic-compiler"
DEB_PATH="dist/neuroprompt-semantic-compiler_${VERSION}_all.deb"
BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
export PIP_CACHE_DIR="$ROOT/staging/pip-cache"
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_NO_INPUT=1

mkdir -p dist "$STAGING_ROOT" staging/debian

"$PYTHON" - <<'PY'
from pathlib import Path

patterns = [
    "neuro-prompt-semantic-compiler-*.tar.gz",
    "neuroprompt_semantic_compiler-*.whl",
    "neuroprompt-semantic-compiler_*_all.deb",
    "SHA256SUMS",
    "RELEASE_MANIFEST.md",
]
for pattern in patterns:
    for path in Path("dist").glob(pattern):
        if path.is_file():
            path.unlink()
PY

PYTHONPATH="$ROOT/src" "$PYTHON" -m compileall -q src app tests
PYTHONPATH="$ROOT/src" "$PYTHON" tools/generate_glossary_docs.py >/dev/null
QT_QPA_PLATFORM=offscreen PYTHONPATH="$ROOT/src" "$PYTHON" -m unittest discover -s tests -v

"$PYTHON" - <<'PY'
import os
import shutil
from pathlib import Path
import tomllib

root = Path.cwd()
version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
name = f"neuro-prompt-semantic-compiler-{version}"
staging = root / "staging" / "release" / name
if staging.exists():
    shutil.rmtree(staging)
staging.parent.mkdir(parents=True, exist_ok=True)

excluded_dirs = {
    ".venv",
    "dist",
    "backups",
    "_backups",
    "outputs",
    "artifacts",
    ".pytest_cache",
    "staging",
    "build",
}
excluded_suffixes = {".pyc", ".pyo"}
excluded_names = {".coverage"}

def ignore(path: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if any(part in excluded_dirs or part.endswith(".egg-info") or part == "__pycache__" for part in rel_parts):
        return True
    if path.name in excluded_names:
        return True
    if path.suffix in excluded_suffixes:
        return True
    return False

for current, dirs, files in os.walk(root):
    current_path = Path(current)
    dirs[:] = [d for d in dirs if not ignore(current_path / d)]
    for filename in files:
        source = current_path / filename
        if ignore(source):
            continue
        target = staging / source.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
print(staging)
PY

tar -C "$STAGING_ROOT" -czf "$ARCHIVE" "$NAME"

"$PYTHON" - <<'PY'
import tarfile
import tomllib
from pathlib import Path

version = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
archive = Path("dist") / f"neuro-prompt-semantic-compiler-{version}.tar.gz"
bad_markers = [
    "/.venv/",
    "/dist/",
    "/backups/",
    "/_backups/",
    "/outputs/",
    "/artifacts/",
    "/.pytest_cache/",
    ".egg-info/",
    "/__pycache__/",
    "/staging/",
    "/build/",
]
with tarfile.open(archive, "r:gz") as tf:
    names = tf.getnames()
    bad = [name for name in names if any(marker in f"/{name}/" for marker in bad_markers)]
    if bad:
        raise SystemExit("Release archive contains excluded paths: " + ", ".join(bad[:20]))
    if any(name.endswith(archive.name) for name in names):
        raise SystemExit("Release archive includes itself")
    required = [
        "pyproject.toml",
        "src/npsc_service.py",
        "src/npsc_gui/main_window.py",
        "src/npsc_gui/glossary.py",
        "src/npsc_resources/configs/ui_glossary_es.json",
        "docs/GLOSARIO_ES.md",
        "configs/compilation_profiles.json",
        "configs/model_profiles.json",
        "assets/icons/neuro-prompt-semantic-compiler.svg",
        "tests/test_compilation_profiles.py",
        "tools/install_local_user.sh",
    ]
    missing = [item for item in required if not any(name.endswith(item) for name in names)]
    if missing:
        raise SystemExit("Release archive missing required paths: " + ", ".join(missing))
print(f"Release source archive limpio: {archive}")
PY

WHEEL_STATUS="not_built"
BUILD_PYTHONPATH=""
if "$PYTHON" - <<'PY' >/dev/null 2>&1
import setuptools
PY
then
  BUILD_PYTHONPATH=""
elif python3 - <<'PY' >/dev/null 2>&1
import setuptools
PY
then
  BUILD_PYTHONPATH="/usr/lib/python3/dist-packages"
fi

if "$PYTHON" -m pip --version >/dev/null 2>&1 && [[ -n "$BUILD_PYTHONPATH" || "$("$PYTHON" - <<'PY'
import importlib.util
print("yes" if importlib.util.find_spec("setuptools") else "no")
PY
)" == "yes" ]]; then
  if [[ -n "$BUILD_PYTHONPATH" ]]; then
    PYTHONPATH="$BUILD_PYTHONPATH" "$PYTHON" -m pip wheel "$STAGING" --no-deps --no-build-isolation -w "$WHEEL_DIR"
  else
    "$PYTHON" -m pip wheel "$STAGING" --no-deps --no-build-isolation -w "$WHEEL_DIR"
  fi
  WHEEL_STATUS="built"
else
  echo "Wheel no construido: pip/setuptools no disponible en el entorno local." >&2
fi

DEB_STATUS="not_built"
if command -v dpkg-deb >/dev/null 2>&1; then
  "$PYTHON" - <<'PY'
import shutil
import tomllib
from pathlib import Path

root = Path.cwd()
version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
source = root / "staging" / "release" / f"neuro-prompt-semantic-compiler-{version}"
deb = root / "staging" / "debian" / "neuroprompt-semantic-compiler"
if deb.exists():
    shutil.rmtree(deb)
for generated in [source / "build", *source.glob("*.egg-info"), *source.glob("src/*.egg-info")]:
    if generated.exists():
        if generated.is_dir():
            shutil.rmtree(generated)
        else:
            generated.unlink()

app_dir = deb / "usr" / "share" / "neuro-prompt-semantic-compiler"
shutil.copytree(source, app_dir)

(deb / "DEBIAN").mkdir(parents=True, exist_ok=True)
(deb / "usr" / "bin").mkdir(parents=True, exist_ok=True)
(deb / "usr" / "share" / "applications").mkdir(parents=True, exist_ok=True)
(deb / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps").mkdir(parents=True, exist_ok=True)
(deb / "usr" / "share" / "metainfo").mkdir(parents=True, exist_ok=True)

(deb / "DEBIAN" / "control").write_text(f"""Package: neuroprompt-semantic-compiler
Version: {version}
Section: utils
Priority: optional
Architecture: all
Depends: python3
Maintainer: NeuroPrompt Team
Description: Offline semantic prompt compiler for local AI workflows
 NeuroPrompt Semantic Compiler improves human prompts, preserves intent,
 generates compact NSL, execution prompts and audit bundles.
""", encoding="utf-8")

(deb / "usr" / "bin" / "npsc").write_text("""#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/usr/share/neuro-prompt-semantic-compiler"
PYTHONPATH="$APP_DIR/src" exec python3 "$APP_DIR/src/npsc_cli.py" "$@"
""", encoding="utf-8")
(deb / "usr" / "bin" / "npsc-gui").write_text("""#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/usr/share/neuro-prompt-semantic-compiler"
PYTHONPATH="$APP_DIR/src" exec python3 -m npsc_gui.main "$@"
""", encoding="utf-8")
(deb / "usr" / "bin" / "npsc").chmod(0o755)
(deb / "usr" / "bin" / "npsc-gui").chmod(0o755)

shutil.copy2(root / "packaging" / "desktop" / "neuro-prompt-semantic-compiler.desktop", deb / "usr" / "share" / "applications" / "neuro-prompt-semantic-compiler.desktop")
shutil.copy2(root / "packaging" / "appstream" / "io.github.npsc.NeuroPromptSemanticCompiler.metainfo.xml", deb / "usr" / "share" / "metainfo" / "io.github.npsc.NeuroPromptSemanticCompiler.metainfo.xml")
shutil.copy2(root / "assets" / "icons" / "neuro-prompt-semantic-compiler.svg", deb / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps" / "neuro-prompt-semantic-compiler.svg")
PY
  dpkg-deb --build "$DEB_STAGING" "$DEB_PATH" >/dev/null
  dpkg-deb -I "$DEB_PATH" >/dev/null
  dpkg-deb -c "$DEB_PATH" >/dev/null
  DEB_STATUS="built"
else
  echo "DEB no construido: dpkg-deb no disponible." >&2
fi

"$PYTHON" - <<PY
from pathlib import Path

dist = Path("dist")
version = "$VERSION"
lines = [
    "# Release Manifest",
    "",
    f"Version: {version}",
    f"Fecha UTC: $BUILD_DATE",
    "",
    "## Artefactos",
]
for path in sorted(dist.iterdir()):
    if path.is_file() and path.name != "SHA256SUMS":
        lines.append(f"- {path.name} ({path.stat().st_size} bytes)")
lines.extend([
    "",
    "## Validaciones ejecutadas por build_release.sh",
    "- compileall src app tests",
    "- unittest discover tests",
    "- inspeccion tarball limpio",
    f"- wheel: $WHEEL_STATUS",
    f"- deb: $DEB_STATUS",
    "- SHA256SUMS generado tras el manifiesto, excluyendo solo el propio SHA256SUMS",
    "",
    "## Limitaciones",
    "- La instalacion de .deb no se ejecuta automaticamente porque requeriria permisos de sistema.",
    "- La GUI requiere PySide6 disponible en el entorno de ejecucion.",
])
(dist / "RELEASE_MANIFEST.md").write_text("\\n".join(lines) + "\\n", encoding="utf-8")
PY

find dist -maxdepth 1 -type f ! -name SHA256SUMS -exec sha256sum {} + | sort > dist/SHA256SUMS

echo "Release completada: $ARCHIVE"
echo "Wheel: $WHEEL_STATUS"
echo "DEB: $DEB_STATUS"
