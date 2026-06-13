🌐 **Language:** [English](LINUX_INSTALL.md) · [Español](LINUX_INSTALL.es.md)

# Linux install and runtime notes

NeuroPrompt Semantic Compiler is a Python 3.10+ and PySide6/Qt 6 desktop application. The recommended portable setup is a project-local virtual environment.

## Recommended universal setup

```bash
cd NeuroPromptSemanticCompiler
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements.txt
./run_gui.sh
```

If your distribution blocks system-wide Python installs via PEP 668, keep using `.venv` instead of installing packages globally.

## Distribution notes

### Ubuntu, Xubuntu, Kubuntu, Debian

Recommended: use `.venv` as shown above.

If you prefer distro packages, names may vary by release:

```bash
sudo apt install python3 python3-venv python3-pip
# Optional system Qt bindings when available:
sudo apt install python3-pyside6.qtwidgets python3-pyside6.qtsvg
```

### Fedora

```bash
sudo dnf install python3 python3-pip
# Optional system Qt bindings:
sudo dnf install python3-pyside6
```

### Arch, CachyOS, Manjaro

```bash
sudo pacman -S python python-pip
# Optional system Qt bindings:
sudo pacman -S pyside6
```

### Other distributions

Use Python 3.10+ and install `PySide6>=6.11` inside `.venv`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Desktop launchers

For a user-local launcher without sudo:

```bash
bash tools/install_local_user.sh
```

The launcher metadata is XDG-compatible and uses the icon name `neuro-prompt-semantic-compiler`.

## Runtime checks

```bash
bash tools/check_runtime.sh
QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

## Legacy GPUs and low-power desktops

The GUI uses native Qt Widgets and avoids Electron/web views. It is intended to be light enough for old GPUs and X11 sessions. If a Wayland session has Qt plugin issues, try launching from an X11 session or with your distribution's recommended Qt platform packages.

## No sudo required for normal use

Normal development, CLI use, GUI use and local launcher installation do not require sudo. Sudo is only needed if you intentionally install distribution packages with `apt`, `dnf` or `pacman`.
