#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║              STOCK MARKET LIVE TRACKER  —  v3.0                        ║
║              Modern PyQt5 Dashboard  ·  Powered by Yahoo Finance        ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Quick Start                                                            ║
║  ─────────────────────────────────────────────────────────────────────  ║
║  1.  pip install PyQt5 yfinance matplotlib pandas plyer                 ║
║  2.  python stock_market_app.py                                         ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Features                                                               ║
║  • Select stocks by company name — no ticker symbols required           ║
║  • Live prices via yfinance, auto-refreshed every 30 seconds            ║
║  • Green / red colour coding with trend arrows                          ║
║  • Interactive 30-day price chart (matplotlib, dark theme)              ║
║  • Above / below price alerts with desktop notifications                ║
║  • Countdown timer showing seconds until next refresh                   ║
║  • Clean GitHub-dark inspired UI — Segoe UI font throughout             ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ── Standard library ──────────────────────────────────────────────────────────
import sys
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ── PyQt5 ─────────────────────────────────────────────────────────────────────
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QPushButton, QLabel,
    QGroupBox, QDialog, QDoubleSpinBox, QFormLayout,
    QMessageBox, QSplitter, QStatusBar,
    QListWidget, QListWidgetItem, QFrame, QSizePolicy,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QBrush, QPalette

# ── Optional third-party (graceful fallback if missing) ──────────────────────
try:
    import yfinance as yf
    YF_OK = True
except ImportError:
    yf = None
    YF_OK = False
    print("⚠  yfinance not found — run:  pip install yfinance")

try:
    import matplotlib
    matplotlib.use("Qt5Agg")
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MPL_OK = True
except ImportError:
    MPL_OK = False
    print("⚠  matplotlib not found — run:  pip install matplotlib pandas")

try:
    from plyer import notification as _plyer_notify
    PLYER_OK = True
except ImportError:
    PLYER_OK = False


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

# How often to auto-refresh price data (milliseconds)
REFRESH_MS = 30_000   # 30 seconds

# ── Stock catalogue: display name  →  ticker symbol ──────────────────────────
# Users pick from full names; the ticker is used only internally.
STOCK_CATALOG: Dict[str, str] = {
    "🍎  Apple":                 "AAPL",
    "🚗  Tesla":                 "TSLA",
    "🪟  Microsoft":             "MSFT",
    "📦  Amazon":                "AMZN",
    "🔍  Google (Alphabet)":     "GOOGL",
    "🟢  NVIDIA":                "NVDA",
    "👤  Meta Platforms":        "META",
    "🎬  Netflix":               "NFLX",
    "🔴  AMD":                   "AMD",
    "🔵  Intel":                 "INTC",
    "📡  Qualcomm":              "QCOM",
    "☁️   Salesforce":            "CRM",
    "🎨  Adobe":                 "ADBE",
    "💳  PayPal":                "PYPL",
    "🎵  Spotify":               "SPOT",
    "🚕  Uber":                  "UBER",
    "🏠  Airbnb":                "ABNB",
    "🛒  Shopify":               "SHOP",
    "📹  Zoom":                  "ZM",
    "🏦  JPMorgan Chase":        "JPM",
    "💰  Goldman Sachs":         "GS",
    "🏦  Bank of America":       "BAC",
    "🥤  Coca-Cola":             "KO",
    "🍔  McDonald's":            "MCD",
    "🏰  Disney":                "DIS",
    "✈️   Boeing":                "BA",
    "🛒  Walmart":               "WMT",
    "🎯  Target":                "TGT",
    "🏡  Home Depot":            "HD",
    "💳  Visa":                  "V",
    "💳  Mastercard":            "MA",
    "💊  Pfizer":                "PFE",
    "🏥  Johnson & Johnson":     "JNJ",
    "🛢️   ExxonMobil":            "XOM",
    "🌩️   Berkshire Hathaway":    "BRK-B",
    "📱  Qualcomm":              "QCOM",
    "🖥️   Dell Technologies":     "DELL",
    "🖨️   HP Inc":                "HPQ",
    "🔋  Rivian":                "RIVN",
    "🚀  SpaceX (Palantir)":     "PLTR",
}

# Reverse lookup: ticker → display name
SYM_TO_NAME: Dict[str, str] = {v: k for k, v in STOCK_CATALOG.items()}

# Stocks shown when the app first starts
DEFAULT_WATCHLIST: List[str] = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN"]


# ══════════════════════════════════════════════════════════════════════════════
#  STYLESHEET  —  GitHub-dark inspired, modern professional look
# ══════════════════════════════════════════════════════════════════════════════

