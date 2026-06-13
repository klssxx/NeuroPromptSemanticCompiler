# Distribución Ubuntu y Linux

## Desde código fuente

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./run_gui.sh
```

## Validación

```bash
./verify_app.sh
bash tools/verify_project.sh
```

## AppStream y desktop

Archivos preparados:

- `packaging/desktop/neuro-prompt-semantic-compiler.desktop`
- `packaging/appstream/io.github.npsc.NeuroPromptSemanticCompiler.metainfo.xml`

## Instalación local sin sudo

```bash
bash tools/install_local_user.sh
```

Valida Python, PySide6, copia la aplicación a rutas XDG del usuario, crea wrappers `npsc` y `npsc-gui`, instala icono y `.desktop` local.

Desinstalación:

```bash
bash tools/uninstall_local_user.sh
```

## Debian

`tools/build_release.sh` construye un `.deb` mínimo con `dpkg-deb` si la herramienta existe:

```text
dist/neuroprompt-semantic-compiler_1.0.0rc1_all.deb
```

Validado sin instalar:

```bash
dpkg-deb -I dist/neuroprompt-semantic-compiler_1.0.0rc1_all.deb
dpkg-deb -c dist/neuroprompt-semantic-compiler_1.0.0rc1_all.deb
```

El paquete declara solo `python3` como dependencia porque PySide6 puede venir de entorno local, pip o paquete de distribución según Ubuntu/Kubuntu. Antes de publicar un `.deb` final conviene decidir una política de dependencias Debian real.

El `.desktop` instalable usa:

```text
Exec=npsc-gui
```

El launcher local de desarrollo sigue siendo:

```bash
./run_gui.sh
```

## Wheel

El wheel se valida fuera del repositorio instalando en `/tmp` con `--target`. Los recursos se resuelven mediante `importlib.resources`.
