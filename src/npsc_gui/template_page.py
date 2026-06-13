"""GUI page for managing reusable prompt templates."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QPlainTextEdit, QPushButton, QTabWidget, QVBoxLayout, QWidget,
)

from i18n import tr
from template_manager import TemplateManager, PromptTemplate
from utils import now_run_id


class TemplateEditorDialog(QDialog):
    """Dialog for creating/editing a template."""

    def __init__(self, parent: QWidget | None = None, template: PromptTemplate | None = None) -> None:
        super().__init__(parent)
        self._template = template
        self.setWindowTitle(tr("tpl.editor.title") if template else tr("tpl.create.title"))
        self.setMinimumSize(520, 420)
        self._build_ui()
        if template:
            self._populate(template)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        form.addRow(tr("tpl.field.name"), self.name_edit)

        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("General")
        form.addRow(tr("tpl.field.category"), self.category_edit)

        self.desc_edit = QLineEdit()
        form.addRow(tr("tpl.field.description"), self.desc_edit)

        self.target_combo = QComboBox()
        self.target_combo.addItems(["auto", "hermes", "codex", "gpt", "claude", "gemini", "qwen", "deepseek", "llama", "mistral", "generic"])
        form.addRow(tr("tpl.field.target"), self.target_combo)

        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["AUTO", "FAST", "STANDARD", "ADVANCED", "ROP", "RESEARCH_MAX"])
        form.addRow(tr("tpl.field.profile"), self.profile_combo)

        layout.addLayout(form)

        layout.addWidget(QLabel(tr("tpl.field.content")))
        self.content_edit = QPlainTextEdit()
        self.content_edit.setPlaceholderText(tr("tpl.placeholder.content"))
        layout.addWidget(self.content_edit, 1)

        # Variable hint
        var_hint = QLabel(tr("tpl.variable.hint"))
        var_hint.setObjectName("Muted")
        layout.addWidget(var_hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self, tpl: PromptTemplate) -> None:
        self.name_edit.setText(tpl.name)
        self.category_edit.setText(tpl.category)
        self.desc_edit.setText(tpl.description)
        self.target_combo.setCurrentText(tpl.target)
        self.profile_combo.setCurrentText(tpl.profile)
        self.content_edit.setPlainText(tpl.content)

    def _on_save(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", tr("tpl.error.name_required"))
            return
        content = self.content_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Error", tr("tpl.error.content_required"))
            return
        self.accept()

    def get_template(self) -> PromptTemplate:
        tpl_id = self._template.id if self._template else now_run_id("tpl")
        return PromptTemplate(
            id=tpl_id,
            name=self.name_edit.text().strip(),
            content=self.content_edit.toPlainText(),
            category=self.category_edit.text().strip() or "General",
            description=self.desc_edit.text().strip(),
            target=self.target_combo.currentText(),
            profile=self.profile_combo.currentText(),
            created_at=self._template.created_at if self._template else "",
            updated_at="",
        )


def build_template_page(parent: "MainWindow") -> QWidget:
    """Build the template management page for the extreme mode sidebar."""
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(28, 24, 28, 24)
    layout.setSpacing(12)

    # Header
    header = QHBoxLayout()
    title = QLabel(tr("tpl.page.title"))
    title.setObjectName("SectionTitle")
    header.addWidget(title)
    header.addStretch(1)

    new_btn = QPushButton(tr("tpl.action.new"))
    new_btn.clicked.connect(lambda: _create_template(parent))
    header.addWidget(new_btn)
    layout.addLayout(header)

    # Category filter
    filter_row = QHBoxLayout()
    filter_row.addWidget(QLabel(tr("tpl.filter.category")))
    category_combo = QComboBox()
    category_combo.addItem(tr("tpl.filter.all"))
    category_combo.setMinimumWidth(180)
    filter_row.addWidget(category_combo)
    filter_row.addStretch(1)

    import_btn = QPushButton(tr("tpl.action.import"))
    import_btn.clicked.connect(lambda: _import_template(parent))
    filter_row.addWidget(import_btn)

    export_all_btn = QPushButton(tr("tpl.action.export_all"))
    export_all_btn.clicked.connect(lambda: _export_all_templates(parent))
    filter_row.addWidget(export_all_btn)
    layout.addLayout(filter_row)

    # Template list
    template_list = QListWidget()
    template_list.setAlternatingRowColors(True)
    layout.addWidget(template_list, 1)

    # Detail panel
    detail_tabs = QTabWidget()

    content_preview = QPlainTextEdit()
    content_preview.setReadOnly(True)
    detail_tabs.addTab(content_preview, tr("tpl.tab.content"))

    meta_label = QLabel()
    meta_label.setWordWrap(True)
    meta_label.setObjectName("Muted")
    detail_tabs.addTab(meta_label, tr("tpl.tab.meta"))

    layout.addWidget(detail_tabs)

    # Action buttons
    actions = QHBoxLayout()
    use_btn = QPushButton(tr("tpl.action.use"))
    edit_btn = QPushButton(tr("tpl.action.edit"))
    dup_btn = QPushButton(tr("tpl.action.duplicate"))
    del_btn = QPushButton(tr("tpl.action.delete"))
    del_btn.setObjectName("DangerButton")

    actions.addWidget(use_btn)
    actions.addWidget(edit_btn)
    actions.addWidget(dup_btn)
    actions.addWidget(del_btn)
    actions.addStretch(1)
    layout.addLayout(actions)

    # Store references on the page widget for later access
    page._template_list = template_list
    page._category_combo = category_combo
    page._content_preview = content_preview
    page._meta_label = meta_label

    # Connect signals
    template_list.currentItemChanged.connect(
        lambda item, _prev: _show_template_detail(parent, item, content_preview, meta_label)
    )
    category_combo.currentTextChanged.connect(
        lambda _txt: _refresh_template_list(parent, template_list, category_combo)
    )
    use_btn.clicked.connect(lambda: _use_template(parent, template_list))
    edit_btn.clicked.connect(lambda: _edit_template(parent, template_list))
    dup_btn.clicked.connect(lambda: _duplicate_template(parent, template_list))
    del_btn.clicked.connect(lambda: _delete_template(parent, template_list))

    # Initial load
    _refresh_template_list(parent, template_list, category_combo)

    return page


def _get_manager(parent) -> TemplateManager:
    if not hasattr(parent, "_template_manager"):
        parent._template_manager = TemplateManager()
    return parent._template_manager


def _refresh_template_list(parent, list_widget: QListWidget, category_combo: QComboBox) -> None:
    mgr = _get_manager(parent)
    list_widget.clear()
    category = category_combo.currentText()
    tr_all = tr("tpl.filter.all")

    templates = mgr.list_all()
    for tpl in templates:
        if category != tr_all and tpl.category != category:
            continue
        item = QListWidgetItem(f"{tpl.name}  [{tpl.category}]")
        item.setData(Qt.UserRole, tpl.id)
        list_widget.addItem(item)

    # Update category filter
    category_combo.blockSignals(True)
    current = category_combo.currentText()
    category_combo.clear()
    category_combo.addItem(tr_all)
    for cat in mgr.categories():
        category_combo.addItem(cat)
    idx = category_combo.findText(current)
    if idx >= 0:
        category_combo.setCurrentIndex(idx)
    category_combo.blockSignals(False)


def _show_template_detail(parent, item: QListWidgetItem | None, content_preview: QPlainTextEdit, meta_label: QLabel) -> None:
    if not item:
        content_preview.clear()
        meta_label.clear()
        return
    tpl_id = item.data(Qt.UserRole)
    mgr = _get_manager(parent)
    tpl = mgr.get(tpl_id)
    if not tpl:
        return
    content_preview.setPlainText(tpl.content)
    meta_text = (
        f"ID: {tpl.id}\n"
        f"Target: {tpl.target} | Profile: {tpl.profile}\n"
        f"Created: {tpl.created_at}\n"
        f"Updated: {tpl.updated_at}\n"
        f"Description: {tpl.description}"
    )
    meta_label.setText(meta_text)


def _create_template(parent) -> None:
    from npsc_gui.main_window import MainWindow
    dlg = TemplateEditorDialog(parent)
    if dlg.exec() != QDialog.Accepted:
        return
    tpl = dlg.get_template()
    mgr = _get_manager(parent)
    mgr.create(tpl)
    _refresh_list(parent)


def _edit_template(parent, list_widget: QListWidget) -> None:
    item = list_widget.currentItem()
    if not item:
        return
    tpl_id = item.data(Qt.UserRole)
    mgr = _get_manager(parent)
    tpl = mgr.get(tpl_id)
    if not tpl:
        return
    dlg = TemplateEditorDialog(parent, tpl)
    if dlg.exec() != QDialog.Accepted:
        return
    updated = dlg.get_template()
    mgr.update(updated)
    _refresh_list(parent)


def _duplicate_template(parent, list_widget: QListWidget) -> None:
    item = list_widget.currentItem()
    if not item:
        return
    tpl_id = item.data(Qt.UserRole)
    mgr = _get_manager(parent)
    mgr.duplicate(tpl_id)
    _refresh_list(parent)


def _delete_template(parent, list_widget: QListWidget) -> None:
    item = list_widget.currentItem()
    if not item:
        return
    tpl_id = item.data(Qt.UserRole)
    name = item.text()
    reply = QMessageBox.question(
        parent, tr("tpl.delete.title"),
        tr("tpl.delete.confirm").format(name=name),
        QMessageBox.Yes | QMessageBox.No,
    )
    if reply != QMessageBox.Yes:
        return
    mgr = _get_manager(parent)
    mgr.delete(tpl_id)
    _refresh_list(parent)


def _use_template(parent, list_widget: QListWidget) -> None:
    item = list_widget.currentItem()
    if not item:
        return
    tpl_id = item.data(Qt.UserRole)
    mgr = _get_manager(parent)
    tpl = mgr.get(tpl_id)
    if not tpl:
        return
    # Set the prompt text in both modes
    if hasattr(parent, "simple_prompt_edit"):
        parent.simple_prompt_edit.setPlainText(tpl.content)
    if hasattr(parent, "prompt_edit"):
        parent.prompt_edit.setPlainText(tpl.content)
    # Set profile and target
    if hasattr(parent, "simple_profile_combo"):
        parent.simple_profile_combo.setCurrentText(tpl.profile)
    if hasattr(parent, "profile_combo"):
        parent.profile_combo.setCurrentText(tpl.profile)
    if hasattr(parent, "simple_target_combo"):
        parent.simple_target_combo.setCurrentText(tpl.target)
    if hasattr(parent, "target_combo"):
        parent.target_combo.setCurrentText(tpl.target)
    # Switch to simple mode
    if hasattr(parent, "_switch_to_mode"):
        from npsc_gui.main_window import MODE_SIMPLE
        parent._switch_to_mode(MODE_SIMPLE)


def _import_template(parent) -> None:
    from PySide6.QtWidgets import QFileDialog
    path, _ = QFileDialog.getOpenFileName(
        parent, tr("tpl.import.title"), "", "JSON (*.json)"
    )
    if not path:
        return
    mgr = _get_manager(parent)
    mgr.import_template(path)
    _refresh_list(parent)


def _export_all_templates(parent) -> None:
    from PySide6.QtWidgets import QFileDialog
    dest = QFileDialog.getExistingDirectory(parent, tr("tpl.export.title"))
    if not dest:
        return
    mgr = _get_manager(parent)
    written = mgr.export_all(dest)
    QMessageBox.information(
        parent, tr("tpl.export.done"),
        tr("tpl.export.count").format(count=len(written)),
    )


def _refresh_list(parent) -> None:
    """Refresh the template list by finding the page widget."""
    if hasattr(parent, "pages") and "plantillas" in parent.pages:
        page = parent.pages["plantillas"]
        _refresh_template_list(parent, page._template_list, page._category_combo)