APP_STYLE = """
/* ── Base ─────────────────────────────────────────────────────────────────── */
QMainWindow, QDialog { background-color: #0d1117; }
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}

/* ── Cards / Group Boxes ──────────────────────────────────────────────────── */
QGroupBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 10px 10px 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    top: -2px;
    padding: 2px 6px;
    background-color: #0d1117;
    color: #58a6ff;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    border-radius: 3px;
}

/* ── Push Buttons ─────────────────────────────────────────────────────────── */
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
    font-size: 12px;
    min-height: 30px;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #58a6ff;
    color: #58a6ff;
}
QPushButton:pressed  { background-color: #1f3a5f; }

QPushButton#addBtn       { background:#238636; border-color:#2ea043; color:#fff; }
QPushButton#addBtn:hover { background:#2ea043; }

QPushButton#removeBtn       { background:#6e1c1c; border-color:#da3633; color:#fff; }
QPushButton#removeBtn:hover { background:#da3633; }

QPushButton#alertBtn       { background:#6e4f00; border-color:#d29922; color:#fff; }
QPushButton#alertBtn:hover { background:#d29922; color:#fff; }

QPushButton#refreshBtn       { background:#1a3c6b; border-color:#388bfd; color:#fff; }
QPushButton#refreshBtn:hover { background:#388bfd; }

/* ── Table ────────────────────────────────────────────────────────────────── */
QTableWidget {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    gridline-color: #21262d;
    selection-background-color: #1f3a5f;
    selection-color: #e6edf3;
    alternate-background-color: #1a1f27;
    font-size: 13px;
    outline: none;
}
QTableWidget::item {
    padding: 10px 14px;
    border-bottom: 1px solid #21262d;
}
QTableWidget::item:selected { background-color: #1f3a5f; }

QHeaderView::section {
    background-color: #0d1117;
    color: #8b949e;
    padding: 10px 14px;
    border: none;
    border-bottom: 2px solid #30363d;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 1px;
}

/* ── Combo Box ────────────────────────────────────────────────────────────── */
QComboBox {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    min-height: 32px;
    min-width: 230px;
}
QComboBox:hover { border-color: #58a6ff; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox QAbstractItemView {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    selection-background-color: #1f3a5f;
    padding: 4px;
    outline: none;
}

/* ── Line Edit / Spin Box ─────────────────────────────────────────────────── */
QLineEdit, QDoubleSpinBox, QSpinBox {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    min-height: 32px;
}
QLineEdit:focus, QDoubleSpinBox:focus { border-color: #58a6ff; }
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: #30363d;
    border: none;
    border-radius: 3px;
    width: 18px;
}

/* ── Scroll Bars ──────────────────────────────────────────────────────────── */
QScrollBar:vertical   { background:#161b22; width:6px;  border-radius:3px; }
QScrollBar:horizontal { background:#161b22; height:6px; border-radius:3px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #30363d; border-radius: 3px;
    min-height: 30px; min-width: 30px;
}
QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover { background: #58a6ff; }
QScrollBar::add-line, QScrollBar::sub-line { width:0; height:0; }

/* ── Status Bar ───────────────────────────────────────────────────────────── */
QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 1px solid #30363d;
    font-size: 11px;
    padding: 4px 10px;
}
QStatusBar QLabel { background: transparent; }

/* ── List Widget ──────────────────────────────────────────────────────────── */
QListWidget {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #c9d1d9;
    outline: none;
}
QListWidget::item { padding: 7px 12px; }
QListWidget::item:selected { background: #1f3a5f; color: #58a6ff; }
QListWidget::item:hover    { background: #21262d; }

/* ── Splitter ─────────────────────────────────────────────────────────────── */
QSplitter::handle          { background-color: #30363d; }
QSplitter::handle:horizontal { width:  1px; }
QSplitter::handle:vertical   { height: 1px; }

/* ── Tooltips ─────────────────────────────────────────────────────────────── */
QToolTip {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  DATA MODEL
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class StockData:
    """Snapshot of one stock's price at a point in time."""
    symbol:     str
    name:       str
    price:      float = 0.0
    change:     float = 0.0
    pct_change: float = 0.0
    volume:     int   = 0
    error:      bool  = False

    # ── Formatted string helpers ──────────────────────────────────────────────
    @property
    def price_str(self) -> str:
        return f"${self.price:,.2f}" if not self.error else "N/A"

    @property
    def change_str(self) -> str:
        if self.error:
            return "N/A"
        sign = "+" if self.change >= 0 else ""
        return f"{sign}${self.change:,.2f}"

    @property
    def pct_str(self) -> str:
        if self.error:
            return "N/A"
        sign = "+" if self.pct_change >= 0 else ""
        return f"{sign}{self.pct_change:.2f}%"

    @property
    def is_up(self) -> bool:
        return self.change >= 0


# ══════════════════════════════════════════════════════════════════════════════
#  BACKGROUND WORKER — fetches price data WITHOUT blocking the UI
# ══════════════════════════════════════════════════════════════════════════════

