🌐 **Language:** [English](LINUX_INSTALL.md) · [Español](LINUX_INSTALL.es.md)

# Instalación y notas de ejecución en Linux

NeuroPrompt Semantic Compiler es una aplicación de escritorio Python 3.10+ y PySide6/Qt 6. La opción portátil recomendada es usar un entorno virtual local dentro del proyecto.

## Configuración universal recomendada

```bash
cd NeuroPromptSemanticCompiler
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements.txt
./run_gui.sh
```

Si tu distribución bloquea instalaciones globales de Python por PEP 668, sigue usando `.venv` en vez de instalar paquetes globalmente.

## Notas por distribución

### Ubuntu, Xubuntu, Kubuntu, Debian

Recomendado: usa `.venv` como arriba.

Si prefieres paquetes de la distribución, los nombres pueden variar según la versión:

```bash
sudo apt install python3 python3-venv python3-pip
# Bindings Qt de sistema opcionales cuando estén disponibles:
sudo apt install python3-pyside6.qtwidgets python3-pyside6.qtsvg
```

### Fedora

```bash
sudo dnf install python3 python3-pip
# Bindings Qt de sistema opcionales:
sudo dnf install python3-pyside6
```

### Arch, CachyOS, Manjaro

```bash
sudo pacman -S python python-pip
# Bindings Qt de sistema opcionales:
sudo pacman -S pyside6
```

### Otras distribuciones

Usa Python 3.10+ e instala `PySide6>=6.11` dentro de `.venv`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Launchers de escritorio

Para instalar un launcher local de usuario sin sudo:

```bash
bash tools/install_local_user.sh
```

Los metadatos del launcher son compatibles con XDG y usan el icono `neuro-prompt-semantic-compiler`.

## Comprobaciones de ejecución

```bash
bash tools/check_runtime.sh
QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

## GPUs antiguas y escritorios ligeros

La GUI usa Qt Widgets nativos y evita Electron/web views. Está pensada para ser suficientemente ligera en GPUs antiguas y sesiones X11. Si una sesión Wayland tiene problemas con plugins Qt, prueba desde una sesión X11 o con los paquetes Qt recomendados por tu distribución.

## Sin sudo para uso normal

El desarrollo normal, CLI, GUI e instalación local del launcher no requieren sudo. Sudo solo hace falta si decides instalar paquetes de distribución con `apt`, `dnf` o `pacman`.
