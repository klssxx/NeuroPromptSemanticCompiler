from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QTimer, Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QToolButton, QVBoxLayout, QWidget


_ACTIVE_POPOVERS: list["ContextHelpPopover"] = []


def close_context_help_popovers() -> None:
    for popover in list(_active_popovers_safe()):
        popover.hide_now()


def _active_popovers_safe() -> list["ContextHelpPopover"]:
    return [popover for popover in _ACTIVE_POPOVERS if popover is not None]


class ContextHelpPopover(QFrame):
    def __init__(
        self,
        title: str,
        body: str,
        parent: QWidget | None = None,
        action_label: str = "",
        action_callback=None,
    ) -> None:
        super().__init__(parent, Qt.ToolTip | Qt.FramelessWindowHint)
        self.setObjectName("ContextHelpPopover")
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setMaximumWidth(380)
        self.setMinimumWidth(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(7)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("ContextHelpTitle")
        self.title_label.setWordWrap(True)
        self.body_label = QLabel(body)
        self.body_label.setObjectName("ContextHelpBody")
        self.body_label.setWordWrap(True)
        self.body_label.setMaximumWidth(340)
        self.body_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(self.title_label)
        layout.addWidget(self.body_label)
        if action_label and action_callback:
            self.action_button = QToolButton(self)
            self.action_button.setText(action_label)
            self.action_button.setFocusPolicy(Qt.StrongFocus)
            self.action_button.clicked.connect(action_callback)
            layout.addWidget(self.action_button)
        _ACTIVE_POPOVERS.append(self)

    def show_near(self, anchor: QWidget) -> None:
        close_context_help_popovers()
        self.adjustSize()
        screen = QGuiApplication.screenAt(anchor.mapToGlobal(anchor.rect().center()))
        available = screen.availableGeometry() if screen else QGuiApplication.primaryScreen().availableGeometry()
        margin = 12
        below = anchor.mapToGlobal(QPoint(0, anchor.height() + 8))
        x = below.x()
        y = below.y()

        if x + self.width() + margin > available.right():
            x = available.right() - self.width() - margin
        if x < available.left() + margin:
            x = available.left() + margin
        if y + self.height() + margin > available.bottom():
            y = anchor.mapToGlobal(QPoint(0, -self.height() - 8)).y()
        if y < available.top() + margin:
            y = available.top() + margin

        self.move(x, y)
        self.show()

    def hide_now(self) -> None:
        self.hide()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.hide_now()
            event.accept()
            return
        super().keyPressEvent(event)


class ContextHelpButton(QToolButton):
    def __init__(
        self,
        title: str,
        body: str,
        parent: QWidget | None = None,
        glossary_id: str | None = None,
        glossary_callback=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("HelpIconButton")
        self.setText("?")
        self.setFixedSize(22, 22)
        self.setCursor(Qt.WhatsThisCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName(f"Ayuda contextual: {title}")
        self.setAccessibleDescription(body)
        self.setToolTip("")
        self.glossary_id = glossary_id
        action_callback = None
        if glossary_id and glossary_callback:
            action_callback = lambda: self._open_glossary(glossary_callback)
        self._popover = ContextHelpPopover(title, body, self.window(), "Ver en glosario", action_callback)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(180)
        self._hide_timer.timeout.connect(self._hide_if_unpinned)
        self._pinned = False
        self.clicked.connect(self._toggle_pinned)
        QApplication.instance().installEventFilter(self)

    @property
    def popover(self) -> ContextHelpPopover:
        return self._popover

    def _show(self) -> None:
        self._hide_timer.stop()
        self._popover.show_near(self)

    def _hide_if_unpinned(self) -> None:
        if not self._pinned:
            self._popover.hide_now()

    def _schedule_hide(self) -> None:
        self._hide_timer.start()

    def _toggle_pinned(self) -> None:
        self._pinned = not self._pinned
        if self._pinned:
            self._show()
        else:
            self._popover.hide_now()

    def _open_glossary(self, glossary_callback) -> None:
        self._pinned = False
        self._popover.hide_now()
        glossary_callback(self.glossary_id)

    def enterEvent(self, event) -> None:
        self._show()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._schedule_hide()
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self._show()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._pinned = False
        self._schedule_hide()
        super().focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self._pinned = False
            self._popover.hide_now()
            event.accept()
            return
        if event.key() in {Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space}:
            self._toggle_pinned()
            event.accept()
            return
        super().keyPressEvent(event)

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.MouseButtonPress and self._popover.isVisible():
            widget = QApplication.widgetAt(event.globalPosition().toPoint()) if hasattr(event, "globalPosition") else None
            if widget is not self and (widget is None or not self._popover.isAncestorOf(widget)):
                self._pinned = False
                self._popover.hide_now()
        return False