class StockFetcher(QThread):
    """
    QThread subclass that downloads price data for a list of symbols
    and emits the results back to the main thread via a Qt signal.

    Why use a thread?  yfinance makes HTTP requests; doing this on the
    main (GUI) thread would freeze the window for several seconds.
    """

    # Signal emitted when all stocks have been fetched
    data_ready  = pyqtSignal(list)   # list[StockData]
    # Signal emitted if a hard error occurs (e.g. no network)
    fetch_error = pyqtSignal(str)

    def __init__(self, symbols: List[str], parent=None):
        super().__init__(parent)
        self.symbols = symbols

    def run(self):
        """Entry point for the background thread."""
        if not YF_OK:
            self.fetch_error.emit("yfinance is not installed")
            return

        results: List[StockData] = []
        for sym in self.symbols:
            try:
                ticker = yf.Ticker(sym)
                fi = ticker.fast_info

                price  = float(fi.last_price      or 0.0)
                prev   = float(fi.previous_close  or price)
                change = price - prev
                pct    = (change / prev * 100) if prev else 0.0

                # Volume: try today's volume, fall back to 3-month average
                try:
                    vol = int(fi.last_volume or fi.three_month_average_volume or 0)
                except (AttributeError, TypeError):
                    vol = 0

                results.append(StockData(
                    symbol=sym,
                    name=SYM_TO_NAME.get(sym, sym),
                    price=price, change=change, pct_change=pct, volume=vol,
                ))
            except Exception as exc:
                results.append(StockData(
                    symbol=sym,
                    name=SYM_TO_NAME.get(sym, sym),
                    error=True,
                ))

        self.data_ready.emit(results)


# ══════════════════════════════════════════════════════════════════════════════
#  CHART DATA WORKER — fetches historical data for the chart in a thread
# ══════════════════════════════════════════════════════════════════════════════

