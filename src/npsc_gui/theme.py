"""NPSC Theme — Hybrid Premium for KDE X11 + GTX 660 legacy.

Principles:
- Solid colors only (no gradients, no rgba alpha blending beyond chip backgrounds)
- Hybrid visual language: Driver Booster circle + Auslogics modularity
- Blue #2B8BC8 as primary accent (distinct from Breeze #3DAEE9)
- Full focus indicators for accessibility
- Light and dark mode support
- Zero GPU-expensive effects
- Semantic colors: green=OK, amber=warning, red=error, blue=info
"""

# ─── Color Tokens ────────────────────────────────────────────────────────────
_DARK = dict(
    bg_base       = "#1A1D20",
    bg_surface    = "#21242A",
    bg_card       = "#272B32",
    bg_elevated   = "#2F333B",
    bg_input      = "#1C1F22",
    bg_sidebar    = "#1E2126",
    bg_header     = "#21242A",
    bg_status     = "#1E2126",
    bg_button     = "#2F333B",
    bg_button_hover = "#3A3F48",
    bg_button_pressed = "#4B5560",

    border_subtle  = "#363A42",
    border_input   = "#4A5060",
    border_focus   = "#2B8BC8",
    border_accent  = "#2B8BC8",

    text_primary   = "#E8EAED",
    text_secondary = "#A4A8AE",
    text_muted     = "#6C717A",
    text_button    = "#E8EAED",
    text_on_accent = "#FFFFFF",

    accent_primary  = "#2B8BC8",
    accent_hover    = "#3CA4E0",
    accent_pressed  = "#1E6FA5",
    accent_brand    = "#4CB8F5",

    state_success = "#30B87A",
    state_warning = "#E5A51A",
    state_error   = "#E04E65",
    state_info    = "#4CB8F5",

    chip_ok_bg     = "rgba(48,184,122,0.12)",
    chip_ok_fg     = "#30B87A",
    chip_warn_bg   = "rgba(229,165,26,0.12)",
    chip_warn_fg   = "#E5A51A",
    chip_error_bg  = "rgba(224,78,101,0.12)",
    chip_error_fg  = "#E04E65",
    chip_info_bg   = "rgba(76,184,245,0.12)",
    chip_info_fg   = "#4CB8F5",

    nav_active_bg   = "rgba(43,139,200,0.10)",
    nav_active_border = "#4CB8F5",

    circle_idle_border  = "#363A42",
    circle_active_border = "#2B8BC8",
    circle_success_border = "#30B87A",
    circle_error_border   = "#E04E65",
)

_LIGHT = dict(
    bg_base       = "#F5F6F7",
    bg_surface    = "#FFFFFF",
    bg_card       = "#FFFFFF",
    bg_elevated   = "#EDEEF0",
    bg_input      = "#FFFFFF",
    bg_sidebar    = "#F0F1F3",
    bg_header     = "#FFFFFF",
    bg_status     = "#F0F1F3",
    bg_button     = "#E0E2E4",
    bg_button_hover = "#D0D2D4",
    bg_button_pressed = "#B8BABC",

    border_subtle  = "#D0D2D4",
    border_input   = "#A8ACAE",
    border_focus   = "#2B8BC8",
    border_accent  = "#2B8BC8",

    text_primary   = "#1A1D20",
    text_secondary = "#5A5E64",
    text_muted     = "#8A8E94",
    text_button    = "#1A1D20",
    text_on_accent = "#FFFFFF",

    accent_primary  = "#2B8BC8",
    accent_hover    = "#3CA4E0",
    accent_pressed  = "#1E6FA5",
    accent_brand    = "#4CB8F5",

    state_success = "#22915C",
    state_warning = "#C28A10",
    state_error   = "#C43048",
    state_info    = "#2B8BC8",

    chip_ok_bg     = "rgba(34,145,92,0.10)",
    chip_ok_fg     = "#22915C",
    chip_warn_bg   = "rgba(194,138,16,0.10)",
    chip_warn_fg   = "#C28A10",
    chip_error_bg  = "rgba(196,48,72,0.10)",
    chip_error_fg  = "#C43048",
    chip_info_bg   = "rgba(43,139,200,0.10)",
    chip_info_fg   = "#2B8BC8",

    nav_active_bg   = "rgba(43,139,200,0.08)",
    nav_active_border = "#2B8BC8",

    circle_idle_border  = "#D0D2D4",
    circle_active_border = "#2B8BC8",
    circle_success_border = "#22915C",
    circle_error_border   = "#C43048",
)


