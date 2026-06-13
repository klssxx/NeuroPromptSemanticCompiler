"""GUI page for version history and visual comparison."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QSplitter, QTabWidget, QTextEdit,
    QVBoxLayout, QWidget,
)

from i18n import tr
from version_history import VersionHistory, compute_diff, compute_unified_diff


def build_history_page(parent: "MainWindow") -> QWidget:
    """Build the version history page for the extreme mode sidebar."""
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(28, 24, 28, 24)
    layout.setSpacing(12)

    # Header
    header = QHBoxLayout()
    title = QLabel(tr("history.page.title"))
    title.setObjectName("SectionTitle")
    header.addWidget(title)
    header.addStretch(1)

    new_btn = QPushButton(tr("history.action.new"))
    new_btn.clicked.connect(lambda: _save_current_version(parent))
    header.addWidget(new_btn)

    clear_btn = QPushButton(tr("history.action.clear_all"))
    clear_btn.setObjectName("DangerButton")
    clear_btn.clicked.connect(lambda: _clear_all_versions(parent))
    header.addWidget(clear_btn)
    layout.addLayout(header)

    # Main splitter: list | detail
    splitter = QSplitter(Qt.Horizontal)

    # Left: version list
    list_widget = QListWidget()
    list_widget.setAlternatingRowColors(True)
    list_widget.setMinimumWidth(280)
    splitter.addWidget(list_widget)

    # Right: detail tabs
    detail_tabs = QTabWidget()

    # Content tab
    content_view = QTextEdit()
    content_view.setReadOnly(True)
    detail_tabs.addTab(content_view, tr("history.tab.content"))

    # Diff tab
    diff_view = QTextEdit()
    diff_view.setReadOnly(True)
    detail_tabs.addTab(diff_view, tr("history.tab.diff"))

    # Meta tab
    meta_label = QLabel()
    meta_label.setWordWrap(True)
    meta_label.setObjectName("Muted")
    detail_tabs.addTab(meta_label, tr("history.tab.meta"))

    splitter.addWidget(detail_tabs)
    splitter.setStretchFactor(0, 0)
    splitter.setStretchFactor(1, 1)
    layout.addWidget(splitter, 1)

    # Compare row
    compare_row = QHBoxLayout()
    compare_row.addWidget(QLabel(tr("history.compare.label")))
    compare_combo = QComboBox()
    compare_combo.setMinimumWidth(200)
    compare_row.addWidget(compare_combo)
    compare_btn = QPushButton(tr("history.compare.btn"))
    compare_row.addWidget(compare_btn)
    compare_row.addStretch(1)

    restore_btn = QPushButton(tr("history.action.restore"))
    restore_btn.clicked.connect(lambda: _restore_version(parent, list_widget))
    compare_row.addWidget(restore_btn)

    del_btn = QPushButton(tr("history.action.delete"))
    del_btn.setObjectName("DangerButton")
    del_btn.clicked.connect(lambda: _delete_version(parent, list_widget))
    compare_row.addWidget(del_btn)
    layout.addLayout(compare_row)

    # Store references
    page._list = list_widget
    page._content_view = content_view
    page._diff_view = diff_view
    page._meta_label = meta_label
    page._compare_combo = compare_combo

    # Signal connections
    list_widget.currentItemChanged.connect(
        lambda item, _prev: _show_version_detail(parent, item, content_view, meta_label)
    )
    compare_btn.clicked.connect(
        lambda: _compare_versions(parent, list_widget, compare_combo, diff_view)
    )
    compare_combo.currentTextChanged.connect(lambda: diff_view.clear())

    # Initial load
    _refresh_history_list(parent, list_widget, compare_combo)

    return page


def _get_history(parent) -> VersionHistory:
    if not hasattr(parent, "_version_history"):
        parent._version_history = VersionHistory()
    return parent._version_history


def _refresh_history_list(parent, list_widget: QListWidget, combo: QComboBox | None = None) -> None:
    hist = _get_history(parent)
    list_widget.clear()
    if combo:
        combo.clear()

    versions = hist.list_all()
    for ver in versions:
        display = f"{ver.name}  —  {ver.display_date}"
        item = QListWidgetItem(display)
        item.setData(Qt.UserRole, ver.id)
        item.setToolTip(ver.short_content)
        list_widget.addItem(item)
        if combo:
            combo.addItem(display, ver.id)


def _show_version_detail(parent, item: QListWidgetItem | None, content_view: QTextEdit, meta_label: QLabel) -> None:
    if not item:
        content_view.clear()
        meta_label.clear()
        return
    ver_id = item.data(Qt.UserRole)
    hist = _get_history(parent)
    ver = hist.get(ver_id)
    if not ver:
        return
    content_view.setPlainText(ver.content)
    meta_text = (
        f"ID: {ver.id}\n"
        f"Target: {ver.target} | Profile: {ver.profile}\n"
        f"Created: {ver.created_at}\n"
        f"Notes: {ver.notes or '(sin notas)'}\n"
        f"Variables: {ver.variables_used or '(ninguna)'}"
    )
    meta_label.setText(meta_text)


def _compare_versions(parent, list_widget: QListWidget, combo: QComboBox, diff_view: QTextEdit) -> None:
    current_item = list_widget.currentItem()
    if not current_item:
        QMessageBox.information(parent, "", tr("history.compare.select_first"))
        return
    compare_idx = combo.currentIndex()
    if compare_idx < 0:
        return
    compare_id = combo.itemData(compare_idx)
    current_id = current_item.data(Qt.UserRole)

    if current_id == compare_id:
        QMessageBox.information(parent, "", tr("history.compare.same"))
        return

    hist = _get_history(parent)
    ver_a = hist.get(current_id)
    ver_b = hist.get(compare_id)
    if not ver_a or not ver_b:
        return

    diff = compute_diff(ver_a.content, ver_b.content)
    unified = compute_unified_diff(ver_a.content, ver_b.content, ver_a.name, ver_b.name)

    stats = diff["stats"]
    lines = [
        tr("history.diff.summary").format(
            added=stats["added_count"],
            removed=stats["removed_count"],
            total_old=stats["total_old"],
            total_new=stats["total_new"],
        ),
        "",
        "═" * 40,
        "",
    ]

    if diff["removed"]:
        lines.append(tr("history.diff.removed"))
        for line in diff["removed"]:
            lines.append(f"  - {line}")
        lines.append("")

    if diff["added"]:
        lines.append(tr("history.diff.added"))
        for line in diff["added"]:
            lines.append(f"  + {line}")
        lines.append("")

    lines.append("═" * 40)
    lines.append(tr("history.diff.unified"))
    lines.append(unified)

    diff_view.setPlainText("\n".join(lines))


def _save_current_version(parent) -> None:
    if not parent.result:
        QMessageBox.information(parent, "", tr("history.save.no_result"))
        return
    content = parent.result.get("optimized_prompt", parent.result.get("chosen_nsl", ""))
    if not content:
        QMessageBox.information(parent, "", tr("history.save.no_content"))
        return
    hist = _get_history(parent)
    name = tr("history.save.name_default")
    if hasattr(parent, "prompt_edit"):
        prompt_text = parent.prompt_edit.toPlainText()
        if prompt_text:
            name = prompt_text[:60].replace("\n", " ")
    ver = hist.create_version(
        name=name,
        content=content,
        target=parent.result.get("target", "auto"),
        profile=parent.result.get("profile", "AUTO"),
        informal_input=parent.result.get("original", ""),
    )
    _refresh_hist(parent)
    QMessageBox.information(parent, "", tr("history.save.done").format(name=ver.name))


def _delete_version(parent, list_widget: QListWidget) -> None:
    item = list_widget.currentItem()
    if not item:
        return
    reply = QMessageBox.question(
        parent, tr("history.delete.title"),
        tr("history.delete.confirm"),
        QMessageBox.Yes | QMessageBox.No,
    )
    if reply != QMessageBox.Yes:
        return
    ver_id = item.data(Qt.UserRole)
    hist = _get_history(parent)
    hist.delete(ver_id)
    _refresh_hist(parent)


def _restore_version(parent, list_widget: QListWidget) -> None:
    item = list_widget.currentItem()
    if not item:
        return
    ver_id = item.data(Qt.UserRole)
    hist = _get_history(parent)
    ver = hist.get(ver_id)
    if not ver:
        return
    if hasattr(parent, "simple_prompt_edit"):
        parent.simple_prompt_edit.setPlainText(ver.informal_input or ver.content)
    if hasattr(parent, "prompt_edit"):
        parent.prompt_edit.setPlainText(ver.informal_input or ver.content)
    QMessageBox.information(parent, "", tr("history.restore.done").format(name=ver.name))


def _clear_all_versions(parent) -> None:
    reply = QMessageBox.question(
        parent, tr("history.clear.title"),
        tr("history.clear.confirm"),
        QMessageBox.Yes | QMessageBox.No,
    )
    if reply != QMessageBox.Yes:
        return
    hist = _get_history(parent)
    for ver in hist.list_all():
        hist.delete(ver.id)
    _refresh_hist(parent)


def _refresh_hist(parent) -> None:
    if hasattr(parent, "pages") and "historial" in parent.pages:
        page = parent.pages["historial"]
        _refresh_history_list(parent, page._list, page._compare_combo)
