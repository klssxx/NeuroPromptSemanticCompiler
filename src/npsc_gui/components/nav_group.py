"""Nav group — sidebar navigation group with label and items."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QFrame, QVBoxLayout, QWidget


class NavItem(QPushButton):
    """Single navigation item in sidebar."""

    clicked_page = Signal(str)

    def __init__(self, page_id: str, text: str = "", parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName("NPSCNavItem")
        self.setProperty("nav", "true")
        self.setCheckable(True)
        self._page_id = page_id
        self.clicked.connect(lambda _checked=False: self.clicked_page.emit(self._page_id))

    @property
    def page_id(self) -> str:
        return self._page_id


class NavGroup(QFrame):
    """Group of NavItems with an uppercase label."""

    def __init__(self, label: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("NPSCNavGroup")
        self._items: list[NavItem] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if label:
            lbl = QLabel(label)
            lbl.setObjectName("NavGroupLabel")
            layout.addWidget(lbl)

        self._layout = layout

    def add_item(self, page_id: str, text: str) -> NavItem:
        item = NavItem(page_id, text)
        self._items.append(item)
        self._layout.addWidget(item)
        return item

    @property
    def items(self) -> list[NavItem]:
        return list(self._items)
