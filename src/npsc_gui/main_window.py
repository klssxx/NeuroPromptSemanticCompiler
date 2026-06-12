from __future__ import annotations

import json
import os
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, QUrl, Signal, Slot, QTimer
from PySide6.QtGui import QDesktopServices, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from compilation_profiles import supported_profile_names
from i18n import set_language, tr
from model_adapter import load_model_profiles
from npsc_gui.controller import CompileController
from npsc_gui.glossary import CATEGORIES, format_entry, get_entry, load_glossary, search_glossary
from npsc_gui.help_popover import ContextHelpButton, close_context_help_popovers
from npsc_gui.settings import data_dir, load_settings, reset_settings, save_settings
from npsc_gui.theme import QSS, get_qss
from npsc_gui.tooltips import apply_tooltip, glossary_term_for, help_text
from npsc_gui.components.circle_indicator import CircleIndicator
from npsc_gui.components.scan_ring import ScanRing
from npsc_gui.components.health_dashboard import HealthDashboard
from npsc_gui.components.status_chip import StatusChip
from npsc_gui.components.result_card import ResultCard
from npsc_gui.components.tool_card import ToolCard
from npsc_gui.components.nav_group import NavGroup, NavItem
from token_estimator import estimate_counters


ROOT = Path(__file__).resolve().parents[2]
ICON_PATH = ROOT / "assets" / "icons" / "neuro-prompt-semantic-compiler.svg"
EXAMPLE_PATH = ROOT / "examples" / "messy_prompt.txt"

# ─── Mode constants ──────────────────────────────────────────────────────────
MODE_SIMPLE = "simple"
MODE_EXTREME = "extreme"