class ChartFetcher(QThread):
    """Downloads 30-day price history for rendering the embedded chart."""

    # symbol, display-name, date-array, price-array, line-colour
    chart_ready = pyqtSignal(str, str, object, object, str)

    def __init__(self, symbol: str, name: str, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.name   = name

    def run(self):
        if not YF_OK:
            self.chart_ready.emit(self.symbol, self.name, [], [], "#58a6ff")
            return
        try:
            hist = yf.Ticker(self.symbol).history(period="1mo")
            if hist.empty:
                self.chart_ready.emit(self.symbol, self.name, [], [], "#58a6ff")
                return
            dates  = hist.index.to_pydatetime()
            prices = hist["Close"].values
            color  = "#3fb950" if prices[-1] >= prices[0] else "#f85149"
            self.chart_ready.emit(self.symbol, self.name, dates, prices, color)
        except Exception:
            self.chart_ready.emit(self.symbol, self.name, [], [], "#58a6ff")


# ══════════════════════════════════════════════════════════════════════════════
#  CHART WIDGET — embedded matplotlib canvas with dark theme
# ══════════════════════════════════════════════════════════════════════════════

class ChartWidget(QWidget):
    """
    Renders a 30-day closing-price chart for whichever stock the
    user clicks.  Uses matplotlib embedded inside a Qt widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_symbol: Optional[str] = None
        self._chart_fetcher: Optional[ChartFetcher] = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if not MPL_OK:
            # matplotlib not installed — show a friendly message
            msg = QLabel(
                "📊  Chart requires matplotlib & pandas\n"
                "     pip install matplotlib pandas"
            )
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("color:#8b949e; font-size:13px;")
            layout.addWidget(msg)
            self.canvas = None
            return

        # Create the dark-themed figure
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor("#161b22")
        self.ax  = self.fig.add_subplot(111)
        self._style_ax()

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background-color:#161b22; border-radius:10px;")
        layout.addWidget(self.canvas)

        self._placeholder()

    def _style_ax(self):
        """Apply dark styling to the matplotlib axes."""
        ax = self.ax
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#30363d")
        ax.grid(color="#21262d", linestyle="--", linewidth=0.5, alpha=0.7)

    def _placeholder(self):
        """Show placeholder text before any stock is selected."""
        if not self.canvas:
            return
        self.ax.clear()
        self._style_ax()
        self.ax.text(
            0.5, 0.5,
            "📈  Click a row in the table to view the price chart",
            transform=self.ax.transAxes,
            ha="center", va="center",
            color="#8b949e", fontsize=12,
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.fig.tight_layout(pad=1.5)
        self.canvas.draw()

    def load_chart(self, symbol: str, name: str):
        """Start loading the chart for *symbol* (non-blocking)."""
        if not self.canvas:
            return
        if symbol == self.current_symbol:
            return   # already showing this stock

        self.current_symbol = symbol

        # Show a loading message immediately so the UI feels responsive
        self.ax.clear()
        self._style_ax()
        self.ax.text(
            0.5, 0.5, f"Loading chart for {name}…",
            transform=self.ax.transAxes,
            ha="center", va="center",
            color="#58a6ff", fontsize=12,
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

        # Fetch historical data in a background thread
        self._chart_fetcher = ChartFetcher(symbol, name)
        self._chart_fetcher.chart_ready.connect(self._render)
        self._chart_fetcher.start()

    def _render(self, symbol: str, name: str, dates, prices, color: str):
        """Slot: called by ChartFetcher once data is available."""
        self.ax.clear()
        self._style_ax()

        if len(prices) == 0:
            self.ax.text(
                0.5, 0.5, "No historical data available",
                transform=self.ax.transAxes,
                ha="center", va="center", color="#da3633", fontsize=12,
            )
            self.canvas.draw()
            return

        # Shaded area + line
        self.ax.fill_between(dates, prices, alpha=0.15, color=color)
        self.ax.plot(dates, prices, color=color, linewidth=2.0, solid_capstyle="round")

        # X-axis: weekly date labels
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        self.ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        self.fig.autofmt_xdate(rotation=30, ha="right")

        # Labels
        self.ax.set_title(
            f"{name}  —  30-day closing price",
            color="#e6edf3", fontsize=11, fontweight="bold", pad=8,
        )
        self.ax.set_ylabel("USD", color="#8b949e", fontsize=9)
        self.fig.tight_layout(pad=1.5)
        self.canvas.draw()

    def reset(self):
        """Clear the chart back to the placeholder state."""
        self.current_symbol = None
        self._placeholder()


# ══════════════════════════════════════════════════════════════════════════════
#  ALERT DIALOG — lets the user set a target price for a stock
# ══════════════════════════════════════════════════════════════════════════════

class AlertDialog(QDialog):
    """
    Modal dialog where the user sets an 'above' and/or 'below' threshold
    price.  Setting a value to 0 disables that alert.
    """

    def __init__(self, symbol: str, name: str, current_price: float, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.name   = name
        self.setWindowTitle(f"Set Alert — {name}")
        self.setMinimumWidth(370)
        self.setModal(True)
        self._build(current_price)

    def _build(self, current_price: float):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        hdr = QLabel(f"🔔  Price Alert  ·  {self.name}")
        hdr.setStyleSheet("font-size:15px; font-weight:700; color:#e6edf3;")
        layout.addWidget(hdr)

        cur = QLabel(f"Current price:  ${current_price:,.2f}")
        cur.setStyleSheet("color:#8b949e; font-size:12px;")
        layout.addWidget(cur)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.above_spin = QDoubleSpinBox()
        self.above_spin.setRange(0, 1_000_000)
        self.above_spin.setDecimals(2)
        self.above_spin.setPrefix("$ ")
        self.above_spin.setValue(round(current_price * 1.05, 2))   # +5 %
        form.addRow("🟢  Alert above:", self.above_spin)

        self.below_spin = QDoubleSpinBox()
        self.below_spin.setRange(0, 1_000_000)
        self.below_spin.setDecimals(2)
        self.below_spin.setPrefix("$ ")
        self.below_spin.setValue(round(current_price * 0.95, 2))   # −5 %
        form.addRow("🔴  Alert below:", self.below_spin)

        layout.addLayout(form)

        hint = QLabel("Set value to  0  to disable an alert direction.")
        hint.setStyleSheet("color:#8b949e; font-size:11px; font-style:italic;")
        layout.addWidget(hint)

        # Buttons
        row = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)

        save = QPushButton("💾  Save Alert")
        save.setObjectName("addBtn")
        save.clicked.connect(self.accept)

        row.addWidget(cancel)
        row.addStretch()
        row.addWidget(save)
        layout.addLayout(row)

    def values(self) -> Tuple[float, float]:
        """Return (above_price, below_price) — 0.0 means disabled."""
        return self.above_spin.value(), self.below_spin.value()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """
    The root application window.

    Layout (three-column, two-row):

        ┌─────────────────────────────────────────────────────────────┐
        │  Header: title · subtitle · timestamp · Refresh button      │
        ├────────────────┬────────────────────────────────────────────┤
        │  Left panel    │  Right panel                               │
        │  • Add stock   │  ┌──────────────────────────────────────┐ │
        │  • Watchlist   │  │  Live price table (top half)         │ │
        │  • Alerts      │  ├──────────────────────────────────────┤ │
        │                │  │  30-day price chart (bottom half)    │ │
        │                │  └──────────────────────────────────────┘ │
        └────────────────┴────────────────────────────────────────────┘
        │  Status bar: status message  ·  countdown to next refresh   │
        └─────────────────────────────────────────────────────────────┘
    """

    def __init__(self):
        super().__init__()

        # ── App state ─────────────────────────────────────────────────────────
        self.watchlist: List[str] = list(DEFAULT_WATCHLIST)

        # Alerts: { symbol: { "above": float, "below": float } }
        self.alerts: Dict[str, Dict[str, float]] = {}

        # Latest price snapshot: { symbol: StockData }
        self.stock_data: Dict[str, StockData] = {}

        # Tracks which alert keys have already fired (prevents re-spamming)
        # key format:  "AAPL_above"  or  "AAPL_below"
        self._fired: set = set()

        # Reference to the active background fetcher (kept alive)
        self._fetcher: Optional[StockFetcher] = None

        # ── Window setup ──────────────────────────────────────────────────────
        self.setWindowTitle("📈  Stock Market Live Tracker")
        self.setMinimumSize(1100, 680)
        self.resize(1360, 800)

        # ── Build UI ──────────────────────────────────────────────────────────
        self._build_ui()

        # ── Apply stylesheet globally ─────────────────────────────────────────
        QApplication.instance().setStyleSheet(APP_STYLE)

        # ── Auto-refresh timer (fires every REFRESH_MS milliseconds) ──────────
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh_data)
        self._refresh_timer.start(REFRESH_MS)

        # ── Countdown timer (updates status bar every second) ─────────────────
        self._remaining = REFRESH_MS // 1000
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._tick)
        self._countdown_timer.start(1000)

        # ── Kick off the first data load after a short delay ──────────────────
        QTimer.singleShot(400, self.refresh_data)

    # ══════════════════════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 6)
        root.setSpacing(10)

        root.addWidget(self._mk_header())

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._mk_left_panel())
        splitter.addWidget(self._mk_right_panel())
        splitter.setSizes([290, 1000])
        splitter.setHandleWidth(1)
        root.addWidget(splitter, stretch=1)

        self._mk_status_bar()

    # ── Header ────────────────────────────────────────────────────────────────
    def _mk_header(self) -> QFrame:
        """Gradient banner: title, subtitle, timestamp, refresh button."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #161b22, stop:1 #0d1117
                );
                border: 1px solid #30363d;
                border-radius: 10px;
            }
        """)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(18, 12, 18, 12)

        # Left: title + subtitle
        titles = QVBoxLayout()
        titles.setSpacing(3)

        t = QLabel("📈  Stock Market Live Tracker")
        t.setStyleSheet(
            "font-size:22px; font-weight:800; color:#e6edf3;"
            "background:transparent; border:none;"
        )

        s = QLabel("Real-time prices  ·  Powered by Yahoo Finance  ·  Auto-refreshes every 30 s")
        s.setStyleSheet(
            "font-size:11px; color:#8b949e; background:transparent; border:none;"
        )

        titles.addWidget(t)
        titles.addWidget(s)
        lay.addLayout(titles)
        lay.addStretch()

        # Right: timestamp + refresh button
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight)
        right.setSpacing(6)

        self._ts_lbl = QLabel("Last updated:  —")
        self._ts_lbl.setStyleSheet(
            "font-size:11px; color:#58a6ff; background:transparent; border:none;"
        )
        self._ts_lbl.setAlignment(Qt.AlignRight)

        rbtn = QPushButton("⟳  Refresh Now")
        rbtn.setObjectName("refreshBtn")
        rbtn.setFixedWidth(145)
        rbtn.clicked.connect(self.refresh_data)

        right.addWidget(self._ts_lbl)
        right.addWidget(rbtn)
        lay.addLayout(right)
        return frame

    # ── Left panel ────────────────────────────────────────────────────────────
    def _mk_left_panel(self) -> QWidget:
        """
        Three cards stacked vertically:
          1. Stock search (editable combo → full company names)
          2. Watchlist management
          3. Active alerts viewer
        """
        panel = QWidget()
        panel.setMaximumWidth(310)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 6, 0)
        lay.setSpacing(10)

        # ── 1. Add stock ───────────────────────────────────────────────────────
        add_group = QGroupBox("Add to Watchlist")
        ag = QVBoxLayout(add_group)
        ag.setSpacing(8)

        lbl = QLabel("Search by company name:")
        lbl.setStyleSheet("color:#8b949e; font-size:11px;")
        ag.addWidget(lbl)

        # Editable combo box — user can type to filter
        self._combo = QComboBox()
        self._combo.setEditable(True)
        self._combo.lineEdit().setPlaceholderText("Type to search…")
        for name in sorted(STOCK_CATALOG.keys()):
            self._combo.addItem(name)
        ag.addWidget(self._combo)

        add_btn = QPushButton("＋  Add to Watchlist")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self._add_stock)
        ag.addWidget(add_btn)

        lay.addWidget(add_group)

        # ── 2. Watchlist ───────────────────────────────────────────────────────
        wl_group = QGroupBox("My Watchlist")
        wg = QVBoxLayout(wl_group)
        wg.setSpacing(6)

        self._wl_list = QListWidget()
        self._wl_list.setMinimumHeight(150)
        self._wl_list.itemClicked.connect(self._on_wl_click)
        wg.addWidget(self._wl_list)

        btn_row = QHBoxLayout()
        rm_btn = QPushButton("✕  Remove")
        rm_btn.setObjectName("removeBtn")
        rm_btn.clicked.connect(self._remove_stock)

        al_btn = QPushButton("🔔  Set Alert")
        al_btn.setObjectName("alertBtn")
        al_btn.clicked.connect(self._open_alert)

        btn_row.addWidget(rm_btn)
        btn_row.addWidget(al_btn)
        wg.addLayout(btn_row)

        lay.addWidget(wl_group)
        self._refresh_wl_widget()   # populate with DEFAULT_WATCHLIST

        # ── 3. Active alerts ───────────────────────────────────────────────────
        al_group = QGroupBox("Active Alerts")
        alg = QVBoxLayout(al_group)

        self._alerts_list = QListWidget()
        self._alerts_list.setMinimumHeight(100)
        alg.addWidget(self._alerts_list)

        clr_btn = QPushButton("🗑  Clear Selected Alert")
        clr_btn.clicked.connect(self._clear_alert)
        alg.addWidget(clr_btn)

        lay.addWidget(al_group)
        lay.addStretch()
        return panel

    # ── Right panel ───────────────────────────────────────────────────────────
    def _mk_right_panel(self) -> QWidget:
        """Price table (top) + price chart (bottom) in a vertical splitter."""
        panel = QWidget()
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        vsplit = QSplitter(Qt.Vertical)
        vsplit.addWidget(self._mk_table_section())
        vsplit.addWidget(self._mk_chart_section())
        vsplit.setSizes([380, 300])
        vsplit.setHandleWidth(1)

        lay.addWidget(vsplit)
        return panel

    def _mk_table_section(self) -> QWidget:
        """The live price table."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 8)
        lay.setSpacing(4)

        hdr = QLabel("LIVE PRICES")
        hdr.setStyleSheet(
            "font-size:10px; font-weight:700; color:#8b949e; letter-spacing:1.5px;"
        )
        lay.addWidget(hdr)

        cols = ["  ", "Company", "Symbol", "Price", "Change", "Change %", "Volume"]
        self._table = QTableWidget(0, len(cols))
        self._table.setHorizontalHeaderLabels(cols)

        # Columns: arrow col fixed; rest stretch
        h = self._table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Stretch)
        h.setSectionResizeMode(0, QHeaderView.Fixed)   # arrow col
        h.setSectionResizeMode(2, QHeaderView.Fixed)   # symbol col
        self._table.setColumnWidth(0, 38)
        self._table.setColumnWidth(2, 72)

        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.cellClicked.connect(self._on_row_click)

        lay.addWidget(self._table)
        return w

    def _mk_chart_section(self) -> QWidget:
        """The embedded matplotlib chart."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(4)

        hdr = QLabel("PRICE CHART  —  30-day closing prices")
        hdr.setStyleSheet(
            "font-size:10px; font-weight:700; color:#8b949e; letter-spacing:1.5px;"
        )
        lay.addWidget(hdr)

        self._chart = ChartWidget()
        lay.addWidget(self._chart, stretch=1)
        return w

    def _mk_status_bar(self):
        """Two-part status bar: status message on the left, countdown on the right."""
        sb = QStatusBar()
        self.setStatusBar(sb)

        self._status_lbl    = QLabel("  Ready")
        self._countdown_lbl = QLabel("")

        sb.addWidget(self._status_lbl)
        sb.addPermanentWidget(self._countdown_lbl)

    # ══════════════════════════════════════════════════════════════════════════
    #  DATA REFRESH
    # ══════════════════════════════════════════════════════════════════════════

    def refresh_data(self):
        """
        Launch a background StockFetcher thread for all symbols
        currently in the watchlist.
        """
        if not self.watchlist:
            self._status_lbl.setText("  Watchlist is empty — add a stock to begin.")
            return

        self._status_lbl.setText("  ⟳  Fetching latest prices…")
        self._remaining = REFRESH_MS // 1000

        # Stop the timer so it won't double-fire during the network call;
        # we restart it from the thread's 'finished' signal.
        self._refresh_timer.stop()

        self._fetcher = StockFetcher(self.watchlist)
        self._fetcher.data_ready.connect(self._on_data)
        self._fetcher.fetch_error.connect(lambda msg: self._status_lbl.setText(f"  ✗  {msg}"))
        self._fetcher.finished.connect(
            lambda: self._refresh_timer.start(REFRESH_MS)
        )
        self._fetcher.start()

    def _on_data(self, data: List[StockData]):
        """Slot: process freshly fetched StockData objects."""
        for sd in data:
            self.stock_data[sd.symbol] = sd

        self._update_table(data)
        self._check_alerts()

        ts = datetime.now().strftime("%H:%M:%S  ·  %d %b %Y")
        self._ts_lbl.setText(f"Last updated:  {ts}")
        ok = sum(1 for sd in data if not sd.error)
        self._status_lbl.setText(
            f"  ✓  {ok}/{len(data)} stocks updated successfully"
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  TABLE
    # ══════════════════════════════════════════════════════════════════════════

    def _update_table(self, data: List[StockData]):
        """Redraw every row in the live-price table."""
        self._table.setRowCount(len(data))

        # Colour palette
        GREEN = QColor("#3fb950")   # price rose
        RED   = QColor("#f85149")   # price fell
        GREY  = QColor("#8b949e")   # error / neutral
        WHITE = QColor("#e6edf3")   # primary text
        DIM   = QColor("#8b949e")   # secondary text

        for row, sd in enumerate(data):
            if sd.error:
                trend_col  = GREY
                arrow_char = "—"
            elif sd.is_up:
                trend_col  = GREEN
                arrow_char = "▲"
            else:
                trend_col  = RED
                arrow_char = "▼"

            def cell(text, color=None, font_size=12, bold=False, align=Qt.AlignVCenter | Qt.AlignLeft):
                """Helper: create a styled, non-editable table cell."""
                item = QTableWidgetItem(text)
                if color:
                    item.setForeground(QBrush(color))
                f = QFont("Segoe UI", font_size, QFont.Bold if bold else QFont.Normal)
                item.setFont(f)
                item.setTextAlignment(align)
                return item

            RIGHT = Qt.AlignRight | Qt.AlignVCenter

            self._table.setItem(row, 0, cell(arrow_char, trend_col,  12, True,  Qt.AlignCenter))
            self._table.setItem(row, 1, cell(sd.name,    WHITE,       12, True))
            self._table.setItem(row, 2, cell(sd.symbol,  DIM,         11, False))
            self._table.setItem(row, 3, cell(sd.price_str,  WHITE,   13, True,  RIGHT))
            self._table.setItem(row, 4, cell(sd.change_str, trend_col,12, False, RIGHT))
            self._table.setItem(row, 5, cell(sd.pct_str,    trend_col,12, True,  RIGHT))

            vol_text = f"{sd.volume:,}" if sd.volume else "—"
            self._table.setItem(row, 6, cell(vol_text, DIM, 11, False, RIGHT))

            self._table.setRowHeight(row, 48)

    # ══════════════════════════════════════════════════════════════════════════
    #  WATCHLIST MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════════

    def _add_stock(self):
        """Add the combo-box selection to the watchlist."""
        display = self._combo.currentText().strip()
        symbol  = STOCK_CATALOG.get(display)

        # Partial match (user may have typed only part of the name)
        if not symbol:
            for name, sym in STOCK_CATALOG.items():
                if display.lower() in name.lower():
                    symbol = sym
                    break

        if not symbol:
            QMessageBox.warning(self, "Not Found",
                f"'{display}' was not found in the catalogue.\n"
                "Try selecting from the dropdown list.")
            return

        if symbol in self.watchlist:
            self._status_lbl.setText(f"  {symbol} is already in your watchlist.")
            return

        self.watchlist.append(symbol)
        self._refresh_wl_widget()
        self.refresh_data()

    def _remove_stock(self):
        """Remove the currently selected watchlist item."""
        item = self._wl_list.currentItem()
        if not item:
            return
        symbol = item.data(Qt.UserRole)
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
        self.alerts.pop(symbol, None)
        self._fired.discard(f"{symbol}_above")
        self._fired.discard(f"{symbol}_below")
        self._refresh_wl_widget()
        self._refresh_alerts_widget()

        # Update table to reflect removal
        remaining = [self.stock_data[s] for s in self.watchlist if s in self.stock_data]
        self._update_table(remaining)

        # Reset chart if this was the displayed stock
        if self._chart.current_symbol == symbol:
            self._chart.reset()

    def _refresh_wl_widget(self):
        """Repopulate the watchlist QListWidget."""
        self._wl_list.clear()
        for sym in self.watchlist:
            name = SYM_TO_NAME.get(sym, sym)
            it   = QListWidgetItem(f"  {name}")
            it.setData(Qt.UserRole, sym)
            self._wl_list.addItem(it)

    def _on_wl_click(self, item: QListWidgetItem):
        """Clicking a watchlist item selects the matching table row."""
        sym = item.data(Qt.UserRole)
        for row in range(self._table.rowCount()):
            cell = self._table.item(row, 2)   # symbol column
            if cell and cell.text() == sym:
                self._table.selectRow(row)
                sd = self.stock_data.get(sym)
                if sd:
                    self._chart.load_chart(sym, sd.name)
                break

    # ══════════════════════════════════════════════════════════════════════════
    #  ROW CLICK → CHART
    # ══════════════════════════════════════════════════════════════════════════

    def _on_row_click(self, row: int, _col: int):
        """Clicking any cell in a row loads that stock's chart."""
        sym_item = self._table.item(row, 2)
        if not sym_item:
            return
        sym  = sym_item.text()
        sd   = self.stock_data.get(sym)
        name = sd.name if sd else sym
        self._chart.load_chart(sym, name)

    # ══════════════════════════════════════════════════════════════════════════
    #  ALERT MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════════

    def _open_alert(self):
        """Open the alert-setting dialog for the selected watchlist stock."""
        item = self._wl_list.currentItem()
        if not item:
            QMessageBox.information(self, "Select a Stock",
                "Please select a stock from your watchlist first.")
            return

        sym   = item.data(Qt.UserRole)
        sd    = self.stock_data.get(sym)
        price = sd.price if sd else 0.0
        name  = SYM_TO_NAME.get(sym, sym)

        dlg = AlertDialog(sym, name, price, parent=self)
        dlg.setStyleSheet(APP_STYLE)

        if dlg.exec_() == QDialog.Accepted:
            above, below = dlg.values()
            self.alerts[sym] = {"above": above, "below": below}
            # Reset fired state so the new thresholds can trigger fresh
            self._fired.discard(f"{sym}_above")
            self._fired.discard(f"{sym}_below")
            self._refresh_alerts_widget()
            self._status_lbl.setText(f"  🔔  Alert saved for {name}")

    def _refresh_alerts_widget(self):
        """Redraw the active-alerts QListWidget."""
        self._alerts_list.clear()
        for sym, bounds in self.alerts.items():
            name  = SYM_TO_NAME.get(sym, sym)
            above = bounds.get("above", 0)
            below = bounds.get("below", 0)
            if above:
                it = QListWidgetItem(f"🟢  {name}  ▲  above  ${above:,.2f}")
                it.setData(Qt.UserRole, (sym, "above"))
                self._alerts_list.addItem(it)
            if below:
                it = QListWidgetItem(f"🔴  {name}  ▼  below  ${below:,.2f}")
                it.setData(Qt.UserRole, (sym, "below"))
                self._alerts_list.addItem(it)

    def _clear_alert(self):
        """Remove the selected alert entry."""
        item = self._alerts_list.currentItem()
        if not item:
            return
        sym, direction = item.data(Qt.UserRole)
        if sym in self.alerts:
            self.alerts[sym][direction] = 0.0
            if not any(v for v in self.alerts[sym].values()):
                del self.alerts[sym]
        self._fired.discard(f"{sym}_{direction}")
        self._refresh_alerts_widget()

    # ══════════════════════════════════════════════════════════════════════════
    #  ALERT CHECKING & NOTIFICATIONS
    # ══════════════════════════════════════════════════════════════════════════

    def _check_alerts(self):
        """Compare each stock's current price against its thresholds."""
        for sym, bounds in list(self.alerts.items()):
            sd = self.stock_data.get(sym)
            if not sd or sd.error:
                continue

            name  = SYM_TO_NAME.get(sym, sym)
            price = sd.price
            above = bounds.get("above", 0)
            below = bounds.get("below", 0)

            # ── above threshold ────────────────────────────────────────────────
            key_a = f"{sym}_above"
            if above and price >= above and key_a not in self._fired:
                self._fired.add(key_a)
                self._notify(
                    title=f"🟢  Price Alert: {name}",
                    body=(
                        f"{name} ({sym}) is now above your target!\n"
                        f"Current: ${price:,.2f}   |   Target: ▲ ${above:,.2f}"
                    ),
                )

            # ── below threshold ────────────────────────────────────────────────
            key_b = f"{sym}_below"
            if below and price <= below and key_b not in self._fired:
                self._fired.add(key_b)
                self._notify(
                    title=f"🔴  Price Alert: {name}",
                    body=(
                        f"{name} ({sym}) has dropped below your target!\n"
                        f"Current: ${price:,.2f}   |   Target: ▼ ${below:,.2f}"
                    ),
                )

            # Reset fired flag once price moves back to a neutral zone
            # (so the alert can fire again if the price crosses again)
            if above and price < above * 0.995:
                self._fired.discard(key_a)
            if below and price > below * 1.005:
                self._fired.discard(key_b)

    def _notify(self, title: str, body: str):
        """
        Show a desktop notification via plyer.
        Falls back to a Qt popup if plyer is unavailable or fails.
        """
        if PLYER_OK:
            try:
                _plyer_notify.notify(
                    title=title,
                    message=body,
                    app_name="Stock Tracker",
                    timeout=8,
                )
                return
            except Exception:
                pass   # fall through

        # Qt fallback
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(body)
        dlg.setIcon(QMessageBox.Information)
        dlg.setStyleSheet(APP_STYLE)
        dlg.exec_()

    # ══════════════════════════════════════════════════════════════════════════
    #  COUNTDOWN TICKER
    # ══════════════════════════════════════════════════════════════════════════

    def _tick(self):
        """Called every second to decrement and display the refresh countdown."""
        if self._remaining > 0:
            self._remaining -= 1
        self._countdown_lbl.setText(f"Next refresh in  {self._remaining} s  ")

    # ══════════════════════════════════════════════════════════════════════════
    #  WINDOW CLOSE
    # ══════════════════════════════════════════════════════════════════════════

    def closeEvent(self, event):
        """Clean up timers and threads on exit."""
        self._refresh_timer.stop()
        self._countdown_timer.stop()
        if self._fetcher and self._fetcher.isRunning():
            self._fetcher.quit()
            self._fetcher.wait(2000)
        event.accept()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Start the Qt application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Stock Market Live Tracker")
    app.setApplicationVersion("3.0")
    app.setStyle("Fusion")          # baseline cross-platform style

    # Global font
    app.setFont(QFont("Segoe UI", 11))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