def _build_qss(c: dict) -> str:
    """Build QSS from color tokens."""
    return f"""
/* ─── Global ──────────────────────────────────────────────────── */
*
{{
    font-family: Inter, "Noto Sans", "Segoe UI", sans-serif;
    font-size: 10.5pt;
}}

QMainWindow, QWidget
{{
    background: {c['bg_base']};
    color: {c['text_primary']};
}}

/* ─── Header ──────────────────────────────────────────────────── */
QFrame#Header
{{
    background: {c['bg_surface']};
    border-bottom: 1px solid {c['border_subtle']};
}}

/* ─── Status Bar ──────────────────────────────────────────────── */
QFrame#StatusBar
{{
    background: {c['bg_surface']};
    border-top: 1px solid {c['border_subtle']};
}}

/* ─── Sidebar ─────────────────────────────────────────────────── */
QFrame#Sidebar
{{
    background: {c['bg_sidebar']};
    border-right: 1px solid {c['border_subtle']};
}}

/* ─── Brand ───────────────────────────────────────────────────── */
QLabel#BrandGlyph
{{
    color: #FFFFFF;
    background: {c['accent_primary']};
    border-radius: 6px;
    font-size: 14px;
    font-weight: 800;
}}

QLabel#AppTitle
{{
    font-size: 13px;
    font-weight: 700;
    color: {c['text_primary']};
}}

QLabel#Muted, QLabel.Muted
{{
    color: {c['text_muted']};
}}

QLabel#SectionTitle
{{
    font-size: 12px;
    font-weight: 700;
    color: {c['text_secondary']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-top: 4px;
    padding-bottom: 2px;
    background: transparent;
    border: none;
}}

/* ─── Buttons ─────────────────────────────────────────────────── */
QPushButton
{{
    background: {c['bg_button']};
    color: {c['text_button']};
    border: 1px solid {c['border_subtle']};
    border-radius: 5px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 11px;
    min-height: 18px;
}}
QPushButton:hover
{{
    background: {c['bg_button_hover']};
    border-color: {c['accent_brand']};
}}
QPushButton:pressed, QPushButton:checked
{{
    background: {c['bg_button_pressed']};
    color: {c['text_primary']};
    border-color: {c['accent_primary']};
}}
QPushButton:disabled
{{
    background: {c['bg_base']};
    color: {c['text_muted']};
    border-color: {c['border_subtle']};
}}
QPushButton:focus
{{
    border: 2px solid {c['border_focus']};
    outline: none;
}}

/* ─── Primary Button ──────────────────────────────────────────── */
QPushButton#PrimaryButton
{{
    background: {c['accent_primary']};
    color: {c['text_on_accent']};
    font-weight: 700;
    border-color: {c['accent_primary']};
    padding: 8px 18px;
    font-size: 11.5px;
    letter-spacing: 0.3px;
}}
QPushButton#PrimaryButton:hover
{{
    background: {c['accent_hover']};
    border-color: {c['accent_hover']};
}}
QPushButton#PrimaryButton:pressed
{{
    background: {c['accent_pressed']};
    border-color: {c['accent_pressed']};
}}
QPushButton#PrimaryButton:focus
{{
    border: 2px solid {c['border_focus']};
}}

QPushButton#HeaderIconButton
{{
    padding: 0px;
    background: transparent;
    border: 1px solid {c['border_subtle']};
    color: {c['text_secondary']};
    border-radius: 5px;
    font-size: 13px;
}}
QPushButton#HeaderIconButton:hover
{{
    background: {c['bg_elevated']};
    color: {c['text_primary']};
}}

QPushButton#DangerButton
{{
    background: transparent;
    color: {c['state_error']};
    border-color: {c['border_subtle']};
}}
QPushButton#DangerButton:hover
{{
    background: {c['chip_error_bg']};
}}

/* ─── Navigation ──────────────────────────────────────────────── */
QPushButton#NPSCNavItem
{{
    text-align: left;
    padding: 7px 14px;
    background: transparent;
    border: none;
    border-left: 2px solid transparent;
    color: {c['text_secondary']};
    border-radius: 0;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton#NPSCNavItem:hover
{{
    background: {c['bg_elevated']};
    color: {c['text_primary']};
}}
QPushButton#NPSCNavItem:checked
{{
    background: {c['nav_active_bg']};
    border-left: 2px solid {c['nav_active_border']};
    color: {c['accent_brand']};
    font-weight: 600;
}}

QLabel#NavGroupLabel
{{
    padding: 6px 14px 4px;
    font-size: 9.5px;
    color: {c['text_muted']};
    font-weight: 700;
    text-transform: uppercase;
}}

/* ─── Circle Indicator ────────────────────────────────────────── */
QFrame#NPSCCircle
{{
    background: transparent;
    border: 4px solid {c['circle_idle_border']};
}}
QFrame#NPSCCircle[circleState="active"]
{{
    border-color: {c['circle_active_border']};
}}
QFrame#NPSCCircle[circleState="success"]
{{
    border-color: {c['circle_success_border']};
}}
QFrame#NPSCCircle[circleState="error"]
{{
    border-color: {c['circle_error_border']};
}}

QLabel#CircleValue
{{
    font-size: 28px;
    font-weight: 800;
    color: {c['accent_brand']};
    background: transparent;
    border: none;
}}
QFrame#NPSCCircle[circleState="success"] QLabel#CircleValue
{{
    color: {c['state_success']};
}}
QFrame#NPSCCircle[circleState="error"] QLabel#CircleValue
{{
    color: {c['state_error']};
}}

QLabel#CircleLabel
{{
    font-size: 10px;
    color: {c['text_muted']};
    background: transparent;
    border: none;
}}

/* ─── Status Chip ─────────────────────────────────────────────── */
QFrame#NPSCChip
{{
    background: {c['chip_ok_bg']};
    border: none;
    border-radius: 4px;
    padding: 0px;
}}
QFrame#NPSCChip[chipState="ok"]
{{
    background: {c['chip_ok_bg']};
}}
QFrame#NPSCChip[chipState="warn"]
{{
    background: {c['chip_warn_bg']};
}}
QFrame#NPSCChip[chipState="error"]
{{
    background: {c['chip_error_bg']};
}}
QFrame#NPSCChip[chipState="info"]
{{
    background: {c['chip_info_bg']};
}}

QLabel#ChipDot
{{
    background: {c['chip_ok_fg']};
    border: none;
    border-radius: 3px;
}}
QFrame#NPSCChip[chipState="ok"] QLabel#ChipDot
{{
    background: {c['chip_ok_fg']};
}}
QFrame#NPSCChip[chipState="warn"] QLabel#ChipDot
{{
    background: {c['chip_warn_fg']};
}}
QFrame#NPSCChip[chipState="error"] QLabel#ChipDot
{{
    background: {c['chip_error_fg']};
}}
QFrame#NPSCChip[chipState="info"] QLabel#ChipDot
{{
    background: {c['chip_info_fg']};
}}

QLabel#ChipText
{{
    font-size: 10.5px;
    font-weight: 600;
    color: {c['chip_ok_fg']};
    background: transparent;
    border: none;
}}
QFrame#NPSCChip[chipState="ok"] QLabel#ChipText
{{
    color: {c['chip_ok_fg']};
}}
QFrame#NPSCChip[chipState="warn"] QLabel#ChipText
{{
    color: {c['chip_warn_fg']};
}}
QFrame#NPSCChip[chipState="error"] QLabel#ChipText
{{
    color: {c['chip_error_fg']};
}}
QFrame#NPSCChip[chipState="info"] QLabel#ChipText
{{
    color: {c['chip_info_fg']};
}}

/* ─── Result Card ─────────────────────────────────────────────── */
QFrame#NPSCResultCard
{{
    background: {c['bg_card']};
    border: 1px solid {c['border_subtle']};
    border-radius: 8px;
}}
QFrame#NPSCResultCard:hover
{{
    border-color: {c['accent_brand']};
}}

QLabel#ResultCardValue
{{
    font-size: 20px;
    font-weight: 800;
    color: {c['text_muted']};
    background: transparent;
    border: none;
}}
QLabel#ResultCardValue[semantic="success"]
{{
    color: {c['state_success']};
}}
QLabel#ResultCardValue[semantic="info"]
{{
    color: {c['accent_brand']};
}}
QLabel#ResultCardValue[semantic="warning"]
{{
    color: {c['state_warning']};
}}
QLabel#ResultCardValue[semantic="error"]
{{
    color: {c['state_error']};
}}

QLabel#ResultCardLabel
{{
    font-size: 10px;
    color: {c['text_muted']};
    background: transparent;
    border: none;
}}

/* ─── Tool Card ───────────────────────────────────────────────── */
QFrame#NPSCToolCard
{{
    background: {c['bg_card']};
    border: 1px solid {c['border_subtle']};
    border-radius: 8px;
}}
QFrame#NPSCToolCard:hover
{{
    border-color: {c['accent_brand']};
}}

QLabel#ToolCardIcon
{{
    background: {c['bg_elevated']};
    color: {c['accent_brand']};
    border-radius: 6px;
    font-size: 14px;
    border: none;
}}

QLabel#ToolCardTitle
{{
    font-size: 12px;
    font-weight: 600;
    color: {c['text_primary']};
    background: transparent;
    border: none;
}}

QLabel#ToolCardDesc
{{
    font-size: 10.5px;
    color: {c['text_muted']};
    background: transparent;
    border: none;
    line-height: 1.4;
}}

/* ─── Inputs ──────────────────────────────────────────────────── */
QComboBox, QLineEdit, QTextEdit, QPlainTextEdit, QListWidget
{{
    background: {c['bg_input']};
    color: {c['text_primary']};
    border: 1px solid {c['border_input']};
    border-radius: 5px;
    padding: 6px;
    selection-background-color: {c['accent_primary']};
    selection-color: {c['text_on_accent']};
}}
QComboBox:hover, QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QListWidget:hover
{{
    border-color: {c['accent_brand']};
}}
QComboBox:focus, QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QListWidget:focus
{{
    border-color: {c['border_focus']};
}}
QComboBox::drop-down
{{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow
{{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {c['text_secondary']};
    margin-right: 8px;
}}
QListWidget::item
{{
    border-radius: 4px;
    padding: 6px;
    margin: 2px;
}}
QListWidget::item:selected
{{
    background: {c['accent_primary']};
    color: {c['text_on_accent']};
}}

/* ─── Checkbox ────────────────────────────────────────────────── */
QCheckBox
{{
    color: {c['text_primary']};
    spacing: 8px;
}}
QCheckBox::indicator
{{
    width: 16px;
    height: 16px;
    border: 1px solid {c['border_input']};
    border-radius: 3px;
    background: {c['bg_input']};
}}
QCheckBox::indicator:hover
{{
    border-color: {c['accent_brand']};
}}
QCheckBox::indicator:checked
{{
    background: {c['accent_primary']};
    border-color: {c['accent_pressed']};
}}

/* ─── Tabs ────────────────────────────────────────────────────── */
QTabWidget::pane
{{
    border: 1px solid {c['border_subtle']};
    background: {c['bg_base']};
    border-radius: 6px;
}}
QTabBar::tab
{{
    background: {c['bg_surface']};
    color: {c['text_secondary']};
    border: 1px solid {c['border_subtle']};
    border-bottom: none;
    padding: 6px 12px;
    margin-right: 2px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    font-size: 11px;
}}
QTabBar::tab:hover
{{
    color: {c['text_primary']};
    border-color: {c['accent_brand']};
}}
QTabBar::tab:selected
{{
    background: {c['bg_elevated']};
    color: {c['text_primary']};
    border-color: {c['accent_primary']};
    font-weight: 600;
}}

/* ─── Progress ────────────────────────────────────────────────── */
QProgressBar
{{
    background: {c['bg_elevated']};
    border: none;
    border-radius: 2px;
    color: {c['text_primary']};
    text-align: center;
    font-weight: 700;
}}
QProgressBar::chunk
{{
    background: {c['accent_primary']};
    border-radius: 2px;
}}

/* ─── Quick Tab Bar ────────────────────────────────────────────── */
QLabel#PromptTab
{{
    font-size: 11px;
    font-weight: 500;
    color: {c['text_muted']};
    padding: 6px 12px;
    background: transparent;
    border: none;
}}
QLabel#PromptTab[active="true"]
{{
    color: {c['accent_brand']};
    border-bottom: 2px solid {c['accent_brand']};
    font-weight: 600;
}}

/* ─── Hero Status ─────────────────────────────────────────────── */
QLabel#HeroStatus
{{
    font-size: 10.5px;
    color: {c['text_muted']};
    background: transparent;
    border: none;
}}

/* ─── Metric Value (legacy compatibility) ─────────────────────── */
QLabel#MetricValue
{{
    font-size: 20px;
    font-weight: 800;
    color: {c['accent_brand']};
}}

/* ─── Splitter ────────────────────────────────────────────────── */
QSplitter::handle
{{
    background: {c['bg_elevated']};
    border: 1px solid {c['border_subtle']};
}}

/* ─── Scrollbar ───────────────────────────────────────────────── */
QScrollBar:vertical, QScrollBar:horizontal
{{
    background: {c['bg_base']};
    border: none;
    margin: 0px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal
{{
    background: {c['border_input']};
    border-radius: 4px;
    min-height: 28px;
    min-width: 28px;
}}
QScrollBar::handle:hover
{{
    background: {c['accent_brand']};
}}
QScrollBar::add-line, QScrollBar::sub-line,
QScrollBar::add-page, QScrollBar::sub-page
{{
    background: transparent;
    border: none;
}}

/* ─── Status States (legacy) ──────────────────────────────────── */
QLabel[statusState="procesando"], QLabel[statusState="warning"]
{{
    color: {c['state_warning']};
}}
QLabel[statusState="error"], QLabel[statusState="bloqueado"],
QLabel[statusState="blocked"], QLabel[statusState="fail"]
{{
    color: {c['state_error']};
}}
QLabel[statusState="cancelado"]
{{
    color: {c['text_muted']};
}}
QLabel[statusState="pass"], QLabel[statusState="normal"]
{{
    color: {c['state_success']};
}}

/* ─── Tooltip ─────────────────────────────────────────────────── */
QToolTip
{{
    background: {c['bg_elevated']};
    color: {c['text_primary']};
    border: 1px solid {c['accent_brand']};
    padding: 6px;
}}

/* ─── Help Icons ──────────────────────────────────────────────── */
QToolButton#HelpIconButton
{{
    background: {c['bg_surface']};
    color: {c['text_secondary']};
    border: 1px solid {c['border_subtle']};
    border-radius: 11px;
    padding: 0px;
    font-weight: 800;
}}
QToolButton#HelpIconButton:hover
{{
    background: {c['bg_elevated']};
    color: {c['text_primary']};
    border-color: {c['accent_brand']};
}}
QToolButton#HelpIconButton:focus
{{
    border: 2px solid {c['border_focus']};
    color: {c['text_primary']};
}}

/* ─── Context Help Popover ────────────────────────────────────── */
QFrame#ContextHelpPopover
{{
    background: {c['bg_elevated']};
    color: {c['text_primary']};
    border: 1px solid {c['accent_brand']};
    border-radius: 6px;
}}
QLabel#ContextHelpTitle
{{
    color: {c['text_primary']};
    font-weight: 800;
    font-size: 11pt;
}}
QLabel#ContextHelpBody
{{
    color: {c['text_secondary']};
    line-height: 1.25;
}}

/* ═══ Simple Mode Styles ═══════════════════════════════════════ */

QLabel#SimpleTitle
{{
    font-size: 18px;
    font-weight: 800;
    color: {c['text_primary']};
    background: transparent;
    border: none;
}}

QLabel#SimpleSubtitle
{{
    font-size: 12px;
    color: {c['text_secondary']};
    background: transparent;
    border: none;
}}

QLabel#SimplePromptLabel
{{
    font-size: 12px;
    font-weight: 600;
    color: {c['text_primary']};
    background: transparent;
    border: none;
}}

QLabel#SimpleProfileValue
{{
    font-size: 11px;
    font-weight: 600;
    color: {c['accent_brand']};
    background: transparent;
    border: none;
}}

QPushButton#SimpleAdvToggle
{{
    background: transparent;
    color: {c['text_secondary']};
    border: 1px solid {c['border_subtle']};
    border-radius: 5px;
    padding: 6px 12px;
    font-size: 11px;
    text-align: left;
    font-weight: 500;
}}
QPushButton#SimpleAdvToggle:hover
{{
    background: {c['bg_elevated']};
    color: {c['text_primary']};
}}
QPushButton#SimpleAdvToggle:checked
{{
    background: {c['bg_elevated']};
    border-color: {c['accent_brand']};
    color: {c['text_primary']};
}}

QFrame#SimpleAdvFrame
{{
    background: {c['bg_card']};
    border: 1px solid {c['border_subtle']};
    border-radius: 6px;
}}

QLabel#SimpleResultHeader
{{
    font-size: 14px;
    font-weight: 700;
    color: {c['state_success']};
    background: transparent;
    border: none;
}}
QLabel#SimpleResultHeader[errorState="true"]
{{
    color: {c['state_error']};
}}

QPushButton#ModeToggleBtn
{{
    background: {c['bg_button']};
    color: {c['text_button']};
    border: 1px solid {c['border_subtle']};
    border-radius: 5px;
    padding: 5px 12px;
    font-weight: 600;
    font-size: 10.5px;
}}
QPushButton#ModeToggleBtn:hover
{{
    background: {c['bg_button_hover']};
    border-color: {c['accent_brand']};
}}
QPushButton#ModeToggleBtn:focus
{{
    border: 2px solid {c['border_focus']};
}}

QPushButton#SimpleHistBtn
{{
    /* inherit default button style */
}}

/* ─── Health Dashboard ─────────────────────────────────────────── */
QFrame#NPSCMetricPill
{{
    background: {c['bg_card']};
    border: 1px solid {c['border_subtle']};
    border-radius: 8px;
}}
QFrame#NPSCMetricPill:hover
{{
    border-color: {c['accent_brand']};
}}
QLabel#MetricPillValue
{{
    font-size: 18px;
    font-weight: 800;
    color: {c['text_muted']};
    background: transparent;
    border: none;
}}
QLabel#MetricPillLabel
{{
    font-size: 10px;
    color: {c['text_muted']};
    background: transparent;
    border: none;
}}

/* ─── Health Section Title ────────────────────────────────────── */
QLabel#HealthSectionTitle
{{
    font-size: 10.5px;
    font-weight: 700;
    color: {c['text_muted']};
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}

/* ─── Metric Pill (in HealthDashboard) ─────────────────────────── */
QFrame#NPSCMetricPill
{{
    background: {c['bg_card']};
    border: 1px solid {c['border_subtle']};
    border-radius: 6px;
    padding: 4px;
}}
QFrame#NPSCMetricPill:hover
{{
    border-color: {c['accent_brand']};
}}
QLabel#MetricPillValue
{{
    background: transparent;
    border: none;
    padding: 0;
}}
QLabel#MetricPillLabel
{{
    background: transparent;
    border: none;
    padding: 0;
    color: {c['text_muted']};
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}}

/* ─── Scan Ring (premium animated ring) ────────────────────────── */
QFrame#NPSCCircle
{{
    background: transparent;
    border: none;
}}

/* ─── Premium Simple Mode ──────────────────────────────────────── */
QWidget#SimpleHeroCircle
{{
    background: transparent;
    border: none;
}}
QLabel#SimpleHeroScore
{{
    font-size: 28px;
    font-weight: 800;
    color: {c['accent_brand']};
    background: transparent;
    border: none;
}}
QLabel#SimpleHeroLabel
{{
    font-size: 10px;
    color: {c['text_muted']};
    background: transparent;
    border: none;
}}
QPushButton#PremiumScanBtn
{{
    background: {c['accent_primary']};
    color: {c['text_on_accent']};
    font-weight: 800;
    font-size: 13px;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    letter-spacing: 0.3px;
}}
QPushButton#PremiumScanBtn:hover
{{
    background: {c['accent_hover']};
}}
QPushButton#PremiumScanBtn:disabled
{{
    background: {c['bg_button']};
    color: {c['text_muted']};
}}
QLabel#PremiumStatusText
{{
    font-size: 10.5px;
    color: {c['text_secondary']};
}}
QFrame#PremiumResultCard
{{
    background: {c['bg_card']};
    border: 1px solid {c['border_subtle']};
    border-radius: 8px;
}}
QFrame#PremiumResultCard:hover
{{
    border-color: {c['accent_brand']};
}}
"""


# ─── Public API ──────────────────────────────────────────────────────────────
QSS_DARK = _build_qss(_DARK)
QSS_LIGHT = _build_qss(_LIGHT)
QSS = QSS_DARK


def get_qss(theme: str = "dark") -> str:
    """Return QSS for the given theme name."""
    if theme == "light":
        return QSS_LIGHT
    return QSS_DARK