class CompileWorker(QObject):
    progress = Signal(int, str)
    finished = Signal(dict)
    failed = Signal(str)
    canceled = Signal()

    def __init__(self, controller: CompileController, request: dict) -> None:
        super().__init__()
        self.controller = controller
        self.request = request
        self.cancel_requested = False

    def cancel(self) -> None:
        self.cancel_requested = True

    @Slot()
    def run(self) -> None:
        try:
            stages = [
                (10, "Analizando intención"),
                (25, "Detectando restricciones"),
                (40, "Seleccionando perfil"),
                (55, "Generando IR semántica"),
                (70, "Compilando NSL y prompt de ejecución"),
                (85, "Validando preservación"),
                (95, "Generando archivos"),
            ]
            for value, label in stages[:4]:
                if self.cancel_requested:
                    self.canceled.emit()
                    return
                self.progress.emit(value, label)
            if self.cancel_requested:
                self.canceled.emit()
                return
            result = self.controller.compile(**self.request)
            if self.cancel_requested:
                self.canceled.emit()
                return
            for value, label in stages[4:]:
                if self.cancel_requested:
                    self.canceled.emit()
                    return
                self.progress.emit(value, label)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = load_settings()
        set_language(str(self.settings.get("language", "es")))
        self.controller = CompileController()
        self.result: dict | None = None
        self.cancel_requested = False
        self.worker_thread: QThread | None = None
        self.worker: CompileWorker | None = None
        self.last_saved_dir: Path | None = None
        self.pages: dict[str, QWidget] = {}
        self.nav_items: dict[str, NavItem] = {}
        self.section_help_buttons: dict[str, ContextHelpButton] = {}
        self.option_help_buttons: dict[str, ContextHelpButton] = {}

        # Mode state — default to simple
        self._current_mode: str = MODE_SIMPLE

        # Debounce timer for counter updates (avoid estimate_text on every keystroke)
        self._counters_debounce_timer = QTimer(self)
        self._counters_debounce_timer.setSingleShot(True)
        self._counters_debounce_timer.setInterval(150)
        self._counters_debounce_timer.timeout.connect(self._update_counters)

        self.setObjectName("NPSCMainWindow")
        self.setWindowTitle("NeuroPrompt Semantic Compiler")
        self.resize(int(self.settings["window_width"]), int(self.settings["window_height"]))
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setStyleSheet(get_qss(self.settings.get("theme", "dark")))

        self._build_ui()
        self._bind_shortcuts()
        self._restore_settings()
        self._update_counters()
        self._set_header_status("ok", tr("status.ready"))

    # ─── Layout ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Global header
        root_layout.addWidget(self._build_header())

        # Top-level mode stack: index 0 = simple mode, index 1 = extreme mode
        self.mode_stack = QStackedWidget()
        self.mode_stack.addWidget(self._build_simple_mode())
        self.mode_stack.addWidget(self._build_extreme_mode())
        root_layout.addWidget(self.mode_stack, 1)

        # Progress strip (3px minimal)
        self.progress_strip = QProgressBar()
        self.progress_strip.setRange(0, 100)
        self.progress_strip.setValue(0)
        self.progress_strip.setFixedHeight(3)
        self.progress_strip.setTextVisible(False)
        root_layout.addWidget(self.progress_strip)

        root_layout.addWidget(self._build_status_bar())
        self.setCentralWidget(root)

    # ─── Header ────────────────────────────────────────────────────

    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Header")
        frame.setFixedHeight(44)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        brand = QLabel("N")
        brand.setObjectName("BrandGlyph")
        brand.setFixedSize(28, 28)
        brand.setAlignment(Qt.AlignCenter)

        title = QLabel("NeuroPrompt")
        title.setObjectName("AppTitle")
        sep = QLabel("·")
        sep.setObjectName("Muted")
        sub = QLabel(tr("app.subtitle"))
        sub.setObjectName("Muted")

        layout.addWidget(brand)
        layout.addWidget(title)
        layout.addWidget(sep)
        layout.addWidget(sub)
        layout.addStretch(1)

        self.header_chip = StatusChip(tr("status.ready"), "ok")
        layout.addWidget(self.header_chip)

        # Mode toggle button — changes label depending on current mode
        self.mode_toggle_btn = QPushButton(tr("mode.activate_extreme"))
        self.mode_toggle_btn.setObjectName("ModeToggleBtn")
        self.mode_toggle_btn.clicked.connect(self._toggle_mode)
        apply_tooltip(self.mode_toggle_btn, "advanced_mode")
        layout.addWidget(self.mode_toggle_btn)

        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("HeaderIconButton")
        settings_btn.setFixedSize(32, 32)
        settings_btn.clicked.connect(self._open_settings)
        apply_tooltip(settings_btn, "settings")

        help_btn = QPushButton("?")
        help_btn.setObjectName("HeaderIconButton")
        help_btn.setFixedSize(32, 32)
        help_btn.clicked.connect(self._open_help)
        apply_tooltip(help_btn, "help")

        layout.addWidget(settings_btn)
        layout.addWidget(help_btn)
        return frame

    # ═══════════════════════════════════════════════════════════════
    #  MODO SENCILLO — Simple Mode
    # ═══════════════════════════════════════════════════════════════

    def _build_simple_mode(self) -> QWidget:
        """Build the simple mode root: a stacked widget with home (index 0) and result (index 1)."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.simple_stack = QStackedWidget()
        self.simple_stack.addWidget(self._build_simple_home())
        self.simple_stack.addWidget(self._build_simple_result())
        layout.addWidget(self.simple_stack, 1)
        return container

    # ─── Simple Home ──────────────────────────────────────────────

    def _build_simple_home(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 28, 40, 28)
        layout.setSpacing(16)

        # Title area
        title = QLabel("NeuroPrompt Semantic Compiler")
        title.setObjectName("SimpleTitle")
        subtitle = QLabel("Convierte una idea en un prompt claro, completo y verificable")
        subtitle.setObjectName("SimpleSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Prompt label
        prompt_label = QLabel("Escribe o pega tu prompt")
        prompt_label.setObjectName("SimplePromptLabel")
        layout.addWidget(prompt_label)

        # Prompt input
        self.simple_prompt_edit = QPlainTextEdit()
        self.simple_prompt_edit.setPlaceholderText(
            "Pega aquí tu prompt original.\n\n"
            "AUTO recomienda el mejor perfil automáticamente."
        )
        self.simple_prompt_edit.setMinimumHeight(160)
        self.simple_prompt_edit.textChanged.connect(self._on_simple_prompt_changed)
        layout.addWidget(self.simple_prompt_edit, 1)

        # Profile status row
        profile_row = QHBoxLayout()
        profile_row.setSpacing(8)
        profile_lbl = QLabel("Perfil:")
        profile_lbl.setObjectName("Muted")
        self.simple_profile_label = QLabel("Automático recomendado")
        self.simple_profile_label.setObjectName("SimpleProfileValue")
        profile_row.addWidget(profile_lbl)
        profile_row.addWidget(self.simple_profile_label)
        profile_row.addStretch(1)
        layout.addLayout(profile_row)

        # Collapsible advanced options
        self.adv_toggle_btn = QPushButton("▸ Opciones avanzadas")
        self.adv_toggle_btn.setObjectName("SimpleAdvToggle")
        self.adv_toggle_btn.setCheckable(True)
        self.adv_toggle_btn.setChecked(False)
        self.adv_toggle_btn.clicked.connect(self._toggle_simple_adv_options)
        layout.addWidget(self.adv_toggle_btn)

        self.adv_frame = QFrame()
        self.adv_frame.setObjectName("SimpleAdvFrame")
        adv_layout = QVBoxLayout(self.adv_frame)
        adv_layout.setContentsMargins(16, 8, 16, 8)
        adv_layout.setSpacing(8)

        # Profile combo
        p_row = QHBoxLayout()
        p_row.addWidget(QLabel("Perfil:"))
        self.simple_profile_combo = QComboBox()
        self.simple_profile_combo.addItems(supported_profile_names())
        self.simple_profile_combo.currentTextChanged.connect(self._on_simple_profile_combo_changed)
        p_row.addWidget(self.simple_profile_combo)
        p_row.addStretch(1)
        adv_layout.addLayout(p_row)

        # Model combo
        m_row = QHBoxLayout()
        m_row.addWidget(QLabel("Modelo:"))
        self.simple_target_combo = QComboBox()
        self.simple_target_combo.addItems(list(load_model_profiles().keys()))
        self.simple_target_combo.currentTextChanged.connect(self._on_target_changed)
        m_row.addWidget(self.simple_target_combo)
        m_row.addStretch(1)
        adv_layout.addLayout(m_row)

        # Level combo
        l_row = QHBoxLayout()
        l_row.addWidget(QLabel("Nivel:"))
        self.simple_level_combo = QComboBox()
        for label, value in [
            ("Automático", "profile_default"),
            ("Conservador", "safe"),
            ("Equilibrado", "balanced"),
            ("Compacto", "aggressive"),
            ("Todos", "all"),
        ]:
            self.simple_level_combo.addItem(label, value)
        l_row.addWidget(self.simple_level_combo)
        l_row.addStretch(1)
        adv_layout.addLayout(l_row)

        # Validation strict
        self.simple_strict_check = QCheckBox("Validación estricta")
        adv_layout.addWidget(self.simple_strict_check)

        # Preserve original
        self.simple_preserve_check = QCheckBox("Permitir original en archivos técnicos")
        self.simple_preserve_check.setChecked(True)
        adv_layout.addWidget(self.simple_preserve_check)

        # Privacy mode
        priv_row = QHBoxLayout()
        priv_row.addWidget(QLabel("Privacidad:"))
        self.simple_privacy_combo = QComboBox()
        for label, value in [
            ("Guardar original completo", "full_original"),
            ("Guardar solo huella digital", "hash_only"),
            ("Guardar vista parcial recortada", "redacted_preview"),
        ]:
            self.simple_privacy_combo.addItem(label, value)
        priv_row.addWidget(self.simple_privacy_combo)
        priv_row.addStretch(1)
        adv_layout.addLayout(priv_row)

        self.adv_frame.setVisible(False)
        layout.addWidget(self.adv_frame)

        # Main compile button — visually dominant
        self.simple_compile_btn = QPushButton("COMPILAR PROMPT")
        self.simple_compile_btn.setObjectName("PrimaryButton")
        self.simple_compile_btn.setMinimumHeight(44)
        self.simple_compile_btn.clicked.connect(self.compile_current)
        apply_tooltip(self.simple_compile_btn, "compile")
        layout.addWidget(self.simple_compile_btn)

        # Secondary actions row
        secondary = QHBoxLayout()
        secondary.setSpacing(8)

        load_ex_btn = QPushButton("Cargar ejemplo")
        load_ex_btn.clicked.connect(self.load_example)
        apply_tooltip(load_ex_btn, "example")
        secondary.addWidget(load_ex_btn)

        clear_btn = QPushButton("Limpiar")
        clear_btn.clicked.connect(self.new_prompt)
        apply_tooltip(clear_btn, "reset")
        secondary.addWidget(clear_btn)

        # Cancel button (hidden by default, shown during compilation)
        self.simple_cancel_btn = QPushButton("Cancelar")
        self.simple_cancel_btn.setObjectName("DangerButton")
        self.simple_cancel_btn.clicked.connect(self.cancel_compile)
        self.simple_cancel_btn.setVisible(False)
        apply_tooltip(self.simple_cancel_btn, "cancel")
        secondary.addWidget(self.simple_cancel_btn)

        history_btn = QPushButton("Historial")
        history_btn.setObjectName("SimpleHistBtn")
        history_btn.clicked.connect(self._show_simple_history)
        secondary.addWidget(history_btn)

        secondary.addStretch(1)
        layout.addLayout(secondary)

        # Mode switch link
        mode_link_row = QHBoxLayout()
        mode_question = QLabel("¿Necesitas control técnico completo?")
        mode_question.setObjectName("Muted")
        mode_link_row.addWidget(mode_question)
        mode_link_row.addStretch(1)
        layout.addLayout(mode_link_row)

        # ── Premium: compact ScanRing + HealthDashboard ──
        # (replaces the old centered hero area with a premium inline strip)
        self.simple_scan_ring = ScanRing(size=52, ring_width=3)
        self.simple_scan_ring.hide()  # shown only during/after compile

        simple_dash_row = QHBoxLayout()
        simple_dash_row.setSpacing(8)

        # Left: scan ring (compact)
        self.simple_scan_container = QWidget()
        scr_layout = QVBoxLayout(self.simple_scan_container)
        scr_layout.setContentsMargins(0, 0, 0, 0)
        scr_layout.setSpacing(2)
        scr_layout.setAlignment(Qt.AlignCenter)
        scr_layout.addWidget(self.simple_scan_ring)

        self.simple_scan_status = QLabel("")
        self.simple_scan_status.setObjectName("PremiumStatusText")
        self.simple_scan_status.setAlignment(Qt.AlignCenter)
        scr_layout.addWidget(self.simple_scan_status)

        self.simple_scan_container.hide()
        simple_dash_row.addWidget(self.simple_scan_container)

        # Right: health dashboard
        self.simple_health = HealthDashboard()
        simple_dash_row.addWidget(self.simple_health, 1)
        layout.addLayout(simple_dash_row)

        # Progress bar (visible during compile)
        self.simple_progress = QProgressBar()
        self.simple_progress.setRange(0, 100)
        self.simple_progress.setValue(0)
        self.simple_progress.setTextVisible(True)
        self.simple_progress.setVisible(False)
        layout.addWidget(self.simple_progress)

        return page

    # ─── Simple Result ─────────────────────────────────────────────

    def _build_simple_result(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 28, 40, 28)
        layout.setSpacing(12)

        # Success/error header
        self.simple_result_header = QLabel("✓ Prompt generado correctamente")
        self.simple_result_header.setObjectName("SimpleResultHeader")
        layout.addWidget(self.simple_result_header)

        # Results tabs
        self.simple_tabs = QTabWidget()
        self.simple_optimized_tab = QPlainTextEdit()
        self.simple_optimized_tab.setReadOnly(True)
        self.simple_tabs.addTab(self.simple_optimized_tab, "Prompt optimizado")

        self.simple_report_tab = QPlainTextEdit()
        self.simple_report_tab.setReadOnly(True)
        self.simple_tabs.addTab(self.simple_report_tab, "Informe")

        self.simple_validation_tab = QPlainTextEdit()
        self.simple_validation_tab.setReadOnly(True)
        self.simple_tabs.addTab(self.simple_validation_tab, "Validación")
        layout.addWidget(self.simple_tabs, 1)

        # Primary action — copy
        copy_row = QHBoxLayout()
        copy_row.setSpacing(8)

        self.simple_copy_btn = QPushButton("COPIAR PROMPT")
        self.simple_copy_btn.setObjectName("PrimaryButton")
        self.simple_copy_btn.setMinimumHeight(40)
        self.simple_copy_btn.clicked.connect(self.copy_recommended)
        apply_tooltip(self.simple_copy_btn, "copy")
        copy_row.addWidget(self.simple_copy_btn)

        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_all)
        apply_tooltip(save_btn, "save")
        copy_row.addWidget(save_btn)

        new_btn = QPushButton("Nueva compilación")
        new_btn.clicked.connect(self._simple_new_compilation)
        copy_row.addWidget(new_btn)

        copy_row.addStretch(1)
        layout.addLayout(copy_row)

        # Compact metrics summary (real data only)
        self.simple_metrics_label = QLabel("")
        self.simple_metrics_label.setObjectName("Muted")
        layout.addWidget(self.simple_metrics_label)

        # Generated files access (compact)
        self.simple_files_row = QHBoxLayout()
        self.simple_files_label = QLabel("")
        self.simple_files_label.setObjectName("Muted")
        self.simple_open_files_btn = QPushButton("Abrir carpeta")
        self.simple_open_files_btn.clicked.connect(self.open_last_output)
        self.simple_open_files_btn.setVisible(False)
        self.simple_files_row.addWidget(self.simple_files_label)
        self.simple_files_row.addWidget(self.simple_open_files_btn)
        self.simple_files_row.addStretch(1)
        layout.addLayout(self.simple_files_row)

        return page

    # ═══════════════════════════════════════════════════════════════
    #  MODO EXTREMO — Extreme Mode (preserved existing interface)
    # ═══════════════════════════════════════════════════════════════

    def _build_extreme_mode(self) -> QWidget:
        """Build the extreme mode: sidebar + stacked pages (all existing UI)."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self._add_page("resumen", self._build_dashboard())
        self._add_page("compilar", self._build_compiler())
        self._add_page("resultados", self._build_results())
        self._add_page("validacion", self._build_validation())
        self._add_page("perfiles", self._build_profiles())
        self._add_page("glosario", self._build_glossary())
        self._add_page("configuracion", self._build_settings_page())
        layout.addWidget(self.stack, 1)
        return container

    # ─── Sidebar ───────────────────────────────────────────────────

    def _build_sidebar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Sidebar")
        frame.setFixedWidth(190)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(0)

        # Group: Principal
        grp_main = NavGroup("Principal")
        self.nav_items["resumen"] = grp_main.add_item("resumen", "Resumen")
        self.nav_items["compilar"] = grp_main.add_item("compilar", "Compilar")
        self.nav_items["resultados"] = grp_main.add_item("resultados", "Resultados")
        self.nav_items["validacion"] = grp_main.add_item("validacion", "Validación")
        layout.addWidget(grp_main)

        # Group: Herramientas
        grp_tools = NavGroup("Herramientas")
        self.nav_items["perfiles"] = grp_tools.add_item("perfiles", "Perfiles")
        self.nav_items["glosario"] = grp_tools.add_item("glosario", "Glosario")
        layout.addWidget(grp_tools)

        # Group: Sistema
        grp_sys = NavGroup("Sistema")
        self.nav_items["configuracion"] = grp_sys.add_item("configuracion", "Configuración")
        layout.addWidget(grp_sys)

        layout.addStretch(1)

        # Connect all nav items
        for item in self.nav_items.values():
            item.clicked_page.connect(self._select_page)

        return frame

    # ─── Status Bar ────────────────────────────────────────────────

    def _build_status_bar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("StatusBar")
        frame.setFixedHeight(24)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(8)
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(6, 6)
        self.status_dot.setStyleSheet(f"background: #30B87A; border-radius: 3px;")
        self.status_label = QLabel("Preparado")
        self.status_label.setObjectName("Muted")
        self.status_profile = QLabel("Perfil: AUTO")
        self.status_profile.setObjectName("Muted")
        self.status_mode = QLabel("Modo: Sencillo")
        self.status_mode.setObjectName("Muted")
        self.status_extra = QLabel("Offline · X11")
        self.status_extra.setObjectName("Muted")
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("·"))
        layout.addWidget(self.status_profile)
        layout.addWidget(QLabel("·"))
        layout.addWidget(self.status_mode)
        layout.addStretch(1)
        layout.addWidget(self.status_extra)
        return frame

    # ─── Helper widgets ────────────────────────────────────────────

    def _help_button(self, key: str) -> ContextHelpButton:
        title, body = help_text(key)
        button = ContextHelpButton(title, body, self, glossary_term_for(key), self.open_glossary_term)
        return button

    def _section_header(self, title: str, help_key: str | None = None) -> QFrame:
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(title)
        label.setObjectName("SectionTitle")
        layout.addWidget(label)
        layout.addStretch(1)
        button = self._help_button(help_key or title)
        self.section_help_buttons[title] = button
        layout.addWidget(button)
        return frame

    def _label_with_help(self, text: str, help_key: str) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(text)
        layout.addWidget(label)
        button = self._help_button(help_key)
        self.option_help_buttons[help_key] = button
        layout.addWidget(button)
        layout.addStretch(1)
        return layout

    # ─── Dashboard (Resumen) ───────────────────────────────────────

    def _build_dashboard(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Hero: Circle + Prompt side by side
        hero = QHBoxLayout()
        hero.setSpacing(24)

        # Circle column
        circle_col = QVBoxLayout()
        circle_col.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.scan_ring = ScanRing(size=140, ring_width=5)
        circle_col.addWidget(self.scan_ring, 0, Qt.AlignHCenter)

        self.compile_hero_btn = QPushButton("Mejorar prompt")
        self.compile_hero_btn.setObjectName("PrimaryButton")
        self.compile_hero_btn.clicked.connect(self.compile_current)
        apply_tooltip(self.compile_hero_btn, "compile")
        circle_col.addWidget(self.compile_hero_btn, 0, Qt.AlignHCenter)

        self.hero_status = QLabel("Pega un prompt y pulsa Mejorar prompt.")
        self.hero_status.setObjectName("HeroStatus")
        self.hero_status.setAlignment(Qt.AlignHCenter)
        circle_col.addWidget(self.hero_status)
        circle_col.addStretch(1)

        # Prompt panel
        prompt_col = QVBoxLayout()
        prompt_col.setSpacing(6)

        # Mini tabs (visual only)
        tab_row = QHBoxLayout()
        tab_row.setSpacing(0)
        tab_active = QLabel("Prompt original")
        tab_active.setObjectName("PromptTab")
        tab_active.setProperty("active", True)
        tab_active.setStyleSheet("border-bottom: 2px solid #4CB8F5; padding: 6px 12px; font-weight: 600; color: #4CB8F5; font-size: 11px;")
        tab_row.addWidget(tab_active)
        tab_row.addStretch(1)
        prompt_col.addLayout(tab_row)

        self.prompt_edit = QPlainTextEdit()
        self.prompt_edit.setPlaceholderText("Pega aquí tu prompt original. AUTO recomienda el mejor perfil automáticamente.")
        self.prompt_edit.textChanged.connect(self._on_extreme_prompt_changed)
        prompt_col.addWidget(self.prompt_edit, 1)

        # Footer: counters + selects
        footer = QHBoxLayout()
        footer.setSpacing(8)
        self.char_label = QLabel("0 caracteres")
        self.char_label.setObjectName("Muted")
        self.token_label = QLabel("0 tokens aprox.")
        self.token_label.setObjectName("Muted")
        footer.addWidget(self.char_label)
        footer.addWidget(self.token_label)
        footer.addStretch(1)

        footer_label_style = "font-size: 10.5px; color: #6C717A;"
        sel_style = "font-size: 10.5px;"

        p_lbl = QLabel("Perfil:")
        p_lbl.setStyleSheet(footer_label_style)
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(supported_profile_names())
        self.profile_combo.setStyleSheet(sel_style)
        m_lbl = QLabel("Modelo:")
        m_lbl.setStyleSheet(footer_label_style)
        self.target_combo = QComboBox()
        self.target_combo.addItems(list(load_model_profiles().keys()))
        self.target_combo.setStyleSheet(sel_style)
        self.target_combo.currentTextChanged.connect(self._on_target_changed)
        l_lbl = QLabel("Nivel:")
        l_lbl.setStyleSheet(footer_label_style)
        self.level_combo = QComboBox()
        for label, value in [
            ("Automático", "profile_default"),
            ("Conservador", "safe"),
            ("Equilibrado", "balanced"),
            ("Compacto", "aggressive"),
            ("Todos", "all"),
        ]:
            self.level_combo.addItem(label, value)
        self.level_combo.setStyleSheet(sel_style)
        footer.addWidget(p_lbl)
        footer.addWidget(self.profile_combo)
        footer.addWidget(m_lbl)
        footer.addWidget(self.target_combo)
        footer.addWidget(l_lbl)
        footer.addWidget(self.level_combo)
        prompt_col.addLayout(footer)

        # Quick action bar (secondary actions only — the primary "Mejorar prompt"
        # button lives in the hero column above, so we don't duplicate it here)
        quick = QHBoxLayout()
        quick.setSpacing(6)

        clear_btn = QPushButton("Limpiar")
        clear_btn.clicked.connect(self.new_prompt)
        apply_tooltip(clear_btn, "reset")
        quick.addWidget(clear_btn)

        load_btn = QPushButton("Cargar archivo")
        load_btn.clicked.connect(self.load_file)
        apply_tooltip(load_btn, "load_file")
        quick.addWidget(load_btn)

        ex_btn = QPushButton("Ejemplo")
        ex_btn.clicked.connect(self.load_example)
        apply_tooltip(ex_btn, "example")
        quick.addWidget(ex_btn)

        quick.addStretch(1)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("DangerButton")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_compile)
        apply_tooltip(self.cancel_button, "cancel")
        self.cancel_button.setVisible(False)
        quick.addWidget(self.cancel_button)

        prompt_col.addLayout(quick)
        hero.addLayout(circle_col)
        hero.addLayout(prompt_col, 1)
        layout.addLayout(hero, 1)

        # Health dashboard (single source of truth for result metrics)
        # NOTE: Was previously duplicated with a row of 4 ResultCard widgets below;
        # the duplication was removed in the 2026-06-11 visual polish pass.
        self.extreme_health = HealthDashboard()
        layout.addWidget(self.extreme_health)

        # Tool cards
        tools_title = QLabel("Herramientas")
        tools_title.setObjectName("SectionTitle")
        layout.addWidget(tools_title)

        tools_row = QHBoxLayout()
        tools_row.setSpacing(10)

        # Glyphs: technical Unicode consistent with monospace UI typography.
        # Replaces the previous 🔍/✅/📄 emojis (looked improvised).
        t1 = ToolCard("Analizar semántica", "Extrae intención y restricciones sin compilar.")
        t1.set_icon_text("⌕")  # U+2315 telephone recorder — search-like
        t2 = ToolCard("Validar preservación", "Verifica pérdidas y restricciones críticas.")
        t2.set_icon_text("✓")  # U+2713 check mark
        t3 = ToolCard("Copiar y guardar", "Copia prompt listo o exporta resultados completos.")
        t3.set_icon_text("⎘")  # U+2398 next page
        t1.mousePressEvent = lambda e: self.analyze_only()
        t2.mousePressEvent = lambda e: self._select_page("validacion")
        t3.mousePressEvent = lambda e: self.copy_recommended()
        for t in (t1, t2, t3):
            tools_row.addWidget(t)
        tools_row.addStretch(1)
        layout.addLayout(tools_row)

        layout.addStretch(1)
        return page

    # ─── Compiler page ─────────────────────────────────────────────

    def _build_compiler(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(10)
        layout.addWidget(self._section_header("Compilador"))

        # Advanced options grid (strict, privacy, custom model)
        top = QGridLayout()
        self.custom_model_edit = QLineEdit()
        self.custom_model_edit.setPlaceholderText("Nombre del modelo personalizado")
        self.strict_check = QCheckBox("Validación estricta")
        self.preserve_check = QCheckBox("Permitir original en archivos técnicos")
        self.preserve_check.setChecked(True)
        self.privacy_combo = QComboBox()
        for label, value in [
            ("Guardar original completo", "full_original"),
            ("Guardar solo huella digital", "hash_only"),
            ("Guardar vista parcial recortada", "redacted_preview"),
        ]:
            self.privacy_combo.addItem(label, value)

        strict_row = QHBoxLayout()
        strict_row.setContentsMargins(0, 0, 0, 0)
        strict_row.addWidget(self.strict_check)
        strict_row.addWidget(self._help_button("strict"))
        strict_row.addStretch(1)
        top.addLayout(strict_row, 0, 0)
        top.addWidget(self.preserve_check, 0, 1)
        top.addLayout(self._label_with_help("Privacidad", "privacy"), 1, 0)
        top.addWidget(self.privacy_combo, 1, 1)
        top.addLayout(self._label_with_help("Modelo personalizado", "custom_model"), 2, 0)
        top.addWidget(self.custom_model_edit, 2, 1)
        layout.addLayout(top)
        self._on_target_changed(self.target_combo.currentText())

        # Prompt display (read-only mirror of dashboard's prompt_edit)
        self.compiler_prompt = QPlainTextEdit()
        self.compiler_prompt.setReadOnly(True)
        self.compiler_prompt.setPlaceholderText("El prompt se muestra aquí. Edítalo en la pestaña Resumen.")
        layout.addWidget(self.compiler_prompt, 1)
        counter_row = QHBoxLayout()
        self.char_label2 = QLabel("0 caracteres")
        self.char_label2.setObjectName("Muted")
        self.token_label2 = QLabel("0 tokens aprox.")
        self.token_label2.setObjectName("Muted")
        counter_row.addWidget(self.char_label2)
        counter_row.addWidget(self.token_label2)
        counter_row.addStretch(1)
        layout.addLayout(counter_row)

        # Action row
        action_row = QHBoxLayout()
        self.compile_button = QPushButton("Mejorar prompt")
        self.compile_button.setObjectName("PrimaryButton")
        apply_tooltip(self.compile_button, "compile")
        self.compile_button.clicked.connect(self.compile_current)
        action_row.addWidget(self.compile_button)

        for text, handler in [
            ("Analizar solamente", self.analyze_only),
            ("Limpiar", self.new_prompt),
            ("Cargar archivo", self.load_file),
            ("Pegar", self.paste_prompt),
            ("Cargar ejemplo", self.load_example),
            ("Guardar resultados", self.save_all),
        ]:
            button = QPushButton(text)
            button.clicked.connect(handler)
            key = {
                "Analizar solamente": "analyze",
                "Limpiar": "reset",
                "Cargar archivo": "load_file",
                "Pegar": "paste",
                "Cargar ejemplo": "example",
                "Guardar resultados": "save",
            }[text]
            apply_tooltip(button, key)
            action_row.addWidget(button)
        layout.addLayout(action_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)
        layout.addStretch(1)
        return page

    # ─── Results page ──────────────────────────────────────────────

    def _build_results(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(self._section_header("Resultados", "results_tab"))
        buttons = QHBoxLayout()
        copy_button = QPushButton("Copiar prompt listo")
        copy_button.clicked.connect(self.copy_recommended)
        apply_tooltip(copy_button, "copy")
        json_button = QPushButton("Copiar JSON para programas")
        json_button.clicked.connect(self.copy_json)
        apply_tooltip(json_button, "copy_json")
        save_button = QPushButton("Guardar resultados")
        save_button.clicked.connect(self.save_all)
        apply_tooltip(save_button, "save")
        open_button = QPushButton("Abrir carpeta de resultados")
        open_button.clicked.connect(self.open_last_output)
        apply_tooltip(open_button, "open_folder")
        buttons.addWidget(copy_button)
        buttons.addWidget(json_button)
        buttons.addWidget(save_button)
        buttons.addWidget(open_button)
        buttons.addStretch(1)
        for key in ["complete_report", "compact_nsl", "json_programs", "semantic_rules", "constraints_origin"]:
            buttons.addWidget(self._help_button(key))
        layout.addLayout(buttons)
        self.tabs = QTabWidget()
        self.summary_text = self._text_tab("Resumen")
        self.optimized_text = self._text_tab("Prompt listo para usar")
        self.hybrid_text = self._text_tab("Informe completo")
        self.original_text = self._text_tab("Prompt original")
        self.validation_text = self._text_tab("Validación")
        self.nsl_text = self._text_tab("NSL compacto")
        self.json_text = self._text_tab("JSON para programas")
        self.seeds_text = self._text_tab("Reglas semánticas")
        self.constraints_text = self._text_tab("Restricciones y origen")
        self.profile_text = self._text_tab("Perfil aplicado")
        self.tabs.currentChanged.connect(lambda _index: close_context_help_popovers())
        layout.addWidget(self.tabs, 1)
        return page

    def _text_tab(self, title: str) -> QPlainTextEdit:
        editor = QPlainTextEdit()
        editor.setReadOnly(True)
        self.tabs.addTab(editor, title)
        return editor

    # ─── Validation ────────────────────────────────────────────────

    def _build_validation(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(self._section_header("Validación"))
        self.validation_detail = QTextEdit()
        self.validation_detail.setReadOnly(True)
        layout.addWidget(self.validation_detail)
        return page

    # ─── Profiles ──────────────────────────────────────────────────

    def _build_profiles(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(self._section_header("Perfiles"))
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(
            "AUTO: analiza el prompt y elige el perfil más adecuado.\n\n"
            "FAST: ideal para tareas rápidas y sencillas. Genera una salida compacta.\n\n"
            "STANDARD: equilibrio entre claridad, tamaño y preservación de información.\n\n"
            "ADVANCED: recomendado para programación, arquitectura y tareas con varias condiciones.\n\n"
            "ROP: Reality Optimization Protocol para decisiones complejas con hipótesis, escenarios, evidencias y autocrítica.\n\n"
            "RESEARCH_MAX: máxima preservación y trazabilidad para investigación profunda."
        )
        layout.addWidget(text)
        return page

    # ─── Glossary ──────────────────────────────────────────────────

    def _build_glossary(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(self._section_header("Glosario"))
        title = QLabel("Diccionario fácil")
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Consulta palabras y abreviaturas de la aplicación con explicaciones sencillas.")
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        controls = QHBoxLayout()
        self.glossary_search = QLineEdit()
        self.glossary_search.setPlaceholderText("Buscar una palabra...")
        self.glossary_search.textChanged.connect(self._refresh_glossary)
        self.glossary_category = QComboBox()
        self.glossary_category.addItems(CATEGORIES)
        self.glossary_category.currentTextChanged.connect(self._refresh_glossary)
        self.glossary_count = QLabel("")
        self.glossary_count.setObjectName("Muted")
        controls.addWidget(self.glossary_search, 1)
        controls.addWidget(self.glossary_category)
        controls.addWidget(self.glossary_count)
        layout.addLayout(controls)

        splitter = QSplitter(Qt.Horizontal)
        self.glossary_list = QListWidget()
        self.glossary_list.setMinimumWidth(270)
        self.glossary_list.currentItemChanged.connect(self._on_glossary_selection_changed)
        self.glossary_detail = QTextEdit()
        self.glossary_detail.setReadOnly(True)
        self.glossary_detail.setPlainText("Escribe una palabra o selecciona un término.")
        splitter.addWidget(self.glossary_list)
        splitter.addWidget(self.glossary_detail)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, 1)

        bottom = QHBoxLayout()
        self.copy_glossary_button = QPushButton("Copiar explicación")
        self.copy_glossary_button.clicked.connect(self.copy_glossary_explanation)
        bottom.addStretch(1)
        bottom.addWidget(self.copy_glossary_button)
        layout.addLayout(bottom)
        self._refresh_glossary()
        return page

    # ─── Settings ──────────────────────────────────────────────────

    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(self._section_header(tr("settings.title")))
        theme_row = QHBoxLayout()
        theme_label = QLabel(tr("settings.theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(tr("settings.theme.dark"), "dark")
        self.theme_combo.addItem(tr("settings.theme.light"), "light")
        self.theme_combo.setCurrentIndex(0 if self.settings.get("theme", "dark") == "dark" else 1)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch(1)
        layout.addLayout(theme_row)

        language_row = QHBoxLayout()
        language_label = QLabel(tr("settings.language"))
        self.language_combo = QComboBox()
        self.language_combo.addItem(tr("settings.language.es"), "es")
        self.language_combo.addItem(tr("settings.language.en"), "en")
        self.language_combo.setCurrentIndex(0 if self.settings.get("language", "es") == "es" else 1)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        language_row.addWidget(language_label)
        language_row.addWidget(self.language_combo)
        language_row.addStretch(1)
        layout.addLayout(language_row)

        # Startup mode setting
        mode_row = QHBoxLayout()
        mode_label = QLabel(tr("settings.startup_mode"))
        self.startup_mode_combo = QComboBox()
        self.startup_mode_combo.addItems(["Sencillo", "Extremo"])
        self.startup_mode_combo.setCurrentIndex(0 if self.settings.get("startup_mode", MODE_SIMPLE) == MODE_SIMPLE else 1)
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.startup_mode_combo)
        mode_row.addStretch(1)
        layout.addLayout(mode_row)

        reset = QPushButton(tr("settings.reset"))
        reset.clicked.connect(self.reset_configuration)
        apply_tooltip(reset, "settings_reset")
        layout.addWidget(QLabel(tr("settings.xdg_note")))
        layout.addWidget(reset)
        layout.addStretch(1)
        return page

    # ─── Page management ───────────────────────────────────────────

    def _add_page(self, name: str, widget: QWidget) -> None:
        self.pages[name] = widget
        self.stack.addWidget(widget)

    def _select_page(self, name: str) -> None:
        close_context_help_popovers()
        # Ensure we are in extreme mode when selecting pages
        if self._current_mode != MODE_EXTREME:
            self._switch_to_mode(MODE_EXTREME)
        if name not in self.pages:
            return
        widget = self.pages[name]
        self.stack.setCurrentWidget(widget)
        for key, item in self.nav_items.items():
            item.setChecked(key == name)
        self.settings["last_section"] = name
        save_settings(self._collect_settings())

    # ─── Mode switching ────────────────────────────────────────────

    def _toggle_mode(self) -> None:
        if self._current_mode == MODE_SIMPLE:
            self._switch_to_mode(MODE_EXTREME)
        else:
            self._switch_to_mode(MODE_SIMPLE)

    def _switch_to_mode(self, mode: str) -> None:
        close_context_help_popovers()
        self._current_mode = mode

        if mode == MODE_SIMPLE:
            self.mode_stack.setCurrentIndex(0)
            self.mode_toggle_btn.setText(tr("mode.activate_extreme"))
            self.status_mode.setText(tr("mode.simple_status"))
            self._set_header_status("ok", tr("mode.simple_header"))
            # Sync prompt from extreme to simple
            if hasattr(self, "prompt_edit") and hasattr(self, "simple_prompt_edit"):
                extreme_text = self.prompt_edit.toPlainText()
                simple_text = self.simple_prompt_edit.toPlainText()
                # If only one side has text, sync to the other
                if extreme_text and not simple_text:
                    self.simple_prompt_edit.setPlainText(extreme_text)
                elif simple_text and not extreme_text:
                    self.prompt_edit.blockSignals(True)
                    self.prompt_edit.setPlainText(simple_text)
                    self.prompt_edit.blockSignals(False)
                elif extreme_text and simple_text:
                    # Both have text — if they differ, the extreme mode is more recent
                    # (user was just editing there). BUT only overwrite simple if
                    # the texts actually differ, to avoid unnecessary clears.
                    if extreme_text != simple_text:
                        self.simple_prompt_edit.setPlainText(extreme_text)
            # Sync combos from extreme to simple
            self._sync_combos_extreme_to_simple()
            # Show simple home if no result
            if not self.result:
                self.simple_stack.setCurrentIndex(0)
            else:
                self.simple_stack.setCurrentIndex(1)
        else:
            self.mode_stack.setCurrentIndex(1)
            self.mode_toggle_btn.setText(tr("mode.activate_simple"))
            self.status_mode.setText(tr("mode.extreme_status"))
            self._set_header_status("ok", tr("mode.extreme_header"))
            # Sync prompt from simple to extreme
            if hasattr(self, "simple_prompt_edit") and hasattr(self, "prompt_edit"):
                simple_text = self.simple_prompt_edit.toPlainText()
                extreme_text = self.prompt_edit.toPlainText()
                if simple_text:
                    self.prompt_edit.setPlainText(simple_text)
            # Sync combos from simple to extreme
            self._sync_combos_simple_to_extreme()
            # If there's a result, go to results page
            if self.result:
                self._select_page("resultados")
            else:
                self._select_page("resumen")
            self._apply_mode_visibility()
            # Ensure counters are updated immediately after mode switch (sync used blockSignals)
            self._update_counters()

        save_settings(self._collect_settings())

    def _sync_combos_simple_to_extreme(self) -> None:
        """Sync combo selections from simple mode to extreme mode."""
        if not hasattr(self, "simple_profile_combo"):
            return
        self.profile_combo.setCurrentText(self.simple_profile_combo.currentText())
        self.target_combo.setCurrentText(self.simple_target_combo.currentText())
        # Sync level
        level_data = self.simple_level_combo.currentData()
        self._set_combo_value(self.level_combo, str(level_data) if level_data else "profile_default")
        self.strict_check.setChecked(self.simple_strict_check.isChecked())
        self.preserve_check.setChecked(self.simple_preserve_check.isChecked())
        # Sync privacy
        priv_data = self.simple_privacy_combo.currentData()
        self._set_combo_value(self.privacy_combo, str(priv_data) if priv_data else "full_original")

    def _sync_combos_extreme_to_simple(self) -> None:
        """Sync combo selections from extreme mode to simple mode."""
        if not hasattr(self, "simple_profile_combo"):
            return
        self.simple_profile_combo.setCurrentText(self.profile_combo.currentText())
        self.simple_target_combo.setCurrentText(self.target_combo.currentText())
        # Sync level
        level_data = self.level_combo.currentData()
        self._set_combo_value(self.simple_level_combo, str(level_data) if level_data else "profile_default")
        self.simple_strict_check.setChecked(self.strict_check.isChecked())
        self.simple_preserve_check.setChecked(self.preserve_check.isChecked())
        # Sync privacy
        priv_data = self.privacy_combo.currentData()
        self._set_combo_value(self.simple_privacy_combo, str(priv_data) if priv_data else "full_original")

    # ─── Simple mode helpers ───────────────────────────────────────

    def _on_simple_prompt_changed(self) -> None:
        """When the simple mode prompt text changes, sync to extreme mode."""
        text = self.simple_prompt_edit.toPlainText()
        if hasattr(self, "prompt_edit"):
            self.prompt_edit.blockSignals(True)
            self.prompt_edit.setPlainText(text)
            self.prompt_edit.blockSignals(False)
        # Debounce counter updates to avoid estimate_text() on every keystroke
        self._counters_debounce_timer.start()
        self._sync_simple_combos_to_extreme_on_change()
        # Update profile label
        profile = self.simple_profile_combo.currentText() if hasattr(self, "simple_profile_combo") else "AUTO"
        if profile == "AUTO":
            self.simple_profile_label.setText("Automático recomendado")
        else:
            self.simple_profile_label.setText(profile)

    def _sync_simple_combos_to_extreme_on_change(self) -> None:
        """Lightweight sync of combos from simple to extreme during typing.
        Ensures that if user changed profile/target/level in simple mode
        and then switches to extreme, the values are already there."""
        if not hasattr(self, "simple_profile_combo"):
            return
        self.profile_combo.blockSignals(True)
        self.profile_combo.setCurrentText(self.simple_profile_combo.currentText())
        self.profile_combo.blockSignals(False)

    def _on_extreme_prompt_changed(self) -> None:
        """When the extreme mode prompt text changes, sync to simple mode."""
        # Only sync if we're actually in extreme mode (not during init)
        if self._current_mode != MODE_EXTREME:
            return
        text = self.prompt_edit.toPlainText()
        if hasattr(self, "simple_prompt_edit"):
            # Avoid overwriting if simple already has different content
            # that the user hasn't confirmed (simple is the "safer" source)
            current_simple = self.simple_prompt_edit.toPlainText()
            if text != current_simple:
                self.simple_prompt_edit.blockSignals(True)
                self.simple_prompt_edit.setPlainText(text)
                self.simple_prompt_edit.blockSignals(False)
        # Debounce counter updates to avoid estimate_text() on every keystroke
        self._counters_debounce_timer.start()

    def _toggle_simple_adv_options(self, checked: bool) -> None:
        self.adv_frame.setVisible(checked)
        if checked:
            self.adv_toggle_btn.setText("▾ Opciones avanzadas")
        else:
            self.adv_toggle_btn.setText("▸ Opciones avanzadas")

    def _on_simple_profile_combo_changed(self, text: str) -> None:
        if text == "AUTO":
            self.simple_profile_label.setText("Automático recomendado")
        else:
            self.simple_profile_label.setText(text)

    def _simple_new_compilation(self) -> None:
        """New compilation in simple mode: clear and go back to home."""
        self.result = None
        self.simple_prompt_edit.clear()
        self.simple_stack.setCurrentIndex(0)
        self.simple_progress.setVisible(False)
        self.simple_progress.setValue(0)

    def _show_simple_history(self) -> None:
        """Show history — open extreme mode history / recent results."""
        # The app doesn't have a dedicated history page, but we can
        # show the results page in extreme mode if there's a result.
        if self.result:
            self._switch_to_mode(MODE_EXTREME)
            self._select_page("resultados")
        else:
            QMessageBox.information(self, "Historial", "No hay compilaciones previas en esta sesión.")

    def _open_settings(self) -> None:
        """Open settings — route to the appropriate settings view."""
        if self._current_mode == MODE_EXTREME:
            self._select_page("configuracion")
        else:
            # Switch to extreme mode and go to settings
            self._switch_to_mode(MODE_EXTREME)
            self._select_page("configuracion")

    def _open_help(self) -> None:
        """Open help — route to the appropriate help view."""
        if self._current_mode == MODE_EXTREME:
            self._select_page("glosario")
        else:
            self._switch_to_mode(MODE_EXTREME)
            self._select_page("glosario")

    # ─── Settings persistence ──────────────────────────────────────

    def _on_theme_changed(self, index: int) -> None:
        theme = "dark" if index == 0 else "light"
        self.settings["theme"] = theme
        self.setStyleSheet(get_qss(theme))
        save_settings(self._collect_settings())

    def _on_language_changed(self, index: int) -> None:
        language = "es" if index == 0 else "en"
        self.settings["language"] = set_language(language)
        # Keep this intentionally lightweight: full widgets are rebuilt on next launch.
        if hasattr(self, "mode_toggle_btn"):
            self.mode_toggle_btn.setText(tr("mode.activate_extreme") if self._current_mode == MODE_SIMPLE else tr("mode.activate_simple"))
        self._set_header_status("ok", tr("status.ready"))
        save_settings(self._collect_settings())

    def _restore_settings(self) -> None:
        self.profile_combo.setCurrentText(str(self.settings["profile"]))
        self.target_combo.setCurrentText(str(self.settings["target"]))
        self.level_combo.setCurrentText(str(self.settings["level"]))
        self._set_combo_value(self.level_combo, str(self.settings["level"]))
        self.strict_check.setChecked(bool(self.settings["strict_validation"]))
        self.preserve_check.setChecked(bool(self.settings["preserve_original"]))
        if hasattr(self, "privacy_combo"):
            self.privacy_combo.setCurrentText(str(self.settings.get("privacy_mode", "full_original")))
            self._set_combo_value(self.privacy_combo, str(self.settings.get("privacy_mode", "full_original")))
        if hasattr(self, "custom_model_edit"):
            self.custom_model_edit.setText(str(self.settings.get("custom_model_name", "")))
        output_dir = str(self.settings.get("output_dir", ""))
        self.last_saved_dir = Path(output_dir) if output_dir else None

        # Sync extreme combos to simple combos
        self._sync_combos_extreme_to_simple()

        # Restore mode — default to simple (redesign default)
        # Legacy advanced_mode is respected only if startup_mode is also set to extreme
        startup_mode = str(self.settings.get("startup_mode", MODE_SIMPLE))
        # Only consider legacy advanced_mode if no startup_mode was ever explicitly set
        if startup_mode == MODE_SIMPLE and bool(self.settings.get("advanced_mode", False)):
            # Legacy user had advanced on, but redesign default is simple.
            # Respect their preference only if they explicitly chose extreme before.
            if self.settings.get("startup_mode", "") == "":
                startup_mode = MODE_EXTREME
        self._switch_to_mode(startup_mode)

        self._apply_mode_visibility()

        # Restore last section only in extreme mode
        if self._current_mode == MODE_EXTREME:
            last_section = str(self.settings.get("last_section", "resumen"))
            _legacy_map = {
                "Panel principal": "resumen",
                "Compilador": "compilar",
                "Resultados": "resultados",
                "Validación": "validacion",
                "Perfiles": "perfiles",
                "Reglas y modelos": "compilar",
                "Configuración": "configuracion",
                "Ayuda": "glosario",
                "Glosario": "glosario",
                "Acerca de": "configuracion",
                "Seeds y modelos": "compilar",
            }
            last_section = _legacy_map.get(last_section, last_section)
            if last_section not in self.pages:
                last_section = "resumen"
            self._select_page(last_section)

    def _collect_settings(self) -> dict:
        return {
            "advanced_mode": self._current_mode == MODE_EXTREME,
            "startup_mode": self._current_mode,
            "theme": self.settings.get("theme", "dark"),
            "language": self.settings.get("language", "es"),
            "profile": self.profile_combo.currentText() if hasattr(self, "profile_combo") else "AUTO",
            "target": self.target_combo.currentText() if hasattr(self, "target_combo") else "codex",
            "level": self._combo_value(self.level_combo) if hasattr(self, "level_combo") else "profile_default",
            "strict_validation": self.strict_check.isChecked() if hasattr(self, "strict_check") else False,
            "preserve_original": self.preserve_check.isChecked() if hasattr(self, "preserve_check") else True,
            "privacy_mode": self._combo_value(self.privacy_combo) if hasattr(self, "privacy_combo") else "full_original",
            "custom_model_name": self.custom_model_edit.text() if hasattr(self, "custom_model_edit") else "",
            "last_section": next((name for name, widget in self.pages.items() if widget is self.stack.currentWidget()), "resumen") if hasattr(self, "stack") else "resumen",
            "window_width": self.width(),
            "window_height": self.height(),
            "output_dir": self.settings.get("output_dir", ""),
        }

    # ─── Shortcuts ─────────────────────────────────────────────────

    def _bind_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.new_prompt)
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.load_file)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.save_all)
        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self.compile_current)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self, activated=self.copy_recommended)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.new_prompt)
        QShortcut(QKeySequence("F1"), self, activated=lambda: self._open_help())
        # Mode switch shortcut
        QShortcut(QKeySequence("Ctrl+M"), self, activated=self._toggle_mode)

    # ─── Mode visibility (extreme mode tab filtering) ──────────────

    def _apply_mode_visibility(self) -> None:
        """In extreme mode, always show all tabs. Legacy compatibility."""
        if not hasattr(self, "tabs"):
            return
        # All tabs visible in extreme mode
        for index in range(self.tabs.count()):
            self.tabs.setTabVisible(index, True)

    # ─── Counters ──────────────────────────────────────────────────

    def _update_counters(self) -> None:
        # Determine which prompt edit is the active one
        text = ""
        if self._current_mode == MODE_SIMPLE and hasattr(self, "simple_prompt_edit"):
            text = self.simple_prompt_edit.toPlainText()
        elif hasattr(self, "prompt_edit"):
            text = self.prompt_edit.toPlainText()

        chars, tokens = estimate_counters(text)
        for lbl in (self.char_label, getattr(self, "char_label2", None)):
            if lbl:
                lbl.setText(f"{chars} caracteres")
        for lbl in (self.token_label, getattr(self, "token_label2", None)):
            if lbl:
                lbl.setText(f"{tokens} tokens aprox.")
        # Sync compiler_prompt mirror
        if hasattr(self, "compiler_prompt"):
            self.compiler_prompt.setPlainText(text)

    # ─── Status ────────────────────────────────────────────────────

    def _set_header_status(self, state: str, text: str) -> None:
        self.header_chip.set_state(state)
        self.header_chip.set_text(text)

    def _set_status(self, message: str, profile: str, validation: str, path: str) -> None:
        self.status_label.setText(message)
        self.status_profile.setText(f"Perfil: {profile}")
        state = validation.lower().strip().replace(" ", "_") or "normal"
        if state in ("normal", "pass"):
            self._set_header_status("ok", message)
            self.status_dot.setStyleSheet("background: #30B87A; border-radius: 3px;")
        elif state in ("procesando", "warning"):
            self._set_header_status("info", message)
            self.status_dot.setStyleSheet("background: #4CB8F5; border-radius: 3px;")
        elif state in ("error", "bloqueado", "blocked", "fail"):
            self._set_header_status("error", message)
            self.status_dot.setStyleSheet("background: #E04E65; border-radius: 3px;")
        elif state == "cancelado":
            self._set_header_status("warn", message)
            self.status_dot.setStyleSheet("background: #E5A51A; border-radius: 3px;")
        else:
            self._set_header_status("ok", message)

    # ─── Combo helpers ─────────────────────────────────────────────

    def _combo_value(self, combo: QComboBox) -> str:
        value = combo.currentData()
        return str(value if value is not None else combo.currentText())

    def _set_combo_value(self, combo: QComboBox, value: str) -> None:
        for index in range(combo.count()):
            if combo.itemData(index) == value or combo.itemText(index) == value:
                combo.setCurrentIndex(index)
                return

    def _on_target_changed(self, target: str) -> None:
        if hasattr(self, "custom_model_edit"):
            self.custom_model_edit.setVisible(target == "custom")

    # ─── Compile request building ──────────────────────────────────

    def _build_compile_request(self) -> dict | None:
        """Build a compile request from the current mode's UI state."""
        if self._current_mode == MODE_SIMPLE:
            prompt = self.simple_prompt_edit.toPlainText().strip()
            if not prompt:
                QMessageBox.warning(self, "Entrada vacía", "Escribe o carga un prompt antes de compilar.")
                return None
            return {
                "prompt": prompt,
                "target": self.simple_target_combo.currentText(),
                "profile": self.simple_profile_combo.currentText(),
                "level": self._combo_value(self.simple_level_combo),
                "strict": self.simple_strict_check.isChecked(),
                "preserve_original": self.simple_preserve_check.isChecked(),
                "privacy_mode": self._combo_value(self.simple_privacy_combo),
                "custom_model_name": "",  # not exposed in simple advanced options
            }
        else:
            prompt = self.prompt_edit.toPlainText().strip()
            if not prompt:
                QMessageBox.warning(self, "Entrada vacía", "Escribe o carga un prompt antes de compilar.")
                return None
            return {
                "prompt": prompt,
                "target": self.target_combo.currentText(),
                "profile": self.profile_combo.currentText(),
                "level": self._combo_value(self.level_combo),
                "strict": self.strict_check.isChecked(),
                "preserve_original": self.preserve_check.isChecked(),
                "privacy_mode": self._combo_value(self.privacy_combo),
                "custom_model_name": self.custom_model_edit.text(),
            }

    # ─── Actions ───────────────────────────────────────────────────

    def new_prompt(self) -> None:
        self.result = None
        # Always reset both modes' UI
        if hasattr(self, "simple_prompt_edit"):
            self.simple_prompt_edit.clear()
        if hasattr(self, "simple_stack"):
            self.simple_stack.setCurrentIndex(0)
        if hasattr(self, "simple_progress"):
            self.simple_progress.setVisible(False)
            self.simple_progress.setValue(0)
        if hasattr(self, "prompt_edit"):
            self.prompt_edit.clear()
        if hasattr(self, "progress"):
            self.progress.setValue(0)
        self.progress_strip.setValue(0)
        if hasattr(self, "scan_ring"):
            self.scan_ring.set_value("—")
            self.scan_ring.set_state("idle")
        self._set_status("Nuevo prompt", self._get_current_profile(), "normal", "")

    def paste_prompt(self) -> None:
        text = QApplication.clipboard().text()
        if self._current_mode == MODE_SIMPLE:
            self.simple_prompt_edit.insertPlainText(text)
        else:
            self.prompt_edit.insertPlainText(text)

    def load_example(self) -> None:
        if EXAMPLE_PATH.exists():
            content = EXAMPLE_PATH.read_text(encoding="utf-8")
            if self._current_mode == MODE_SIMPLE:
                self.simple_prompt_edit.setPlainText(content)
            else:
                self.prompt_edit.setPlainText(content)
                self._select_page("compilar")

    def load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Cargar prompt", str(ROOT), "Textos (*.txt *.md);;Todos (*)")
        if path:
            content = Path(path).read_text(encoding="utf-8")
            if self._current_mode == MODE_SIMPLE:
                self.simple_prompt_edit.setPlainText(content)
            else:
                self.prompt_edit.setPlainText(content)

    def analyze_only(self) -> None:
        self.compile_current()
        self._switch_to_mode(MODE_EXTREME)
        self._select_page("validacion")

    def compile_auto(self) -> None:
        if self._current_mode == MODE_SIMPLE:
            self.simple_profile_combo.setCurrentText("AUTO")
        else:
            self.profile_combo.setCurrentText("AUTO")
        if self._current_mode == MODE_SIMPLE:
            self._switch_to_mode(MODE_SIMPLE)
        else:
            self._select_page("resumen")
        prompt = self._get_current_prompt()
        if prompt.strip():
            self.compile_current()

    def compile_current(self) -> None:
        prompt = self._get_current_prompt().strip()
        if not prompt:
            QMessageBox.warning(self, "Entrada vacía", "Escribe o carga un prompt antes de compilar.")
            return
        if self.worker_thread and self.worker_thread.isRunning():
            return
        self.cancel_requested = False

        request = self._build_compile_request()
        if request is None:
            return

        # Show progress in the current mode
        if self._current_mode == MODE_SIMPLE:
            self.simple_progress.setVisible(True)
            self.simple_progress.setValue(0)
            self.simple_compile_btn.setEnabled(False)
            self.simple_cancel_btn.setVisible(True)
            self.simple_cancel_btn.setEnabled(True)
        else:
            self.cancel_button.setVisible(True)
            self.cancel_button.setEnabled(True)
            self.compile_button.setEnabled(False)
            self.compile_hero_btn.setEnabled(False)

        self.worker_thread = QThread(self)
        self.worker = CompileWorker(self.controller, request)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.failed.connect(self._on_worker_failed)
        self.worker.canceled.connect(self._on_worker_canceled)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker.canceled.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.failed.connect(self.worker.deleteLater)
        self.worker.canceled.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def cancel_compile(self) -> None:
        self.cancel_requested = True
        if self.worker:
            self.worker.cancel()
        self._set_status("Cancelación solicitada", self._get_current_profile(), "procesando", "")

    # ─── Current state helpers ─────────────────────────────────────

    def _get_current_prompt(self) -> str:
        if self._current_mode == MODE_SIMPLE and hasattr(self, "simple_prompt_edit"):
            return self.simple_prompt_edit.toPlainText()
        elif hasattr(self, "prompt_edit"):
            return self.prompt_edit.toPlainText()
        return ""

    def _get_current_profile(self) -> str:
        if self._current_mode == MODE_SIMPLE and hasattr(self, "simple_profile_combo"):
            return self.simple_profile_combo.currentText()
        elif hasattr(self, "profile_combo"):
            return self.profile_combo.currentText()
        return "AUTO"

    # ─── Worker callbacks ──────────────────────────────────────────

    @Slot(int, str)
    def _on_worker_progress(self, value: int, label: str) -> None:
        # Guard: skip GUI updates if cancellation was requested or the
        # window is being closed — avoids writing to destroyed widgets.
        if self.cancel_requested:
            return
        if hasattr(self, "progress"):
            self.progress.setValue(value)
        self.progress_strip.setValue(value)
        if hasattr(self, "scan_ring"):
            self.scan_ring.scanning_progress(value)
        if hasattr(self, "hero_status"):
            self.hero_status.setText(f"Progreso: {value}%")
        if self._current_mode == MODE_SIMPLE and hasattr(self, "simple_progress"):
            self.simple_progress.setValue(value)
        if self._current_mode == MODE_SIMPLE and hasattr(self, "simple_scan_ring"):
            self.simple_scan_container.show()
            self.simple_scan_ring.show()
            self.simple_scan_ring.scanning_progress(value)
            self.simple_scan_status.setText(f"{value}%")
        self._set_status(label, self._get_current_profile(), "procesando", "")

    @Slot(dict)
    def _on_worker_finished(self, result: dict) -> None:
        self.result = result
        if hasattr(self, "progress"):
            self.progress.setValue(100)
        self.progress_strip.setValue(100)
        self._render_result()
        save_settings(self._collect_settings())

        if self._current_mode == MODE_SIMPLE:
            # Show simple result view
            self.simple_stack.setCurrentIndex(1)
            self.simple_progress.setVisible(False)
            self.simple_compile_btn.setEnabled(True)
            self.simple_cancel_btn.setVisible(False)
        else:
            self._select_page("resultados")
            self.cancel_button.setVisible(False)
            self.compile_button.setEnabled(True)
            self.compile_hero_btn.setEnabled(True)

        self.worker = None
        self.worker_thread = None

    @Slot(str)
    def _on_worker_failed(self, message: str) -> None:
        if hasattr(self, "progress"):
            self.progress.setValue(0)
        self.progress_strip.setValue(0)
        if hasattr(self, "scan_ring"):
            self.scan_ring.set_state("error")
        self._set_status("Error", self._get_current_profile(), "error", "")

        if self._current_mode == MODE_SIMPLE:
            self.simple_progress.setVisible(False)
            self.simple_compile_btn.setEnabled(True)
            self.simple_cancel_btn.setVisible(False)
            # Show error in simple result header
            self.simple_result_header.setText("✗ Error al compilar")
            self.simple_result_header.setProperty("errorState", True)
            for w in (self.simple_result_header,):
                w.style().unpolish(w)
                w.style().polish(w)
            self.simple_optimized_tab.setPlainText(message)
            self.simple_stack.setCurrentIndex(1)
        else:
            self.cancel_button.setVisible(False)
            self.compile_button.setEnabled(True)
            self.compile_hero_btn.setEnabled(True)

        self.worker = None
        self.worker_thread = None
        QMessageBox.critical(self, "Error al compilar", message)

    @Slot()
    def _on_worker_canceled(self) -> None:
        if hasattr(self, "progress"):
            self.progress.setValue(0)
        self.progress_strip.setValue(0)
        if hasattr(self, "scan_ring"):
            self.scan_ring.set_value("—")
            self.scan_ring.set_state("idle")
        if hasattr(self, "hero_status"):
            self.hero_status.setText("Cancelado.")

        if self._current_mode == MODE_SIMPLE:
            self.simple_progress.setVisible(False)
            self.simple_compile_btn.setEnabled(True)
            self.simple_cancel_btn.setVisible(False)
        else:
            self.cancel_button.setVisible(False)
            self.compile_button.setEnabled(True)
            self.compile_hero_btn.setEnabled(True)

        self._set_status("Cancelado", self._get_current_profile(), "cancelado", "")
        self.worker = None
        self.worker_thread = None

    # ─── Result rendering ──────────────────────────────────────────

    def _render_result(self) -> None:
        if not self.result:
            self._set_status(tr("error.no_result"), self._get_current_profile(), "error", "")
            return
        result = self.result
        validation = result["context_loss_report"]
        score = validation.get("score", 0)
        profile = result["applied_profile"]

        # Circle (extreme mode)
        if hasattr(self, "scan_ring"):
            self.scan_ring.scanning_finish(score)
        if hasattr(self, "hero_status"):
            self.hero_status.setText(f"{score}/100 — Copia el prompt listo para usar.")

        # Result cards (extreme mode)
        if hasattr(self, "extreme_health"):
            warnings_count_r = len(validation.get("warnings", []))
            errors_count_r = len(validation.get("critical_losses", []))
            constraints_count_r = len(validation.get("critical_constraints_preserved", []))
            self.extreme_health.update_metrics(
                score=score,
                constraints=constraints_count_r,
                warnings=warnings_count_r,
                errors=errors_count_r,
            )
        if hasattr(self, "card_preservation"):  # legacy: removed in 2026-06-11 polish
            self.card_preservation.set_value(str(score))
            self.card_preservation.set_semantic("success" if score >= 85 else "warning" if score >= 60 else "error")
        if hasattr(self, "card_constraints"):  # legacy
            constraints_count = len(validation.get("critical_constraints_preserved", []))
            self.card_constraints.set_value(str(constraints_count))
            self.card_constraints.set_semantic("success" if constraints_count > 0 else "muted")
        if hasattr(self, "card_warnings"):  # legacy
            warnings_count = len(validation.get("warnings", []))
            self.card_warnings.set_value(str(warnings_count))
            self.card_warnings.set_semantic("warning" if warnings_count > 0 else "muted")
        if hasattr(self, "card_errors"):  # legacy
            self.card_errors.set_value("0")
            self.card_errors.set_semantic("muted")

        # Extreme mode text tabs
        if hasattr(self, "summary_text"):
            self.summary_text.setPlainText(
                f"Perfil solicitado: {result['requested_profile']}\n"
                f"Perfil aplicado: {profile}\n"
                f"Motivo AUTO: {result.get('auto_info', {}).get('selection_reason', 'manual')}\n"
                f"Huella digital (SHA-256): {result['prompt_sha256']}\n"
                f"Puntuación de preservación: {score}/100\n"
                f"retention_score: {validation.get('retention_score', score)}\n"
                f"precision_score: {validation.get('precision_score', 0)}\n"
                f"unsupported_addition_score: {validation.get('unsupported_addition_score', 0)}\n"
                f"nsl_size_ratio: {validation.get('nsl_size_ratio', validation.get('compression_ratio_nsl', 0))}\n"
                f"execution_size_ratio: {validation.get('execution_size_ratio', validation.get('expansion_ratio_execution_prompt', 0))}\n"
                f"Restricciones preservadas: {', '.join(validation.get('critical_constraints_preserved', [])) or 'ninguna detectada'}\n"
                f"Advertencias: {', '.join(validation.get('warnings', [])) or 'ninguna'}\n"
                "Siguiente acción recomendada: copia el Prompt listo para usar."
            )
        if hasattr(self, "original_text"):
            self.original_text.setPlainText(result["original"] if result.get("privacy_mode") == "full_original" else "[omitido por modo de privacidad]")
        if hasattr(self, "hybrid_text"):
            self.hybrid_text.setPlainText(result["hybrid_markdown"])
        if hasattr(self, "optimized_text"):
            self.optimized_text.setPlainText(result["optimized_prompt"])
        if hasattr(self, "nsl_text"):
            self.nsl_text.setPlainText(result["chosen_nsl"])
        if hasattr(self, "json_text"):
            self.json_text.setPlainText(json.dumps(result["hybrid_json"], indent=2, ensure_ascii=False))
        if hasattr(self, "seeds_text"):
            self.seeds_text.setPlainText(json.dumps(result["seeds"], indent=2, ensure_ascii=False))
        if hasattr(self, "constraints_text"):
            self.constraints_text.setPlainText(json.dumps(result["semantic_ir"].get("effective_prompt_ir", {}), indent=2, ensure_ascii=False))
        if hasattr(self, "validation_text"):
            self.validation_text.setPlainText(result["context_loss_markdown"])
        if hasattr(self, "validation_detail"):
            self.validation_detail.setPlainText(result["context_loss_markdown"])
        if hasattr(self, "profile_text"):
            self.profile_text.setPlainText(json.dumps(result["profile_status"], indent=2, ensure_ascii=False))

        # ─── Simple mode result rendering ──────────────────────────
        self.simple_result_header.setText("✓ Prompt generado correctamente")
        self.simple_result_header.setProperty("errorState", False)
        for w in (self.simple_result_header,):
            w.style().unpolish(w)
            w.style().polish(w)

        self.simple_optimized_tab.setPlainText(result["optimized_prompt"])
        self.simple_report_tab.setPlainText(result["hybrid_markdown"])
        self.simple_validation_tab.setPlainText(result["context_loss_markdown"])

        # Compact metrics
        constraints_count = len(validation.get("critical_constraints_preserved", []))
        files_count = len(self.controller.last_result.get("generated_files", [])) if self.controller.last_result else 0
        self.simple_metrics_label.setText(
            f"Preservación: {score} % · {constraints_count} restricciones · {files_count} archivos"
        )

        # ── Premium: update compact scan ring + health dashboard ──
        if hasattr(self, "simple_scan_ring"):
            self.simple_scan_ring.scanning_finish(score)
            self.simple_scan_status.setText(f"{score}/100")
        if hasattr(self, "simple_health"):
            warnings_count = len(validation.get("warnings", []))
            errors_count = len(validation.get("critical_losses", []))
            self.simple_health.update_metrics(
                score=score,
                constraints=constraints_count,
                warnings=warnings_count,
                errors=errors_count,
            )

        # Generated files info
        if self.last_saved_dir and self.last_saved_dir.exists():
            self.simple_files_label.setText(f"Carpeta: {self.last_saved_dir}")
            self.simple_open_files_btn.setVisible(True)
        else:
            self.simple_files_label.setText("")
            self.simple_open_files_btn.setVisible(False)

        if validation.get("strict_status") == "blocked":
            self._set_status("Bloqueado por strict", profile, "bloqueado", "")
        else:
            self._set_status("Completado", profile, validation.get("profile_status", "pass"), "")

    # ─── Clip/save ─────────────────────────────────────────────────

    def copy_recommended(self) -> None:
        if self.result:
            text = self.result.get("optimized_prompt", "")
        elif hasattr(self, "optimized_text"):
            text = self.optimized_text.toPlainText()
        else:
            text = ""
        if text:
            QApplication.clipboard().setText(text)
            self._set_status("Prompt listo copiado", self._get_current_profile(), "normal", "")

    def copy_json(self) -> None:
        QApplication.clipboard().setText(self.json_text.toPlainText())
        self._set_status("JSON para programas copiado", self._get_current_profile(), "normal", "")

    def save_all(self) -> None:
        if not self.result:
            QMessageBox.warning(self, "Sin resultado", "Compila un prompt antes de guardar.")
            return
        default = self.settings.get("output_dir") or str(data_dir() / "outputs")
        path = QFileDialog.getExistingDirectory(self, "Carpeta de salida", default)
        if not path:
            return
        artifacts = self.controller.save_all(path)
        self.settings["output_dir"] = path
        self.last_saved_dir = Path(path)
        save_settings(self._collect_settings())

        # Update simple mode file info
        if hasattr(self, "simple_files_label"):
            self.simple_files_label.setText(f"Carpeta: {path}")
            self.simple_open_files_btn.setVisible(True)
        if hasattr(self, "simple_metrics_label") and self.result:
            validation = self.result["context_loss_report"]
            score = validation.get("score", 0)
            constraints_count = len(validation.get("critical_constraints_preserved", []))
            self.simple_metrics_label.setText(
                f"Preservación: {score} % · {constraints_count} restricciones · {len(artifacts)} archivos"
            )

        self._set_status(f"{len(artifacts)} archivos generados", self.result["applied_profile"], self.result["context_loss_report"].get("profile_status", "pass"), path)

    def open_last_output(self) -> None:
        configured_output = str(self.settings.get("output_dir", "")).strip()
        candidate = self.last_saved_dir or (Path(configured_output) if configured_output else None)
        if candidate is None or not candidate.exists():
            QMessageBox.information(self, "Sin carpeta exportada", "Guarda primero los resultados para abrir la carpeta.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(candidate)))
        self._set_status("Carpeta abierta", self._get_current_profile(), "normal", str(candidate))

    def reset_configuration(self) -> None:
        reset_settings()
        self.settings = load_settings()
        self._restore_settings()
        self._set_status("Configuración restablecida", self._get_current_profile(), "normal", "")

    # ─── Glossary ──────────────────────────────────────────────────

    def _refresh_glossary(self) -> None:
        if not hasattr(self, "glossary_list"):
            return
        current_id = self.glossary_list.currentItem().data(Qt.UserRole) if self.glossary_list.currentItem() else ""
        query = self.glossary_search.text() if hasattr(self, "glossary_search") else ""
        category = self.glossary_category.currentText() if hasattr(self, "glossary_category") else "Todas"
        matches = search_glossary(query, category)
        self.glossary_list.clear()
        for entry in matches:
            item = QListWidgetItem(f"{entry['term']}  ·  {entry['simple_name']}")
            item.setData(Qt.UserRole, entry["id"])
            self.glossary_list.addItem(item)
            if entry["id"] == current_id:
                self.glossary_list.setCurrentItem(item)
        self.glossary_count.setText(f"{len(load_glossary())} términos disponibles")
        if not matches:
            self.glossary_detail.setPlainText("No se encontraron términos. Prueba otra palabra.")
            return
        if not self.glossary_list.currentItem() and query:
            self.glossary_list.setCurrentRow(0)
        elif not query and not self.glossary_list.currentItem():
            self.glossary_detail.setPlainText("Escribe una palabra o selecciona un término.")

    def _on_glossary_selection_changed(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            return
        entry = get_entry(str(current.data(Qt.UserRole)))
        if entry:
            self.glossary_detail.setPlainText(format_entry(entry, self._current_mode == MODE_EXTREME))

    def open_glossary_term(self, term_id: str | None) -> None:
        self._switch_to_mode(MODE_EXTREME)
        self._select_page("glosario")
        if not term_id:
            self.glossary_search.setFocus(Qt.OtherFocusReason)
            return
        entry = get_entry(term_id)
        self.glossary_search.setText(entry["term"] if entry else term_id)
        self._refresh_glossary()
        for index in range(self.glossary_list.count()):
            item = self.glossary_list.item(index)
            if item.data(Qt.UserRole) == (entry["id"] if entry else term_id):
                self.glossary_list.setCurrentItem(item)
                break
        self.glossary_search.setFocus(Qt.OtherFocusReason)

    def copy_glossary_explanation(self) -> None:
        QApplication.clipboard().setText(self.glossary_detail.toPlainText())
        self._set_status("Explicación copiada", self._get_current_profile(), "normal", "")

    # ─── Close ─────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        # Cancel any running worker thread before closing to avoid
        # signals hitting destroyed widgets or zombie threads.
        if self.worker_thread and self.worker_thread.isRunning():
            self.cancel_requested = True
            if self.worker:
                self.worker.cancel()
            self.worker_thread.quit()
            self.worker_thread.wait(3000)
        save_settings(self._collect_settings())
        super().closeEvent(event)
