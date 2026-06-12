from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication


ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "assets" / "icons" / "neuro-prompt-semantic-compiler.svg"
SIZES = [16, 32, 48, 64, 128, 256, 512]


def main() -> int:
    app = QApplication.instance() or QApplication([])
    renderer = QSvgRenderer(str(SVG))
    if not renderer.isValid():
        print(f"SVG no valido: {SVG}", file=sys.stderr)
        return 1
    for size in SIZES:
        image = QImage(QSize(size, size), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        out = SVG.with_name(f"neuro-prompt-semantic-compiler-{size}.png")
        image.save(str(out))
        print(out)
    app.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
