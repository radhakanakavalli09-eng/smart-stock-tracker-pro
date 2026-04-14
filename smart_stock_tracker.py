#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║      SMART STOCK TRACKER  —  Advanced Edition  v2.0                     ║
║      Portfolio Manager  ·  Intelligent Signals  ·  Market Scanner       ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ⚠  DISCLAIMER                                                          ║
║  All signals in this app are based on technical indicators only         ║
║  (Moving Averages, RSI, momentum). They are TREND ESTIMATIONS and       ║
║  are NOT financial predictions or investment advice. Past technical      ║
║  patterns do not guarantee future price movements.                      ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Install:  pip install PyQt5 yfinance matplotlib pandas plyer           ║
║  Run:      python smart_stock_tracker.py                                 ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ══════════════════════════════════════════════════════════════════════════════
#  §1  IMPORTS
# ══════════════════════════════════════════════════════════════════════════════
import sys
import json
import os
import math
from datetime import datetime, time as dtime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QPushButton, QLabel, QComboBox, QDoubleSpinBox,
    QSpinBox, QCheckBox, QGroupBox, QDialog, QFormLayout, QLineEdit,
    QListWidget, QListWidgetItem, QFrame, QScrollArea, QSlider,
    QStatusBar, QProgressBar, QMessageBox, QSizePolicy, QGridLayout,
    QStackedWidget,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QBrush, QPalette, QPixmap

# ── Optional packages (graceful fallback if missing) ─────────────────────────
try:
    import yfinance as yf
    import pandas as pd
    YF_OK = True
except ImportError:
    YF_OK = False
    print("⚠  yfinance/pandas not found — run:  pip install yfinance pandas")

try:
    import matplotlib
    matplotlib.use("Qt5Agg")
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    import matplotlib.gridspec as gridspec
    MPL_OK = True
except ImportError:
    MPL_OK = False

try:
    from plyer import notification as _plyer
    PLYER_OK = True
except ImportError:
    PLYER_OK = False


# ══════════════════════════════════════════════════════════════════════════════
#  §2  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

REFRESH_MS       = 30_000          # price refresh interval (ms)
PORTFOLIO_FILE   = "portfolio.json"

# Full-name → symbol mapping (shown to user as full names only)
STOCK_CATALOG: Dict[str, str] = {
    "🍎  Apple":               "AAPL",
    "🚗  Tesla":               "TSLA",
    "🪟  Microsoft":           "MSFT",
    "📦  Amazon":              "AMZN",
    "🔍  Google (Alphabet)":   "GOOGL",
    "🟢  NVIDIA":              "NVDA",
    "👤  Meta Platforms":      "META",
    "🎬  Netflix":             "NFLX",
    "🔴  AMD":                 "AMD",
    "🔵  Intel":               "INTC",
    "📡  Qualcomm":            "QCOM",
    "☁️   Salesforce":          "CRM",
    "🎨  Adobe":               "ADBE",
    "💳  PayPal":              "PYPL",
    "🎵  Spotify":             "SPOT",
    "🚕  Uber":                "UBER",
    "🏠  Airbnb":              "ABNB",
    "🛒  Shopify":             "SHOP",
    "📹  Zoom":                "ZM",
    "🏦  JPMorgan Chase":      "JPM",
    "💰  Goldman Sachs":       "GS",
    "🏦  Bank of America":     "BAC",
    "🥤  Coca-Cola":           "KO",
    "🍔  McDonald's":          "MCD",
    "🏰  Disney":              "DIS",
    "✈️   Boeing":              "BA",
    "🛒  Walmart":             "WMT",
    "🎯  Target":              "TGT",
    "🏡  Home Depot":          "HD",
    "💳  Visa":                "V",
    "💳  Mastercard":          "MA",
    "💊  Pfizer":              "PFE",
    "🏥  J&J":                 "JNJ",
    "🛢️   ExxonMobil":          "XOM",
    "🌩️   Berkshire Hathaway":  "BRK-B",
    "🌍  Palantir":            "PLTR",
    "🚀  CrowdStrike":         "CRWD",
    "💻  Snowflake":           "SNOW",
    "🔋  Rivian":              "RIVN",
    "🖥️   Dell":               "DELL",
}
SYM_TO_NAME = {v: k for k, v in STOCK_CATALOG.items()}

# Predefined universe used by the Market Scanner tab
SCAN_UNIVERSE = [
    "AAPL","MSFT","GOOGL","AMZN","TSLA","NVDA","META","NFLX",
    "AMD","INTC","QCOM","CRM","ADBE","PYPL","SPOT","UBER",
    "ABNB","SHOP","ZM","JPM","GS","BAC","KO","MCD",
    "DIS","BA","WMT","V","MA","PFE","XOM","PLTR","CRWD",
]


# ══════════════════════════════════════════════════════════════════════════════
#  §3  STYLESHEET  —  Deep-dark professional theme
# ══════════════════════════════════════════════════════════════════════════════

APP_STYLE = """
QMainWindow, QDialog { background-color: #0a0e17; }
QWidget {
    background-color: #0a0e17;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}

/* Cards */
QGroupBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 10px 10px 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px; top: -2px;
    padding: 2px 8px;
    background-color: #0a0e17;
    color: #58a6ff;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    border-radius: 3px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 8px;
    background-color: #0a0e17;
    margin-top: -1px;
}
QTabBar::tab {
    background-color: #161b22;
    color: #8b949e;
    border: 1px solid #30363d;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 8px 18px;
    margin-right: 2px;
    font-weight: 600;
    font-size: 12px;
}
QTabBar::tab:selected {
    background-color: #1f6feb;
    color: #ffffff;
    border-color: #388bfd;
}
QTabBar::tab:hover:!selected { background-color: #21262d; color: #c9d1d9; }

/* Buttons */
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
QPushButton:hover  { background-color: #30363d; border-color: #58a6ff; color: #58a6ff; }
QPushButton:pressed { background-color: #1f3a5f; }
QPushButton#addBtn      { background:#238636; border-color:#2ea043; color:#fff; }
QPushButton#addBtn:hover{ background:#2ea043; }
QPushButton#removeBtn      { background:#6e1c1c; border-color:#da3633; color:#fff; }
QPushButton#removeBtn:hover{ background:#da3633; }
QPushButton#scanBtn      { background:#1a3c6b; border-color:#388bfd; color:#fff; }
QPushButton#scanBtn:hover{ background:#388bfd; }
QPushButton#alertBtn      { background:#4a2d00; border-color:#d29922; color:#fff; }
QPushButton#alertBtn:hover{ background:#d29922; }

/* Table */
QTableWidget {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    gridline-color: #21262d;
    selection-background-color: #1f3a5f;
    selection-color: #e6edf3;
    alternate-background-color: #1a1f27;
    outline: none;
}
QTableWidget::item { padding: 9px 12px; border-bottom: 1px solid #21262d; }
QTableWidget::item:selected { background-color: #1f3a5f; }
QHeaderView::section {
    background-color: #0d1117;
    color: #8b949e;
    padding: 9px 12px;
    border: none;
    border-bottom: 2px solid #30363d;
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.8px;
}

/* Combo / Line edit */
QComboBox, QLineEdit, QDoubleSpinBox, QSpinBox {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    min-height: 32px;
}
QComboBox:hover, QLineEdit:focus, QDoubleSpinBox:focus { border-color: #58a6ff; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox QAbstractItemView {
    background-color: #21262d; color: #c9d1d9;
    border: 1px solid #30363d; border-radius: 6px;
    selection-background-color: #1f3a5f; padding: 4px; outline: none;
}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QSpinBox::up-button, QSpinBox::down-button {
    background: #30363d; border: none; border-radius: 3px; width: 18px;
}

/* Scrollbars */
QScrollBar:vertical   { background:#161b22; width:6px;  border-radius:3px; }
QScrollBar:horizontal { background:#161b22; height:6px; border-radius:3px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background:#30363d; border-radius:3px; min-height:30px; min-width:30px;
}
QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover { background:#58a6ff; }
QScrollBar::add-line, QScrollBar::sub-line { width:0; height:0; }

/* List */
QListWidget {
    background-color:#161b22; border:1px solid #30363d; border-radius:6px; outline:none;
}
QListWidget::item { padding:8px 12px; }
QListWidget::item:selected { background:#1f3a5f; color:#58a6ff; }
QListWidget::item:hover    { background:#21262d; }

/* Checkbox */
QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #30363d; border-radius: 4px;
    background: #21262d;
}
QCheckBox::indicator:checked { background: #238636; border-color: #2ea043; }

/* Status bar */
QStatusBar {
    background-color:#161b22; color:#8b949e; border-top:1px solid #30363d;
    font-size:11px; padding:4px 10px;
}
QStatusBar QLabel { background:transparent; }

/* Splitter */
QSplitter::handle { background-color:#21262d; }
QSplitter::handle:horizontal { width:1px; }
QSplitter::handle:vertical   { height:1px; }

/* Progress bar */
QProgressBar {
    background-color:#21262d; border:1px solid #30363d; border-radius:4px;
    text-align:center; color:#c9d1d9;
}
QProgressBar::chunk { background-color:#1f6feb; border-radius:4px; }

/* Tooltips */
QToolTip {
    background-color:#21262d; color:#c9d1d9; border:1px solid #30363d;
    border-radius:4px; padding:4px 8px; font-size:12px;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  §4  DATA MODELS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Position:
    """One portfolio holding."""
    symbol:        str
    name:          str
    buy_price:     float
    quantity:      float
    watchlist:     bool  = False
    alert_enabled: bool  = True

@dataclass
class AlertConfig:
    """Per-stock alert settings."""
    above_price:           float = 0.0   # 0 = disabled
    below_price:           float = 0.0
    movement_threshold:    float = 2.0   # % in 1 day → trigger movement alert
    trend_alerts:          bool  = True  # MA/RSI signals
    movement_alerts:       bool  = True

@dataclass
class StockAnalysis:
    """
    Complete snapshot for one ticker.
    ⚠ All signal fields are TECHNICAL ESTIMATIONS, not predictions.
    """
    symbol:        str
    name:          str
    current_price: float        = 0.0
    prev_close:    float        = 0.0
    change_1d:     float        = 0.0
    pct_1d:        float        = 0.0
    rsi:           Optional[float] = None
    rsi_zone:      str          = "NEUTRAL"   # OVERSOLD / NEUTRAL / OVERBOUGHT
    sma_code:      str          = "NEUTRAL"   # BULL_CROSS / BULL / BEAR / BEAR_CROSS
    sma_label:     str          = "—"
    signal_code:   str          = "NEUTRAL"
    signal_label:  str          = "→ Neutral"
    signal_color:  str          = "#8b949e"
    movement_alert: bool        = False
    hist:          Any          = None         # pd.DataFrame, passed through signal
    error:         bool         = False


# ══════════════════════════════════════════════════════════════════════════════
#  §5  TECHNICAL ANALYSIS ENGINE
#
#  ⚠ All functions below compute TECHNICAL INDICATORS derived from
#    historical price data. They are used for TREND ESTIMATION only.
#    They do NOT predict future prices and are NOT investment advice.
# ══════════════════════════════════════════════════════════════════════════════

class TechAnalyzer:
    """
    Static helpers that compute RSI, SMA signals, and an overall
    trend estimate from a price series.

    IMPORTANT: These are lagging indicators — they describe what HAS
    happened, not what WILL happen. Use them as one input among many,
    never as a sole trading signal.
    """

    @staticmethod
    def rsi(close: "pd.Series", period: int = 14) -> Optional[float]:
        """
        Relative Strength Index (0 – 100).
        Zones:  RSI < 30 → historically seen as oversold territory.
                RSI > 70 → historically seen as overbought territory.
        ⚠ These zones describe past tendencies, not future direction.
        """
        if len(close) < period + 2:
            return None
        delta  = close.diff()
        gain   = delta.clip(lower=0)
        loss   = (-delta).clip(lower=0)
        avg_g  = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_l  = loss.ewm(com=period - 1, min_periods=period).mean()
        rs     = avg_g / avg_l.replace(0, float("inf"))
        series = 100 - (100 / (1 + rs))
        val    = float(series.iloc[-1])
        return round(val, 1) if not math.isnan(val) else None

    @staticmethod
    def rsi_zone(rsi: Optional[float]) -> str:
        """Classify RSI value into a named zone."""
        if rsi is None:         return "NEUTRAL"
        if rsi < 30:            return "OVERSOLD"
        if rsi > 70:            return "OVERBOUGHT"
        return "NEUTRAL"

    @staticmethod
    def rsi_series(close: "pd.Series", period: int = 14) -> "pd.Series":
        """Return the full RSI series (for chart rendering)."""
        if len(close) < period + 2:
            return pd.Series(dtype=float)
        delta = close.diff()
        gain  = delta.clip(lower=0)
        loss  = (-delta).clip(lower=0)
        avg_g = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_l = loss.ewm(com=period - 1, min_periods=period).mean()
        rs    = avg_g / avg_l.replace(0, float("inf"))
        return 100 - (100 / (1 + rs))

    @staticmethod
    def sma_signal(close: "pd.Series") -> dict:
        """
        SMA(20) vs SMA(50) crossover.
        Golden Cross = SMA20 crosses ABOVE SMA50 → bullish context.
        Death Cross  = SMA20 crosses BELOW SMA50 → bearish context.
        ⚠ Crossovers are lagging and do not guarantee price direction.
        """
        if len(close) < 52:
            return {"code": "NEUTRAL", "label": "Insufficient data", "sma20": None, "sma50": None}
        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()
        c20, c50 = float(sma20.iloc[-1]), float(sma50.iloc[-1])
        p20, p50 = float(sma20.iloc[-2]), float(sma50.iloc[-2])

        if p20 < p50 and c20 > c50:
            return {"code": "BULL_CROSS", "label": "Golden Cross ↑",  "sma20": c20, "sma50": c50}
        if p20 > p50 and c20 < c50:
            return {"code": "BEAR_CROSS", "label": "Death Cross ↓",   "sma20": c20, "sma50": c50}
        if c20 > c50:
            return {"code": "BULL",       "label": "Above SMA50 ↑",   "sma20": c20, "sma50": c50}
        return     {"code": "BEAR",       "label": "Below SMA50 ↓",   "sma20": c20, "sma50": c50}

    @staticmethod
    def overall_signal(rsi: Optional[float], sma_code: str, pct_1d: float) -> Tuple[str, str, str]:
        """
        Combine RSI + SMA + 1-day momentum into a single trend estimate.
        Returns (code, label, hex_colour).

        ⚠ DISCLAIMER: This score is a TECHNICAL TREND ESTIMATE ONLY.
          It is NOT a buy/sell recommendation or price prediction.
        """
        score = 0

        # RSI contribution
        if rsi is not None:
            if   rsi < 25:  score += 2
            elif rsi < 35:  score += 1
            elif rsi > 75:  score -= 2
            elif rsi > 65:  score -= 1

        # SMA contribution
        score += {"BULL_CROSS": 2, "BULL": 1, "BEAR": -1, "BEAR_CROSS": -2}.get(sma_code, 0)

        # Counter-trend momentum: big daily moves often mean-revert
        if pct_1d < -4:  score += 1
        elif pct_1d > 4: score -= 1

        if   score >= 3:  return "STRONG_BUY",  "⬆ STRONG BUY SIGNAL",  "#3fb950"
        elif score == 2:  return "BUY",          "↗ BUY SIGNAL",         "#56d364"
        elif score == 1:  return "MILD_BUY",     "↗ MILD BUY SIGNAL",    "#7ee787"
        elif score == -1: return "MILD_SELL",    "↘ MILD SELL SIGNAL",   "#ff7b72"
        elif score == -2: return "SELL",         "↘ SELL SIGNAL",        "#f85149"
        elif score <= -3: return "STRONG_SELL",  "⬇ STRONG SELL SIGNAL","#da3633"
        return                   "NEUTRAL",      "→ Neutral",             "#8b949e"

    @classmethod
    def analyze(cls, hist: "pd.DataFrame",
                current_price: float,
                pct_1d: float,
                movement_threshold: float = 2.0,
                symbol: str = "",
                name: str = "") -> StockAnalysis:
        """Run full analysis on a price history DataFrame."""
        close       = hist["Close"].dropna()
        rsi_val     = cls.rsi(close)
        sma         = cls.sma_signal(close)
        sig_code, sig_label, sig_color = cls.overall_signal(rsi_val, sma["code"], pct_1d)
        movement    = abs(pct_1d) >= movement_threshold

        return StockAnalysis(
            symbol        = symbol,
            name          = name or SYM_TO_NAME.get(symbol, symbol),
            current_price = current_price,
            prev_close    = current_price - (current_price * pct_1d / 100) if pct_1d else current_price,
            change_1d     = current_price * pct_1d / 100,
            pct_1d        = pct_1d,
            rsi           = rsi_val,
            rsi_zone      = cls.rsi_zone(rsi_val),
            sma_code      = sma["code"],
            sma_label     = sma["label"],
            signal_code   = sig_code,
            signal_label  = sig_label,
            signal_color  = sig_color,
            movement_alert= movement,
            hist          = hist,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  §6  DATA PERSISTENCE — JSON save / load
# ══════════════════════════════════════════════════════════════════════════════

class DataStore:
    """Reads and writes the portfolio JSON file."""

    _DEFAULT = {
        "portfolio":     [],
        "watchlist":     [],
        "alert_configs": {},
        "settings": {
            "refresh_interval":           30,
            "default_movement_threshold": 2.0,
            "trend_alerts_global":        True,
            "movement_alerts_global":     True,
            "scan_alerts_global":         False,
            "advance_warning_hours":      0,
        },
    }

    @classmethod
    def load(cls) -> dict:
        try:
            with open(PORTFOLIO_FILE, encoding="utf-8") as f:
                data = json.load(f)
            # Merge missing keys from default
            for k, v in cls._DEFAULT.items():
                data.setdefault(k, v)
            if isinstance(data.get("settings"), dict):
                for k, v in cls._DEFAULT["settings"].items():
                    data["settings"].setdefault(k, v)
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return dict(cls._DEFAULT)

    @classmethod
    def save(cls, data: dict) -> None:
        try:
            with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ DataStore.save error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  §7  BACKGROUND WORKERS
# ══════════════════════════════════════════════════════════════════════════════

class PriceWorker(QThread):
    """
    Fetches live prices + full 3-month history for every symbol
    in the watchlist/portfolio.  Runs off the main thread.
    """
    result_ready = pyqtSignal(list)      # list[StockAnalysis]
    progress     = pyqtSignal(int, int)  # fetched, total
    fetch_error  = pyqtSignal(str)

    def __init__(self, symbols: List[str],
                 alert_configs: Dict[str, dict],
                 settings: dict,
                 parent=None):
        super().__init__(parent)
        self.symbols       = symbols
        self.alert_configs = alert_configs
        self.settings      = settings

    def run(self):
        if not YF_OK:
            self.fetch_error.emit("yfinance not installed")
            return

        results: List[StockAnalysis] = []
        total = len(self.symbols)

        for idx, sym in enumerate(self.symbols):
            try:
                results.append(self._fetch(sym))
            except Exception as exc:
                results.append(StockAnalysis(
                    symbol=sym,
                    name=SYM_TO_NAME.get(sym, sym),
                    error=True
                ))
            self.progress.emit(idx + 1, total)

        self.result_ready.emit(results)

    def _fetch(self, sym: str) -> StockAnalysis:
        # ── DEBUG: confirms the worker thread is actually running ──────────────
        print(f"[FETCH] Requesting data for {sym} ...")
        ticker = yf.Ticker(sym)

        # 3-month daily history gives enough data for RSI(14) + SMA(20/50)
        hist = ticker.history(period="3mo", interval="1d")

        if hist.empty:
            print(f"[FETCH] {sym}: history is empty — check the symbol or your network.")
            return StockAnalysis(symbol=sym, name=SYM_TO_NAME.get(sym, sym), error=True)

        def _safe(val, fallback: float) -> float:
            """Return float(val) but treat None/NaN/0 as missing → use fallback."""
            try:
                v = float(val)
                return v if (not math.isnan(v) and v > 0) else fallback
            except (TypeError, ValueError):
                return fallback

        last_close = float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else last_close

        # fast_info gives a real-time price; fall back to last daily close if it fails
        try:
            fi    = ticker.fast_info
            price = _safe(fi.last_price,     last_close)
            prev  = _safe(fi.previous_close, prev_close)
        except Exception as exc:
            print(f"[FETCH] {sym}: fast_info failed ({exc}), using daily close.")
            price = last_close
            prev  = prev_close

        pct_1d = (price - prev) / prev * 100 if prev else 0.0
        # ── DEBUG: price data confirmed ────────────────────────────────────────
        print(f"[FETCH] {sym}: price=${price:.2f}  prev=${prev:.2f}  Δ={pct_1d:+.2f}%")

        cfg    = self.alert_configs.get(sym, {})
        thresh = cfg.get("movement_threshold",
                         self.settings.get("default_movement_threshold", 2.0))

        result = TechAnalyzer.analyze(hist, price, pct_1d, thresh, sym,
                                      SYM_TO_NAME.get(sym, sym))
        print(f"[FETCH] {sym}: RSI={result.rsi}  MA={result.sma_code}  → {result.signal_label}")
        return result


class ScannerWorker(QThread):
    """
    Scans the SCAN_UNIVERSE to find top gainers, losers, and notable
    technical signals.  Used by the Market Scanner tab.
    """
    scan_done  = pyqtSignal(list)    # list[StockAnalysis]
    progress   = pyqtSignal(int, int)
    scan_error = pyqtSignal(str)

    def __init__(self, symbols: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        self.symbols = symbols or SCAN_UNIVERSE

    def run(self):
        if not YF_OK:
            self.scan_error.emit("yfinance not installed")
            return
        results = []
        total   = len(self.symbols)
        for idx, sym in enumerate(self.symbols):
            try:
                ticker = yf.Ticker(sym)
                hist   = ticker.history(period="3mo", interval="1d")
                if hist.empty:
                    continue
                try:
                    fi    = ticker.fast_info
                    price = float(fi.last_price     or hist["Close"].iloc[-1])
                    prev  = float(fi.previous_close or hist["Close"].iloc[-2])
                except Exception:
                    price = float(hist["Close"].iloc[-1])
                    prev  = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price

                pct_1d = (price - prev) / prev * 100 if prev else 0.0
                results.append(TechAnalyzer.analyze(hist, price, pct_1d, 2.0, sym,
                                                    SYM_TO_NAME.get(sym, sym)))
            except Exception:
                pass
            self.progress.emit(idx + 1, total)

        # Sort by absolute 1-day % change (biggest movers first)
        results.sort(key=lambda a: abs(a.pct_1d), reverse=True)
        self.scan_done.emit(results)


# ══════════════════════════════════════════════════════════════════════════════
#  §8  REUSABLE WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

# ── 8a. Stat Card ──────────────────────────────────────────────────────────────
class StatCard(QFrame):
    """Small metric card shown in the header banner."""

    def __init__(self, icon: str, title: str, value: str = "—"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 10px;
            }
        """)
        self.setMinimumWidth(160)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(4)

        header = QLabel(f"{icon}  {title}")
        header.setStyleSheet("font-size:10px; font-weight:700; color:#8b949e; letter-spacing:1px;")
        lay.addWidget(header)

        self._val = QLabel(value)
        self._val.setStyleSheet("font-size:18px; font-weight:800; color:#e6edf3;")
        lay.addWidget(self._val)

    def update(self, value: str, color: str = "#e6edf3"):
        self._val.setText(value)
        self._val.setStyleSheet(f"font-size:18px; font-weight:800; color:{color};")


# ── 8b. Signal Panel ───────────────────────────────────────────────────────────
class SignalPanel(QWidget):
    """
    Displays RSI zone, SMA signal, and the combined trend estimate
    for one stock.  Also shows the legal disclaimer.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(8)

        self._title = QLabel("Select a stock to see signals")
        self._title.setStyleSheet("font-size:13px; font-weight:700; color:#e6edf3;")
        lay.addWidget(self._title)

        # RSI row
        rsi_row = QHBoxLayout()
        rsi_row.setSpacing(6)
        self._rsi_lbl = QLabel("RSI (14):")
        self._rsi_lbl.setStyleSheet("color:#8b949e; font-size:12px;")
        self._rsi_val = QLabel("—")
        self._rsi_val.setStyleSheet("font-size:12px; font-weight:700; color:#c9d1d9;")
        self._rsi_zone = QLabel("")
        self._rsi_zone.setStyleSheet("font-size:11px; padding:2px 6px; border-radius:4px;")
        rsi_row.addWidget(self._rsi_lbl)
        rsi_row.addWidget(self._rsi_val)
        rsi_row.addWidget(self._rsi_zone)
        rsi_row.addStretch()
        lay.addLayout(rsi_row)

        # RSI bar (visual indicator)
        self._rsi_bar = _RsiBar()
        lay.addWidget(self._rsi_bar)

        # MA signal
        ma_row = QHBoxLayout()
        self._ma_lbl = QLabel("MA Signal:")
        self._ma_lbl.setStyleSheet("color:#8b949e; font-size:12px;")
        self._ma_val = QLabel("—")
        self._ma_val.setStyleSheet("font-size:12px; font-weight:700; color:#c9d1d9;")
        ma_row.addWidget(self._ma_lbl)
        ma_row.addWidget(self._ma_val)
        ma_row.addStretch()
        lay.addLayout(ma_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #30363d;")
        lay.addWidget(sep)

        # Overall signal
        self._overall = QLabel("→ Neutral")
        self._overall.setAlignment(Qt.AlignCenter)
        self._overall.setStyleSheet(
            "font-size:15px; font-weight:800; color:#8b949e;"
            "background-color:#21262d; border-radius:8px; padding:8px;"
        )
        lay.addWidget(self._overall)

        # Disclaimer
        disc = QLabel(
            "⚠ These are trend ESTIMATIONS based on MA & RSI indicators.\n"
            "NOT financial predictions or investment advice."
        )
        disc.setWordWrap(True)
        disc.setStyleSheet(
            "font-size:10px; color:#6e7681; font-style:italic;"
            "background:#0d1117; border-radius:6px; padding:6px;"
        )
        lay.addWidget(disc)

    def refresh(self, sa: StockAnalysis):
        """Update all labels with the given StockAnalysis."""
        self._title.setText(f"{sa.name}  ({sa.symbol})")
        if sa.rsi is not None:
            self._rsi_val.setText(str(sa.rsi))
            self._rsi_bar.set_rsi(sa.rsi)
        else:
            self._rsi_val.setText("—")
            self._rsi_bar.set_rsi(None)

        zone_styles = {
            "OVERSOLD":   ("OVERSOLD",   "#3fb950", "#0d2d0f"),
            "OVERBOUGHT": ("OVERBOUGHT", "#f85149", "#2d0f0f"),
            "NEUTRAL":    ("NEUTRAL",    "#8b949e", "#21262d"),
        }
        zlabel, zcolor, zbg = zone_styles.get(sa.rsi_zone, ("", "#8b949e", "#21262d"))
        self._rsi_zone.setText(zlabel)
        self._rsi_zone.setStyleSheet(
            f"font-size:10px; font-weight:700; color:{zcolor};"
            f"background:{zbg}; padding:2px 8px; border-radius:4px;"
        )

        ma_color = {"BULL_CROSS": "#3fb950", "BULL": "#7ee787",
                    "BEAR_CROSS": "#f85149", "BEAR": "#ff7b72"}.get(sa.sma_code, "#8b949e")
        self._ma_val.setText(sa.sma_label)
        self._ma_val.setStyleSheet(f"font-size:12px; font-weight:700; color:{ma_color};")

        self._overall.setText(sa.signal_label)
        self._overall.setStyleSheet(
            f"font-size:15px; font-weight:800; color:{sa.signal_color};"
            "background-color:#21262d; border-radius:8px; padding:8px;"
        )

    def clear(self):
        self._title.setText("Select a stock to see signals")
        self._rsi_val.setText("—")
        self._rsi_bar.set_rsi(None)
        self._rsi_zone.setText("")
        self._ma_val.setText("—")
        self._overall.setText("→ Neutral")


class _RsiBar(QWidget):
    """
    A thin coloured bar showing where the RSI value falls on the 0-100 scale.
    Green zone: 0-30 (oversold), red zone: 70-100 (overbought), grey: 30-70.
    """

    def __init__(self):
        super().__init__()
        self.setFixedHeight(20)
        self._rsi: Optional[float] = None

    def set_rsi(self, value: Optional[float]):
        self._rsi = value
        self.update()

    def paintEvent(self, e):
        from PyQt5.QtGui import QPainter, QBrush, QColor
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        r = 5

        # Background track
        p.setBrush(QBrush(QColor("#21262d")))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 4, w, h - 8, r, r)

        if self._rsi is None:
            return

        # Colour zones
        seg_w = w / 100
        for x in range(w):
            frac = x / w * 100
            if frac < 30:
                c = QColor("#3fb950")
            elif frac > 70:
                c = QColor("#f85149")
            else:
                c = QColor("#30363d")
            p.setBrush(QBrush(c))
            p.drawRect(x, 5, 1, h - 10)

        # Marker
        mx = int(self._rsi / 100 * w)
        p.setBrush(QBrush(QColor("#e6edf3")))
        p.drawEllipse(mx - 5, 2, 10, h - 4)


# ── 8c. Chart Widget ───────────────────────────────────────────────────────────
class ChartWidget(QWidget):
    """
    Two-panel matplotlib chart:
      Panel 1 — Price + SMA(20) + SMA(50) with bullish/bearish fill
      Panel 2 — RSI(14) with overbought / oversold bands highlighted
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_symbol: Optional[str] = None
        self._chart_thread: Optional[QThread] = None
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        if not MPL_OK:
            lbl = QLabel("Install matplotlib for charts\n pip install matplotlib")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#8b949e;")
            lay.addWidget(lbl)
            self.canvas = None
            return

        self.fig = Figure(figsize=(6, 4), dpi=90)
        self.fig.patch.set_facecolor("#161b22")

        gs = gridspec.GridSpec(2, 1, height_ratios=[2.5, 1], hspace=0.05)
        self.ax_price = self.fig.add_subplot(gs[0])
        self.ax_rsi   = self.fig.add_subplot(gs[1], sharex=self.ax_price)
        self._style_axes()

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background-color:#161b22;")
        lay.addWidget(self.canvas)
        self._placeholder()

    def _style_axes(self):
        for ax in (self.ax_price, self.ax_rsi):
            ax.set_facecolor("#0d1117")
            ax.tick_params(colors="#8b949e", labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#30363d")
            ax.grid(color="#21262d", linestyle="--", linewidth=0.4, alpha=0.8)

    def _placeholder(self):
        if not self.canvas:
            return
        for ax in (self.ax_price, self.ax_rsi):
            ax.clear()
        self._style_axes()
        self.ax_price.text(
            0.5, 0.5, "📈  Select a stock to view the chart",
            transform=self.ax_price.transAxes,
            ha="center", va="center", color="#8b949e", fontsize=12,
        )
        self.ax_price.set_xticks([])
        self.ax_price.set_yticks([])
        self.ax_rsi.set_xticks([])
        self.ax_rsi.set_yticks([])
        self.fig.tight_layout(pad=1.0)
        self.canvas.draw()

    def load(self, sa: StockAnalysis):
        """Render the chart from a StockAnalysis object (hist already fetched)."""
        if not self.canvas or sa.hist is None or sa.error:
            self._placeholder()
            return
        self.current_symbol = sa.symbol
        self._render(sa)

    def _render(self, sa: StockAnalysis):
        hist  = sa.hist
        close = hist["Close"].dropna()
        dates = close.index.to_pydatetime()

        if len(close) < 5:
            self._placeholder()
            return

        for ax in (self.ax_price, self.ax_rsi):
            ax.clear()
        self._style_axes()

        # ── Price panel ───────────────────────────────────────────────────────
        self.ax_price.plot(dates, close.values, color="#c9d1d9", linewidth=1.5, zorder=4, label="Price")

        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()
        if not sma20.dropna().empty:
            self.ax_price.plot(dates, sma20.values, color="#58a6ff",
                               linewidth=1.2, alpha=0.85, label="SMA 20", zorder=3)
        if not sma50.dropna().empty:
            self.ax_price.plot(dates, sma50.values, color="#f0883e",
                               linewidth=1.2, alpha=0.85, label="SMA 50", zorder=3)

        # Green / red fill between SMA lines
        if not sma20.dropna().empty and not sma50.dropna().empty:
            self.ax_price.fill_between(dates, sma20, sma50,
                where=(sma20 >= sma50), alpha=0.1, color="#3fb950", interpolate=True)
            self.ax_price.fill_between(dates, sma20, sma50,
                where=(sma20 <  sma50), alpha=0.1, color="#f85149", interpolate=True)

        # Mark Golden Cross / Death Cross
        if sa.sma_code in ("BULL_CROSS", "BEAR_CROSS"):
            vline_color = "#3fb950" if sa.sma_code == "BULL_CROSS" else "#f85149"
            self.ax_price.axvline(dates[-1], color=vline_color,
                                  linestyle="--", linewidth=1.0, alpha=0.7)
            label = "Golden Cross" if sa.sma_code == "BULL_CROSS" else "Death Cross"
            self.ax_price.annotate(
                label, xy=(dates[-1], float(close.iloc[-1])),
                xytext=(-60, 20), textcoords="offset points",
                color=vline_color, fontsize=8,
                arrowprops=dict(arrowstyle="->", color=vline_color),
            )

        self.ax_price.set_title(
            f"{sa.name} ({sa.symbol})  —  3-month price",
            color="#e6edf3", fontsize=10, fontweight="bold", pad=6,
        )
        legend = self.ax_price.legend(
            fontsize=8, framealpha=0.2, facecolor="#21262d",
            edgecolor="#30363d", labelcolor="#c9d1d9"
        )

        # ── RSI panel ─────────────────────────────────────────────────────────
        rsi_series = TechAnalyzer.rsi_series(close)
        if not rsi_series.dropna().empty:
            rsi_dates = rsi_series.index.to_pydatetime()
            self.ax_rsi.plot(rsi_dates, rsi_series.values, color="#bc8cff", linewidth=1.2)
            self.ax_rsi.axhline(70, color="#f85149", linestyle="--", linewidth=0.8, alpha=0.6)
            self.ax_rsi.axhline(30, color="#3fb950", linestyle="--", linewidth=0.8, alpha=0.6)
            self.ax_rsi.fill_between(rsi_dates, rsi_series, 70,
                where=(rsi_series >= 70), alpha=0.2, color="#f85149", interpolate=True)
            self.ax_rsi.fill_between(rsi_dates, rsi_series, 30,
                where=(rsi_series <= 30), alpha=0.2, color="#3fb950", interpolate=True)
            self.ax_rsi.set_ylim(0, 100)
            self.ax_rsi.set_ylabel("RSI", color="#8b949e", fontsize=8)
            self.ax_rsi.yaxis.set_ticks([30, 50, 70])

        # X-axis formatting (shared)
        self.ax_rsi.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        self.ax_rsi.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        self.fig.autofmt_xdate(rotation=30, ha="right")
        plt_label = self.ax_price.xaxis.get_ticklabels()
        for lbl in plt_label:
            lbl.set_visible(False)

        self.fig.tight_layout(pad=1.0)
        self.canvas.draw()

    def reset(self):
        self.current_symbol = None
        self._placeholder()


# ── 8d. Alert Feed ─────────────────────────────────────────────────────────────
class AlertFeed(QWidget):
    """Scrollable time-stamped list of triggered alerts."""

    _ICONS = {
        "BULL": "🟢", "BEAR": "🔴", "MOVEMENT": "⚡",
        "PRICE": "🔔", "SCANNER": "🔍", "INFO": "ℹ️",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(160)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(4)

        hdr = QHBoxLayout()
        title = QLabel("LIVE ALERTS")
        title.setStyleSheet("font-size:10px; font-weight:700; color:#58a6ff; letter-spacing:1.5px;")
        clr = QPushButton("Clear All")
        clr.setFixedHeight(22)
        clr.setFixedWidth(70)
        clr.setStyleSheet("font-size:10px; padding:2px 8px; min-height:22px;")
        clr.clicked.connect(self._clear)
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(clr)
        lay.addLayout(hdr)

        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget { font-size:11px; }"
            "QListWidget::item { padding: 4px 8px; }"
        )
        lay.addWidget(self._list)

    def add(self, category: str, symbol: str, message: str):
        icon = self._ICONS.get(category, "•")
        ts   = datetime.now().strftime("%H:%M:%S")
        it   = QListWidgetItem(f"{ts}  {icon}  {symbol}  —  {message}")

        color = {
            "BULL":    QColor("#3fb950"),
            "BEAR":    QColor("#f85149"),
            "MOVEMENT":QColor("#d29922"),
            "PRICE":   QColor("#58a6ff"),
            "SCANNER": QColor("#bc8cff"),
        }.get(category, QColor("#8b949e"))
        it.setForeground(QBrush(color))
        it.setFont(QFont("Segoe UI", 11))

        self._list.insertItem(0, it)   # newest at top
        if self._list.count() > 100:   # cap history
            self._list.takeItem(self._list.count() - 1)

    def _clear(self):
        self._list.clear()


# ══════════════════════════════════════════════════════════════════════════════
#  §9  DIALOGS
# ══════════════════════════════════════════════════════════════════════════════

class AddPositionDialog(QDialog):
    """Dialog to add a new portfolio position."""

    def __init__(self, existing_symbols: List[str] = (), parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Position to Portfolio")
        self.setMinimumWidth(400)
        self.setModal(True)
        self._build(existing_symbols)

    def _build(self, existing: List[str]):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(20, 20, 20, 20)

        lay.addWidget(_hdr("📊  Add Portfolio Position"))

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self._combo = QComboBox()
        self._combo.setEditable(True)
        self._combo.lineEdit().setPlaceholderText("Search company…")
        for name in sorted(STOCK_CATALOG.keys()):
            sym = STOCK_CATALOG[name]
            if sym not in existing:
                self._combo.addItem(name, sym)
        form.addRow("Company:", self._combo)

        self._buy = QDoubleSpinBox()
        self._buy.setRange(0.01, 1_000_000)
        self._buy.setDecimals(2)
        self._buy.setPrefix("$ ")
        self._buy.setValue(100.00)
        form.addRow("Buy Price (avg):", self._buy)

        self._qty = QDoubleSpinBox()
        self._qty.setRange(0.001, 1_000_000)
        self._qty.setDecimals(3)
        self._qty.setValue(1.0)
        form.addRow("Quantity (shares):", self._qty)

        self._wl = QCheckBox("Add to Watchlist too")
        form.addRow("", self._wl)

        self._alert = QCheckBox("Enable alerts for this stock")
        self._alert.setChecked(True)
        form.addRow("", self._alert)

        lay.addLayout(form)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("✅  Add Position")
        ok.setObjectName("addBtn")
        ok.clicked.connect(self.accept)
        btns.addWidget(cancel)
        btns.addStretch()
        btns.addWidget(ok)
        lay.addLayout(btns)

    def values(self) -> Optional[Position]:
        raw  = self._combo.currentText().strip()
        # 1) Exact match (user selected from dropdown)
        sym  = STOCK_CATALOG.get(raw) or self._combo.currentData()

        # 2) Fuzzy match: compare cleaned catalog names against typed text
        if not sym and raw:
            query = raw.lower()
            for catalog_name, catalog_sym in STOCK_CATALOG.items():
                # Strip emoji prefix (everything before first alpha char cluster)
                clean = catalog_name.split()[-1].lower() if catalog_name.split() else ""
                full_clean = "".join(
                    c for c in catalog_name if c.isalpha() or c.isspace()
                ).strip().lower()
                if query in full_clean or full_clean.startswith(query):
                    sym  = catalog_sym
                    raw  = catalog_name
                    break

        if not sym:
            QMessageBox.warning(
                self, "Stock Not Found",
                f"Could not find a stock matching "{raw}".\n\n"
                "Please select a company from the dropdown list."
            )
            print(f"[AddPosition] WARNING — no symbol found for input: {raw!r}")
            return None

        print(f"[AddPosition] Resolved  '{raw}'  →  {sym}  "
              f"buy=${self._buy.value():.2f}  qty={self._qty.value()}")
        return Position(
            symbol        = sym,
            name          = raw,
            buy_price     = self._buy.value(),
            quantity      = self._qty.value(),
            watchlist     = self._wl.isChecked(),
            alert_enabled = self._alert.isChecked(),
        )


class AlertConfigDialog(QDialog):
    """Configure per-stock alert thresholds and preferences."""

    def __init__(self, symbol: str, name: str,
                 current_price: float,
                 existing: Optional[AlertConfig] = None,
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Alert Config — {name}")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build(symbol, name, current_price, existing or AlertConfig())

    def _build(self, sym, name, price, cfg: AlertConfig):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(20, 20, 20, 20)

        lay.addWidget(_hdr(f"🔔  Alerts  —  {name} ({sym})"))
        lay.addWidget(QLabel(f"Current price:  ${price:,.2f}"))

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self._above = QDoubleSpinBox()
        self._above.setRange(0, 1_000_000)
        self._above.setDecimals(2)
        self._above.setPrefix("$ ")
        self._above.setValue(cfg.above_price or round(price * 1.05, 2))
        form.addRow("🟢  Alert above:", self._above)

        self._below = QDoubleSpinBox()
        self._below.setRange(0, 1_000_000)
        self._below.setDecimals(2)
        self._below.setPrefix("$ ")
        self._below.setValue(cfg.below_price or round(price * 0.95, 2))
        form.addRow("🔴  Alert below:", self._below)

        self._move = QDoubleSpinBox()
        self._move.setRange(0.5, 20.0)
        self._move.setDecimals(1)
        self._move.setSuffix(" %")
        self._move.setValue(cfg.movement_threshold)
        form.addRow("⚡  Movement threshold:", self._move)

        self._trend = QCheckBox("Enable MA / RSI trend signals")
        self._trend.setChecked(cfg.trend_alerts)
        form.addRow("", self._trend)

        self._movement_cb = QCheckBox("Enable sudden movement alerts")
        self._movement_cb.setChecked(cfg.movement_alerts)
        form.addRow("", self._movement_cb)

        lay.addLayout(form)

        lay.addWidget(QLabel(
            "Set price to 0 to disable that price alert direction."
        ))

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("💾  Save")
        ok.setObjectName("addBtn")
        ok.clicked.connect(self.accept)
        btns.addWidget(cancel)
        btns.addStretch()
        btns.addWidget(ok)
        lay.addLayout(btns)

    def values(self) -> AlertConfig:
        return AlertConfig(
            above_price        = self._above.value(),
            below_price        = self._below.value(),
            movement_threshold = self._move.value(),
            trend_alerts       = self._trend.isChecked(),
            movement_alerts    = self._movement_cb.isChecked(),
        )


class AddWatchlistDialog(QDialog):
    """Add a stock to the watchlist (without buying it)."""

    def __init__(self, existing: List[str] = (), parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add to Watchlist")
        self.setMinimumWidth(360)
        self.setModal(True)
        self._build(existing)

    def _build(self, existing):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.addWidget(_hdr("👁  Add to Watchlist"))

        self._combo = QComboBox()
        self._combo.setEditable(True)
        self._combo.lineEdit().setPlaceholderText("Search company…")
        for name in sorted(STOCK_CATALOG.keys()):
            if STOCK_CATALOG[name] not in existing:
                self._combo.addItem(name, STOCK_CATALOG[name])
        lay.addWidget(self._combo)

        self._alert = QCheckBox("Enable alerts for this stock")
        self._alert.setChecked(True)
        lay.addWidget(self._alert)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("✅  Add")
        ok.setObjectName("addBtn")
        ok.clicked.connect(self.accept)
        btns.addWidget(cancel)
        btns.addStretch()
        btns.addWidget(ok)
        lay.addLayout(btns)

    def values(self) -> Tuple[Optional[str], bool]:
        name = self._combo.currentText().strip()
        sym  = STOCK_CATALOG.get(name) or self._combo.currentData()
        return sym, self._alert.isChecked()


def _hdr(text: str) -> QLabel:
    """Small helper: styled section header label."""
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size:15px; font-weight:700; color:#e6edf3;")
    return lbl


# ══════════════════════════════════════════════════════════════════════════════
#  §10  TABS
# ══════════════════════════════════════════════════════════════════════════════

# ── Portfolio Tab ──────────────────────────────────────────────────────────────
class PortfolioTab(QWidget):
    """
    Left: table of positions with live P&L and technical signals.
    Right (shared with detail panel in MainWindow): updates when a row is clicked.
    """
    row_selected = pyqtSignal(str)   # emits symbol

    # Column indices
    COL_FLAG, COL_NAME, COL_SYM, COL_BUY, COL_NOW = 0, 1, 2, 3, 4
    COL_QTY, COL_INVESTED, COL_VALUE, COL_PL, COL_PLpct = 5, 6, 7, 8, 9
    COL_RSI, COL_SIGNAL = 10, 11
    NCOLS = 12

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        # Button bar
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        add_btn = QPushButton("＋  Add Position")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self._add)

        self._rm_btn = QPushButton("✕  Remove")
        self._rm_btn.setObjectName("removeBtn")
        self._rm_btn.clicked.connect(self._remove)

        self._al_btn = QPushButton("🔔  Configure Alert")
        self._al_btn.setObjectName("alertBtn")
        self._al_btn.clicked.connect(self._configure_alert)

        btn_row.addWidget(add_btn)
        btn_row.addWidget(self._rm_btn)
        btn_row.addWidget(self._al_btn)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        # Table
        headers = [
            "🔔", "Company", "Symbol",
            "Buy $", "Now $", "Qty",
            "Invested", "Value", "P&L $", "P&L %",
            "RSI", "Signal",
        ]
        self._table = QTableWidget(0, self.NCOLS)
        self._table.setHorizontalHeaderLabels(headers)
        h = self._table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Interactive)
        h.setSectionResizeMode(self.COL_NAME,   QHeaderView.Stretch)
        h.setSectionResizeMode(self.COL_SIGNAL, QHeaderView.Stretch)
        self._table.setColumnWidth(self.COL_FLAG, 28)
        self._table.setColumnWidth(self.COL_SYM,  55)
        self._table.setColumnWidth(self.COL_BUY,  75)
        self._table.setColumnWidth(self.COL_NOW,  75)
        self._table.setColumnWidth(self.COL_QTY,  65)
        self._table.setColumnWidth(self.COL_INVESTED, 80)
        self._table.setColumnWidth(self.COL_VALUE, 80)
        self._table.setColumnWidth(self.COL_PL,   80)
        self._table.setColumnWidth(self.COL_PLpct, 65)
        self._table.setColumnWidth(self.COL_RSI,  50)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.cellClicked.connect(self._on_click)

        # ── Empty-state placeholder (shown when portfolio has no positions) ────
        # Hidden as soon as the first position is added.
        self._empty_lbl = QLabel(
            "📭  Your portfolio is empty\n\n"
            "Click  ＋ Add Position  above to start tracking a stock.\n\n"
            "You will see live prices, P&L, RSI, and trend signals here."
        )
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._empty_lbl.setWordWrap(True)
        self._empty_lbl.setStyleSheet(
            "color: #8b949e; font-size: 14px; line-height: 1.8;"
            "background-color: #161b22;"
            "border: 2px dashed #30363d; border-radius: 12px; padding: 40px 30px;"
        )
        lay.addWidget(self._empty_lbl)   # stacks below the table in the layout
        lay.addWidget(self._table)

    # ── called by MainWindow ───────────────────────────────────────────────────
    def set_app(self, app: "MainWindow"):
        """Give the tab a reference to the main window for data access."""
        self._app = app

    def populate(self, analyses: Dict[str, StockAnalysis]):
        """
        Refresh every row.  Preserves the current row selection.
        Shows the empty-state placeholder when no positions exist.
        """
        selected_sym = self._selected_symbol()
        portfolio    = self._app.state["portfolio"]

        # Toggle between empty-state label and live data table
        is_empty = len(portfolio) == 0
        self._empty_lbl.setVisible(is_empty)
        self._table.setVisible(not is_empty)

        if is_empty:
            return  # nothing to render

        self._table.setRowCount(len(portfolio))
        for row, pos_dict in enumerate(portfolio):
            sym = pos_dict["symbol"]
            sa  = analyses.get(sym)
            self._fill_row(row, pos_dict, sa)
            self._table.setRowHeight(row, 44)

        # Restore selection
        if selected_sym:
            self._select_row_by_sym(selected_sym)

    def _fill_row(self, row: int, pos: dict, sa: Optional[StockAnalysis]):
        GREEN = QColor("#3fb950")
        RED   = QColor("#f85149")
        WHITE = QColor("#e6edf3")
        DIM   = QColor("#8b949e")
        GREY  = QColor("#8b949e")

        buy   = pos.get("buy_price", 0)
        qty   = pos.get("quantity",  1)
        alert = pos.get("alert_enabled", False)
        inv   = buy * qty

        # now_p is None when the background fetch hasn't returned yet.
        # The row still appears immediately after "Add Position" — price shows
        # "⟳ Fetching..." until the PriceWorker thread completes.
        now_p  = sa.current_price if (sa and not sa.error) else None
        value  = (now_p * qty)       if now_p  is not None else None
        pl     = (value - inv)       if value   is not None else None
        pl_pct = (pl / inv * 100)    if (pl is not None and inv) else None
        is_up  = (pl >= 0)           if pl      is not None else True

        def cell(text, color=None, bold=False,
                 align=Qt.AlignVCenter | Qt.AlignLeft) -> QTableWidgetItem:
            it = QTableWidgetItem(str(text))
            if color: it.setForeground(QBrush(color))
            it.setFont(QFont("Segoe UI", 11, QFont.Bold if bold else QFont.Normal))
            it.setTextAlignment(align)
            return it

        R = Qt.AlignRight | Qt.AlignVCenter
        C = Qt.AlignCenter | Qt.AlignVCenter

        alert_flag = "🔔" if alert else "○"
        self._table.setItem(row, self.COL_FLAG,     cell(alert_flag,             DIM,   False, C))
        self._table.setItem(row, self.COL_NAME,     cell(pos["name"],            WHITE, True))
        self._table.setItem(row, self.COL_SYM,      cell(pos["symbol"],          DIM))
        self._table.setItem(row, self.COL_BUY,      cell(f"${buy:,.2f}",         DIM,   False, R))

        # Current price column — colour shows today's direction
        if sa and not sa.error:
            now_str, now_color = f"${now_p:,.2f}", (GREEN if sa.pct_1d >= 0 else RED)
        elif sa and sa.error:
            now_str, now_color = "Error", RED
        else:
            now_str, now_color = "⟳ Fetching...", DIM   # no live data yet

        self._table.setItem(row, self.COL_NOW,     cell(now_str, now_color, True, R))
        self._table.setItem(row, self.COL_QTY,     cell(f"{qty:.2f}",  DIM, False, R))
        self._table.setItem(row, self.COL_INVESTED, cell(f"${inv:,.2f}", DIM, False, R))

        # Value, P&L, P&L% — show "⟳ Fetching..." until live price arrives
        FETCH = "⟳ Fetching..."
        pl_c  = (GREEN if is_up else RED) if pl is not None else DIM
        sign  = "+" if is_up else ""

        self._table.setItem(row, self.COL_VALUE,  cell(
            f"${value:,.2f}"      if value  is not None else FETCH, WHITE, False, R))
        self._table.setItem(row, self.COL_PL,     cell(
            f"{sign}${pl:,.2f}"   if pl     is not None else FETCH, pl_c,  True,  R))
        self._table.setItem(row, self.COL_PLpct,  cell(
            f"{sign}{pl_pct:.2f}%" if pl_pct is not None else FETCH, pl_c, True,  R))

        rsi_v = str(sa.rsi) if sa and sa.rsi is not None else "—"
        rsi_c = {"OVERSOLD": GREEN, "OVERBOUGHT": RED}.get(
            sa.rsi_zone if sa else "NEUTRAL", GREY)
        self._table.setItem(row, self.COL_RSI,      cell(rsi_v, rsi_c, False, C))

        sig_c = QColor(sa.signal_color) if sa else GREY
        self._table.setItem(row, self.COL_SIGNAL,   cell(
            sa.signal_label if sa and not sa.error else "—", sig_c, True))

    # ── internal ───────────────────────────────────────────────────────────────
    def _selected_symbol(self) -> Optional[str]:
        rows = self._table.selectedItems()
        if not rows:
            return None
        row = self._table.row(rows[0])
        it  = self._table.item(row, self.COL_SYM)
        return it.text() if it else None

    def _select_row_by_sym(self, sym: str):
        for row in range(self._table.rowCount()):
            it = self._table.item(row, self.COL_SYM)
            if it and it.text() == sym:
                self._table.selectRow(row)
                break

    def _on_click(self, row, _col):
        it = self._table.item(row, self.COL_SYM)
        if it:
            self.row_selected.emit(it.text())

    def _add(self):
        existing = [p["symbol"] for p in self._app.state["portfolio"]]
        dlg = AddPositionDialog(existing, parent=self)
        dlg.setStyleSheet(APP_STYLE)
        if dlg.exec_() == QDialog.Accepted:
            pos = dlg.values()
            if pos:
                self._app.add_position(pos)

    def _remove(self):
        sym = self._selected_symbol()
        if not sym:
            return
        reply = QMessageBox.question(
            self, "Remove Position",
            f"Remove {sym} from your portfolio?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._app.remove_position(sym)

    def _configure_alert(self):
        sym = self._selected_symbol()
        if not sym:
            return
        sa = self._app.analyses.get(sym)
        price = sa.current_price if sa else 0.0
        name  = SYM_TO_NAME.get(sym, sym)
        cfg   = self._app.get_alert_config(sym)
        dlg   = AlertConfigDialog(sym, name, price, cfg, parent=self)
        dlg.setStyleSheet(APP_STYLE)
        if dlg.exec_() == QDialog.Accepted:
            self._app.save_alert_config(sym, dlg.values())


# ── Watchlist Tab ──────────────────────────────────────────────────────────────
class WatchlistTab(QWidget):
    row_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        # Buttons
        btn_row = QHBoxLayout()
        add = QPushButton("＋  Add to Watchlist")
        add.setObjectName("addBtn")
        add.clicked.connect(self._add)

        self._rm = QPushButton("✕  Remove")
        self._rm.setObjectName("removeBtn")
        self._rm.clicked.connect(self._remove)

        self._al = QPushButton("🔔  Configure Alert")
        self._al.setObjectName("alertBtn")
        self._al.clicked.connect(self._configure_alert)

        btn_row.addWidget(add)
        btn_row.addWidget(self._rm)
        btn_row.addWidget(self._al)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        # Table
        headers = ["🔔", "Company", "Symbol", "Price", "1D Change", "1D %", "RSI", "Signal"]
        self._table = QTableWidget(0, len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        h = self._table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Interactive)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(7, QHeaderView.Stretch)
        self._table.setColumnWidth(0, 28)
        self._table.setColumnWidth(2, 55)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.cellClicked.connect(self._on_click)
        lay.addWidget(self._table)

    def set_app(self, app: "MainWindow"):
        self._app = app

    def populate(self, analyses: Dict[str, StockAnalysis]):
        wl = self._app.state["watchlist"]
        selected = self._selected_symbol()
        self._table.setRowCount(len(wl))

        GREEN = QColor("#3fb950"); RED = QColor("#f85149")
        WHITE = QColor("#e6edf3"); DIM = QColor("#8b949e")
        R = Qt.AlignRight | Qt.AlignVCenter
        C = Qt.AlignCenter  | Qt.AlignVCenter

        for row, entry in enumerate(wl):
            sym    = entry["symbol"]
            alert  = entry.get("alert_enabled", False)
            sa     = analyses.get(sym)
            name   = SYM_TO_NAME.get(sym, sym)

            def cell(t, col=None, bold=False, align=Qt.AlignVCenter | Qt.AlignLeft):
                it = QTableWidgetItem(str(t))
                if col: it.setForeground(QBrush(col))
                it.setFont(QFont("Segoe UI", 11, QFont.Bold if bold else QFont.Normal))
                it.setTextAlignment(align)
                return it

            tc = GREEN if (sa and sa.pct_1d >= 0) else RED
            self._table.setItem(row, 0, cell("🔔" if alert else "○", DIM, align=C))
            self._table.setItem(row, 1, cell(name, WHITE, True))
            self._table.setItem(row, 2, cell(sym,  DIM))
            self._table.setItem(row, 3, cell(f"${sa.current_price:,.2f}" if sa and not sa.error else "N/A",
                                             tc, True, R))
            self._table.setItem(row, 4, cell(f"${sa.change_1d:+,.2f}" if sa and not sa.error else "—",
                                             tc, False, R))
            self._table.setItem(row, 5, cell(f"{sa.pct_1d:+.2f}%" if sa and not sa.error else "—",
                                             tc, True, R))
            rsi_c = {"OVERSOLD": GREEN, "OVERBOUGHT": RED}.get(
                sa.rsi_zone if sa else "NEUTRAL", DIM)
            self._table.setItem(row, 6, cell(str(sa.rsi) if sa and sa.rsi else "—",
                                             rsi_c, False, C))
            sc = QColor(sa.signal_color) if sa else DIM
            self._table.setItem(row, 7, cell(sa.signal_label if sa and not sa.error else "—",
                                             sc, True))
            self._table.setRowHeight(row, 44)

        if selected:
            self._select_by_sym(selected)

    def _selected_symbol(self) -> Optional[str]:
        rows = self._table.selectedItems()
        if not rows: return None
        it = self._table.item(self._table.row(rows[0]), 2)
        return it.text() if it else None

    def _select_by_sym(self, sym: str):
        for row in range(self._table.rowCount()):
            it = self._table.item(row, 2)
            if it and it.text() == sym:
                self._table.selectRow(row); break

    def _on_click(self, row, _col):
        it = self._table.item(row, 2)
        if it: self.row_selected.emit(it.text())

    def _add(self):
        existing = [e["symbol"] for e in self._app.state["watchlist"]] + \
                   [p["symbol"] for p in self._app.state["portfolio"]]
        dlg = AddWatchlistDialog(existing, parent=self)
        dlg.setStyleSheet(APP_STYLE)
        if dlg.exec_() == QDialog.Accepted:
            sym, alert = dlg.values()
            if sym:
                self._app.add_watchlist(sym, alert)

    def _remove(self):
        sym = self._selected_symbol()
        if sym:
            self._app.remove_watchlist(sym)

    def _configure_alert(self):
        sym = self._selected_symbol()
        if not sym: return
        sa    = self._app.analyses.get(sym)
        price = sa.current_price if sa else 0.0
        cfg   = self._app.get_alert_config(sym)
        dlg   = AlertConfigDialog(sym, SYM_TO_NAME.get(sym, sym), price, cfg, parent=self)
        dlg.setStyleSheet(APP_STYLE)
        if dlg.exec_() == QDialog.Accepted:
            self._app.save_alert_config(sym, dlg.values())


# ── Market Scanner Tab ─────────────────────────────────────────────────────────
class ScannerTab(QWidget):
    row_selected = pyqtSignal(str)

    # Column indices
    COL_TREND, COL_NAME, COL_SYM, COL_PRICE = 0, 1, 2, 3
    COL_CHANGE, COL_PCT, COL_RSI, COL_MA, COL_SIGNAL = 4, 5, 6, 7, 8
    NCOLS = 9

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._results: List[StockAnalysis] = []

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        # Controls
        ctrl = QHBoxLayout()
        self._scan_btn = QPushButton("🔍  Scan Market Now")
        self._scan_btn.setObjectName("scanBtn")
        self._scan_btn.clicked.connect(self._scan)

        self._filter = QComboBox()
        self._filter.addItems(["All Stocks", "Top Gainers", "Top Losers",
                                "Bullish Signals", "Bearish Signals",
                                "Oversold (RSI<30)", "Overbought (RSI>70)"])
        self._filter.currentIndexChanged.connect(self._apply_filter)

        self._progress = QProgressBar()
        self._progress.setFixedHeight(6)
        self._progress.setVisible(False)

        self._scan_ts = QLabel("Last scan:  —")
        self._scan_ts.setStyleSheet("color:#8b949e; font-size:11px;")

        ctrl.addWidget(self._scan_btn)
        ctrl.addWidget(QLabel("Filter:"))
        ctrl.addWidget(self._filter)
        ctrl.addStretch()
        ctrl.addWidget(self._scan_ts)
        lay.addLayout(ctrl)
        lay.addWidget(self._progress)

        # Disclaimer
        disc = QLabel(
            "⚠  Scanner signals are TECHNICAL ESTIMATIONS only — not investment advice."
        )
        disc.setStyleSheet("font-size:10px; color:#6e7681; font-style:italic;")
        lay.addWidget(disc)

        # Table
        headers = ["Trend", "Company", "Symbol", "Price",
                   "Change $", "Change %", "RSI", "MA Signal", "Alert Signal"]
        self._table = QTableWidget(0, self.NCOLS)
        self._table.setHorizontalHeaderLabels(headers)
        h = self._table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Interactive)
        h.setSectionResizeMode(self.COL_NAME,   QHeaderView.Stretch)
        h.setSectionResizeMode(self.COL_SIGNAL, QHeaderView.Stretch)
        self._table.setColumnWidth(self.COL_TREND, 40)
        self._table.setColumnWidth(self.COL_SYM,   55)
        self._table.setColumnWidth(self.COL_PRICE, 75)
        self._table.setColumnWidth(self.COL_CHANGE,75)
        self._table.setColumnWidth(self.COL_PCT,   65)
        self._table.setColumnWidth(self.COL_RSI,   45)
        self._table.setColumnWidth(self.COL_MA,    120)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.cellClicked.connect(self._on_click)
        lay.addWidget(self._table)

    def set_app(self, app: "MainWindow"):
        self._app = app

    def _scan(self):
        self._scan_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setValue(0)

        self._worker = ScannerWorker()
        self._worker.progress.connect(lambda d, t: self._progress.setValue(int(d / t * 100)))
        self._worker.scan_done.connect(self._on_scan_done)
        self._worker.start()

    def _on_scan_done(self, results: List[StockAnalysis]):
        self._results = results
        self._scan_btn.setEnabled(True)
        self._progress.setVisible(False)
        self._scan_ts.setText(f"Last scan:  {datetime.now():%H:%M:%S}")
        self._apply_filter()

        # Fire scanner alerts if enabled
        if self._app.state["settings"].get("scan_alerts_global"):
            for sa in results[:5]:   # top 5 movers
                if abs(sa.pct_1d) >= 3:
                    self._app.fire_notification(
                        "SCANNER", sa.symbol,
                        f"Big move: {sa.pct_1d:+.2f}%  |  {sa.signal_label}"
                    )

    def _apply_filter(self):
        idx = self._filter.currentIndex()
        filtered = list(self._results)
        if   idx == 1: filtered = [s for s in filtered if s.pct_1d >  0][:10]
        elif idx == 2: filtered = [s for s in filtered if s.pct_1d <= 0][-10:]
        elif idx == 3: filtered = [s for s in filtered
                                   if s.signal_code in ("STRONG_BUY","BUY","MILD_BUY")]
        elif idx == 4: filtered = [s for s in filtered
                                   if s.signal_code in ("STRONG_SELL","SELL","MILD_SELL")]
        elif idx == 5: filtered = [s for s in filtered if s.rsi is not None and s.rsi < 30]
        elif idx == 6: filtered = [s for s in filtered if s.rsi is not None and s.rsi > 70]
        self._fill_table(filtered)

    def _fill_table(self, data: List[StockAnalysis]):
        GREEN = QColor("#3fb950"); RED = QColor("#f85149")
        WHITE = QColor("#e6edf3"); DIM = QColor("#8b949e")
        R = Qt.AlignRight | Qt.AlignVCenter
        C = Qt.AlignCenter | Qt.AlignVCenter

        self._table.setRowCount(len(data))
        for row, sa in enumerate(data):
            tc    = GREEN if sa.pct_1d >= 0 else RED
            arrow = "▲" if sa.pct_1d >= 0 else "▼"

            def cell(t, col=None, bold=False, align=Qt.AlignVCenter | Qt.AlignLeft):
                it = QTableWidgetItem(str(t))
                if col: it.setForeground(QBrush(col))
                it.setFont(QFont("Segoe UI", 11, QFont.Bold if bold else QFont.Normal))
                it.setTextAlignment(align)
                return it

            self._table.setItem(row, self.COL_TREND,  cell(arrow, tc, True, C))
            self._table.setItem(row, self.COL_NAME,   cell(sa.name,  WHITE, True))
            self._table.setItem(row, self.COL_SYM,    cell(sa.symbol, DIM))
            self._table.setItem(row, self.COL_PRICE,  cell(f"${sa.current_price:,.2f}", WHITE, True, R))
            self._table.setItem(row, self.COL_CHANGE, cell(f"${sa.change_1d:+,.2f}", tc, False, R))
            self._table.setItem(row, self.COL_PCT,    cell(f"{sa.pct_1d:+.2f}%", tc, True, R))

            rsi_c = {"OVERSOLD": GREEN, "OVERBOUGHT": RED}.get(sa.rsi_zone, DIM)
            self._table.setItem(row, self.COL_RSI,    cell(str(sa.rsi) if sa.rsi else "—",
                                                           rsi_c, False, C))
            ma_c = {"BULL_CROSS": GREEN, "BULL": QColor("#7ee787"),
                    "BEAR_CROSS": RED,   "BEAR": QColor("#ff7b72")}.get(sa.sma_code, DIM)
            self._table.setItem(row, self.COL_MA,     cell(sa.sma_label, ma_c))
            sc = QColor(sa.signal_color)
            self._table.setItem(row, self.COL_SIGNAL, cell(sa.signal_label, sc, True))
            self._table.setRowHeight(row, 42)

    def _on_click(self, row, _col):
        it = self._table.item(row, self.COL_SYM)
        if it: self.row_selected.emit(it.text())


# ── Settings Tab ───────────────────────────────────────────────────────────────
class SettingsTab(QWidget):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        outer.addWidget(_hdr("⚙  Settings"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        inner = QWidget()
        lay   = QVBoxLayout(inner)
        lay.setSpacing(16)
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        # ── Refresh ───────────────────────────────────────────────────────────
        grp1 = QGroupBox("Auto Refresh")
        f1   = QFormLayout(grp1)
        self._refresh = QSpinBox()
        self._refresh.setRange(10, 300)
        self._refresh.setSuffix(" s")
        self._refresh.setValue(30)
        f1.addRow("Refresh interval:", self._refresh)
        lay.addWidget(grp1)

        # ── Alerts ────────────────────────────────────────────────────────────
        grp2 = QGroupBox("Alert Preferences")
        f2   = QFormLayout(grp2)
        self._move_thresh = QDoubleSpinBox()
        self._move_thresh.setRange(0.5, 20.0)
        self._move_thresh.setSuffix(" %")
        self._move_thresh.setValue(2.0)
        self._move_thresh.setToolTip(
            "Default threshold: if a stock moves this much in one day, fire a movement alert."
        )
        f2.addRow("Default movement threshold:", self._move_thresh)

        self._trend_global    = QCheckBox("Enable MA/RSI trend alerts globally")
        self._trend_global.setChecked(True)
        f2.addRow("", self._trend_global)

        self._movement_global = QCheckBox("Enable sudden movement alerts globally")
        self._movement_global.setChecked(True)
        f2.addRow("", self._movement_global)

        self._scan_global     = QCheckBox("Notify on scanner results (top movers)")
        f2.addRow("", self._scan_global)

        lay.addWidget(grp2)

        # ── Advance Warning ───────────────────────────────────────────────────
        grp3 = QGroupBox("Advance Warning")
        f3   = QFormLayout(grp3)
        f3.addRow(QLabel(
            "When active, sends a trend signal alert the selected number of\n"
            "hours before US market close (4:00 PM ET) if signals are notable."
        ))
        self._adv_hours = QComboBox()
        self._adv_hours.addItems(["Disabled", "1 hour before close",
                                   "2 hours before close", "3 hours before close"])
        f3.addRow("Advance warning:", self._adv_hours)
        lay.addWidget(grp3)

        # Disclaimer
        disc = QLabel(
            "⚠  IMPORTANT: All technical signals are ESTIMATIONS based on Moving\n"
            "     Averages and RSI. They describe historical tendencies only.\n"
            "     They are NOT financial predictions or investment advice.\n"
            "     Never make investment decisions based solely on these signals."
        )
        disc.setStyleSheet(
            "font-size:11px; color:#6e7681; font-style:italic;"
            "background:#161b22; border:1px solid #30363d;"
            "border-radius:8px; padding:12px;"
        )
        disc.setWordWrap(True)
        lay.addWidget(disc)

        # Save button
        save = QPushButton("💾  Save Settings")
        save.setObjectName("addBtn")
        save.clicked.connect(self._save)
        outer.addWidget(save)

    def load_settings(self, s: dict):
        self._refresh.setValue(s.get("refresh_interval", 30))
        self._move_thresh.setValue(s.get("default_movement_threshold", 2.0))
        self._trend_global.setChecked(s.get("trend_alerts_global", True))
        self._movement_global.setChecked(s.get("movement_alerts_global", True))
        self._scan_global.setChecked(s.get("scan_alerts_global", False))
        hours = s.get("advance_warning_hours", 0)
        self._adv_hours.setCurrentIndex(hours)

    def _save(self):
        hours = self._adv_hours.currentIndex()
        self.settings_changed.emit({
            "refresh_interval":           self._refresh.value(),
            "default_movement_threshold": self._move_thresh.value(),
            "trend_alerts_global":        self._trend_global.isChecked(),
            "movement_alerts_global":     self._movement_global.isChecked(),
            "scan_alerts_global":         self._scan_global.isChecked(),
            "advance_warning_hours":      hours,
        })


# ══════════════════════════════════════════════════════════════════════════════
#  §11  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """
    Root window.  Layout:
      ┌─ header: title + 4 stat cards ──────────────────────────┐
      ├─ QSplitter (horizontal) ─────────────────────────────────┤
      │  Left: QTabWidget (Portfolio, Watchlist, Scanner, Cfg)   │
      │  Right: SignalPanel + ChartWidget (detail for selection) │
      ├─ Alert Feed (fixed height) ──────────────────────────────┤
      └─ Status Bar ─────────────────────────────────────────────┘
    """

    def __init__(self):
        super().__init__()
        # ── State ─────────────────────────────────────────────────────────────
        self.state     = DataStore.load()
        self.analyses: Dict[str, StockAnalysis] = {}
        self._fired:   set = set()   # prevent repeated alert noise
        self._fetcher: Optional[PriceWorker] = None
        self._all_symbols_cached: List[str] = []

        # ── Window ────────────────────────────────────────────────────────────
        self.setWindowTitle("📊  Smart Stock Tracker  —  Advanced Edition")
        self.setMinimumSize(1200, 700)
        self.resize(1440, 840)

        # ── Build UI ──────────────────────────────────────────────────────────
        self._build_ui()
        QApplication.instance().setStyleSheet(APP_STYLE)
        QApplication.instance().setFont(QFont("Segoe UI", 11))

        # Load settings into settings tab
        self._settings_tab.load_settings(self.state["settings"])

        # ── Timers ────────────────────────────────────────────────────────────
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh_data)
        interval = self.state["settings"].get("refresh_interval", 30) * 1000
        self._refresh_timer.start(interval)

        self._countdown = self.state["settings"].get("refresh_interval", 30)
        self._cd_timer  = QTimer(self)
        self._cd_timer.timeout.connect(self._tick)
        self._cd_timer.start(1000)

        # ── Advance warning timer (checks once per minute) ────────────────────
        self._adv_timer = QTimer(self)
        self._adv_timer.timeout.connect(self._check_advance_warning)
        self._adv_timer.start(60_000)

        # Initial load
        QTimer.singleShot(500, self.refresh_data)

    # ── UI construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 6)
        root.setSpacing(10)

        root.addWidget(self._mk_header())

        # Main content splitter (tabs | detail)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._mk_tabs())
        splitter.addWidget(self._mk_detail_panel())
        splitter.setSizes([800, 440])
        splitter.setHandleWidth(1)
        root.addWidget(splitter, stretch=1)

        # Alert feed
        self._alert_feed = AlertFeed()
        root.addWidget(self._alert_feed)

        self._mk_status_bar()

    def _mk_header(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #161b22, stop:1 #0a0e17);
                border: 1px solid #30363d;
                border-radius: 10px;
            }
        """)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(16, 12, 16, 12)

        # Title
        titles = QVBoxLayout()
        t = QLabel("📊  Smart Stock Tracker")
        t.setStyleSheet(
            "font-size:22px; font-weight:800; color:#e6edf3;"
            "background:transparent; border:none;"
        )
        s = QLabel(
            "Portfolio Manager  ·  Intelligent Signals  ·  Market Scanner  "
            "·  Auto-refresh every 30 s"
        )
        s.setStyleSheet("font-size:11px; color:#8b949e; background:transparent; border:none;")
        titles.addWidget(t)
        titles.addWidget(s)
        lay.addLayout(titles)
        lay.addStretch()

        # Stat cards
        self._card_value  = StatCard("💰", "PORTFOLIO VALUE")
        self._card_today  = StatCard("📈", "TODAY'S P&L")
        self._card_total  = StatCard("💎", "TOTAL P&L")
        self._card_alerts = StatCard("🔔", "ACTIVE ALERTS")

        # Timestamp
        ts_col = QVBoxLayout()
        self._ts_lbl = QLabel("Last updated: —")
        self._ts_lbl.setStyleSheet(
            "font-size:11px; color:#58a6ff; background:transparent; border:none;"
        )
        refresh_btn = QPushButton("⟳  Refresh Now")
        refresh_btn.setObjectName("scanBtn")
        refresh_btn.setFixedWidth(140)
        refresh_btn.clicked.connect(self.refresh_data)
        ts_col.addWidget(self._ts_lbl)
        ts_col.addWidget(refresh_btn)

        for card in (self._card_value, self._card_today, self._card_total, self._card_alerts):
            lay.addWidget(card)
        lay.addSpacing(8)
        lay.addLayout(ts_col)
        return frame

    def _mk_tabs(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()

        self._portfolio_tab = PortfolioTab()
        self._portfolio_tab.set_app(self)
        self._portfolio_tab.row_selected.connect(self._on_symbol_selected)

        self._watchlist_tab = WatchlistTab()
        self._watchlist_tab.set_app(self)
        self._watchlist_tab.row_selected.connect(self._on_symbol_selected)

        self._scanner_tab = ScannerTab()
        self._scanner_tab.set_app(self)
        self._scanner_tab.row_selected.connect(self._on_symbol_selected)

        self._settings_tab = SettingsTab()
        self._settings_tab.settings_changed.connect(self._apply_settings)

        self._tabs.addTab(self._portfolio_tab, "📊  Portfolio")
        self._tabs.addTab(self._watchlist_tab, "👁  Watchlist")
        self._tabs.addTab(self._scanner_tab,   "🔍  Market Scanner")
        self._tabs.addTab(self._settings_tab,  "⚙  Settings")

        lay.addWidget(self._tabs)
        return w

    def _mk_detail_panel(self) -> QWidget:
        """Right panel: signal analysis + chart."""
        w = QWidget()
        w.setMinimumWidth(380)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(4, 0, 0, 0)
        lay.setSpacing(6)

        grp = QGroupBox("Stock Analysis")
        gl  = QVBoxLayout(grp)
        gl.setSpacing(6)

        self._signal_panel = SignalPanel()
        gl.addWidget(self._signal_panel)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#30363d;")
        gl.addWidget(sep)

        self._chart = ChartWidget()
        gl.addWidget(self._chart, stretch=1)

        lay.addWidget(grp, stretch=1)
        return w

    def _mk_status_bar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._status_lbl = QLabel("  Ready")
        self._cd_lbl     = QLabel("")
        sb.addWidget(self._status_lbl)
        sb.addPermanentWidget(self._cd_lbl)

    # ── Data refresh ──────────────────────────────────────────────────────────
    def refresh_data(self):
        symbols = self._all_symbols()
        if not symbols:
            self._status_lbl.setText("  No stocks to track — add a position or watchlist entry.")
            return

        self._status_lbl.setText(f"  ⟳  Fetching {len(symbols)} stocks…")
        self._countdown = self.state["settings"].get("refresh_interval", 30)
        self._refresh_timer.stop()

        self._fetcher = PriceWorker(
            symbols,
            self.state.get("alert_configs", {}),
            self.state.get("settings", {}),
        )
        self._fetcher.result_ready.connect(self._on_data)
        self._fetcher.fetch_error.connect(
            lambda m: self._status_lbl.setText(f"  ✗  {m}")
        )
        self._fetcher.finished.connect(
            lambda: self._refresh_timer.start(
                self.state["settings"].get("refresh_interval", 30) * 1000
            )
        )
        self._fetcher.start()

    def _on_data(self, results: List[StockAnalysis]):
        for sa in results:
            self.analyses[sa.symbol] = sa

        # Update tables
        self._portfolio_tab.populate(self.analyses)
        self._watchlist_tab.populate(self.analyses)

        # Update header cards
        self._refresh_cards()

        # Alert checks
        self._check_alerts()

        ts = datetime.now().strftime("%H:%M:%S  ·  %d %b %Y")
        self._ts_lbl.setText(f"Last updated:  {ts}")
        ok = sum(1 for sa in results if not sa.error)
        self._status_lbl.setText(f"  ✓  {ok}/{len(results)} stocks updated")

    def _refresh_cards(self):
        tot_invested = 0.0
        tot_value    = 0.0
        tot_yest     = 0.0   # yesterday's total value (for today's P&L)

        for pos in self.state["portfolio"]:
            sym = pos["symbol"]
            sa  = self.analyses.get(sym)
            if not sa or sa.error:
                continue
            qty = pos.get("quantity", 1)
            bp  = pos.get("buy_price", 0)
            tot_invested += bp * qty
            tot_value    += sa.current_price * qty
            tot_yest     += sa.prev_close    * qty

        total_pl    = tot_value - tot_invested
        today_pl    = tot_value - tot_yest
        pct_total   = (total_pl / tot_invested * 100) if tot_invested else 0
        pct_today   = (today_pl / tot_yest     * 100) if tot_yest     else 0

        self._card_value.update(f"${tot_value:,.2f}")

        sign_t = "+" if today_pl >= 0 else ""
        c_t    = "#3fb950" if today_pl >= 0 else "#f85149"
        self._card_today.update(f"{sign_t}${today_pl:,.2f}  ({sign_t}{pct_today:.2f}%)", c_t)

        sign_T = "+" if total_pl >= 0 else ""
        c_T    = "#3fb950" if total_pl >= 0 else "#f85149"
        self._card_total.update(f"{sign_T}${total_pl:,.2f}  ({sign_T}{pct_total:.2f}%)", c_T)

        # Count active alerts
        n_alerts = sum(
            1 for s in self._all_alert_symbols()
            if self.state.get("alert_configs", {}).get(s)
        )
        self._card_alerts.update(str(n_alerts))

    # ── Alert logic ───────────────────────────────────────────────────────────
    def _check_alerts(self):
        """
        ⚠ All alerts are based on technical indicators.
           They are trend estimations only, NOT predictions.
        """
        settings = self.state.get("settings", {})
        trend_ok = settings.get("trend_alerts_global", True)
        move_ok  = settings.get("movement_alerts_global", True)

        for sym, sa in self.analyses.items():
            if sa.error:
                continue
            pos   = self._find_position(sym)
            wl    = self._find_watchlist(sym)
            alert_enabled = (pos  and pos.get("alert_enabled",  False)) or \
                            (wl   and wl.get("alert_enabled",   False))
            if not alert_enabled:
                continue

            cfg = AlertConfig(**self.state.get("alert_configs", {}).get(sym, {})) \
                  if sym in self.state.get("alert_configs", {}) else AlertConfig()

            # ── Price target alerts ───────────────────────────────────────────
            key_above = f"{sym}_above"
            if cfg.above_price and sa.current_price >= cfg.above_price \
                    and key_above not in self._fired:
                self._fired.add(key_above)
                self.fire_notification(
                    "PRICE", sym,
                    f"Price ${sa.current_price:,.2f} crossed above target ${cfg.above_price:,.2f}"
                )

            key_below = f"{sym}_below"
            if cfg.below_price and sa.current_price <= cfg.below_price \
                    and key_below not in self._fired:
                self._fired.add(key_below)
                self.fire_notification(
                    "PRICE", sym,
                    f"Price ${sa.current_price:,.2f} dropped below target ${cfg.below_price:,.2f}"
                )

            # Reset fired flags when price moves back into neutral zone
            if cfg.above_price and sa.current_price < cfg.above_price * 0.995:
                self._fired.discard(key_above)
            if cfg.below_price and sa.current_price > cfg.below_price * 1.005:
                self._fired.discard(key_below)

            # ── Trend signal alerts (MA / RSI) ────────────────────────────────
            # ⚠ These are TECHNICAL ESTIMATIONS, not predictions.
            if trend_ok and cfg.trend_alerts:
                key_trend = f"{sym}_trend_{sa.signal_code}"
                if sa.signal_code in ("STRONG_BUY", "BUY") \
                        and key_trend not in self._fired:
                    self._fired.add(key_trend)
                    self.fire_notification(
                        "BULL", sym,
                        f"[TREND ESTIMATE — not a prediction]  "
                        f"RSI={sa.rsi}  {sa.sma_label}  →  {sa.signal_label}"
                    )
                elif sa.signal_code in ("STRONG_SELL", "SELL") \
                        and key_trend not in self._fired:
                    self._fired.add(key_trend)
                    self.fire_notification(
                        "BEAR", sym,
                        f"[TREND ESTIMATE — not a prediction]  "
                        f"RSI={sa.rsi}  {sa.sma_label}  →  {sa.signal_label}"
                    )
                # Reset when signal changes
                elif sa.signal_code not in ("STRONG_BUY","BUY","STRONG_SELL","SELL"):
                    self._fired.discard(f"{sym}_trend_STRONG_BUY")
                    self._fired.discard(f"{sym}_trend_BUY")
                    self._fired.discard(f"{sym}_trend_STRONG_SELL")
                    self._fired.discard(f"{sym}_trend_SELL")

            # ── Sudden movement alert ─────────────────────────────────────────
            if move_ok and cfg.movement_alerts and sa.movement_alert:
                key_move = f"{sym}_move_{datetime.now():%Y%m%d}"
                if key_move not in self._fired:
                    self._fired.add(key_move)
                    direction = "risen" if sa.pct_1d > 0 else "fallen"
                    self.fire_notification(
                        "MOVEMENT", sym,
                        f"High movement detected: {sa.pct_1d:+.2f}% today  "
                        f"(threshold: {cfg.movement_threshold:.1f}%)"
                    )

            # MA crossover special notifications
            if sa.sma_code == "BULL_CROSS":
                key_gc = f"{sym}_golden_cross_{datetime.now():%Y%m%d}"
                if key_gc not in self._fired:
                    self._fired.add(key_gc)
                    self.fire_notification(
                        "BULL", sym,
                        "[TREND SIGNAL] Golden Cross detected — SMA20 crossed above SMA50. "
                        "(Not a prediction)"
                    )
            elif sa.sma_code == "BEAR_CROSS":
                key_dc = f"{sym}_death_cross_{datetime.now():%Y%m%d}"
                if key_dc not in self._fired:
                    self._fired.add(key_dc)
                    self.fire_notification(
                        "BEAR", sym,
                        "[TREND SIGNAL] Death Cross detected — SMA20 crossed below SMA50. "
                        "(Not a prediction)"
                    )

    def _check_advance_warning(self):
        """
        Sends advance warnings before US market close.
        ⚠ These are based on current technical signals only.
        """
        hours = self.state["settings"].get("advance_warning_hours", 0)
        if not hours:
            return

        now_et = datetime.now()  # simplified: assume local ≈ ET
        market_close = dtime(16, 0)   # 4:00 PM ET
        hours_to_close = (
            market_close.hour - now_et.hour
            + (market_close.minute - now_et.minute) / 60
        )

        if 0 < hours_to_close <= hours:
            key = f"adv_warn_{now_et:%Y%m%d_%H}"
            if key not in self._fired:
                self._fired.add(key)
                for sym, sa in self.analyses.items():
                    if sa.signal_code in ("STRONG_BUY","BUY","STRONG_SELL","SELL"):
                        self.fire_notification(
                            "INFO", sym,
                            f"Advance warning ({hours}h before close): "
                            f"{sa.signal_label}  RSI={sa.rsi}  {sa.sma_label}"
                        )

    def fire_notification(self, category: str, symbol: str, message: str):
        """Show desktop notification + add to in-app feed."""
        # In-app feed
        self._alert_feed.add(category, symbol, message)

        # Desktop notification via plyer
        name = SYM_TO_NAME.get(symbol, symbol)
        title = f"📊 {name} ({symbol})"
        if PLYER_OK:
            try:
                _plyer.notify(
                    title=title, message=message,
                    app_name="Smart Stock Tracker", timeout=7
                )
                return
            except Exception:
                pass
        # Fallback: silent (avoid popup spam during auto-refresh)

    # ── Symbol selection → detail panel ──────────────────────────────────────
    def _on_symbol_selected(self, sym: str):
        sa = self.analyses.get(sym)
        if sa and not sa.error:
            self._signal_panel.refresh(sa)
            self._chart.load(sa)
        else:
            self._signal_panel.clear()
            self._chart.reset()

    # ── Portfolio / Watchlist mutations ───────────────────────────────────────
    def add_position(self, pos: Position):
        # Remove from watchlist if already there
        self.state["watchlist"] = [
            w for w in self.state["watchlist"] if w["symbol"] != pos.symbol
        ]
        self.state["portfolio"].append(asdict(pos))
        if pos.watchlist:
            self.state["watchlist"].append({"symbol": pos.symbol,
                                            "alert_enabled": pos.alert_enabled})
        DataStore.save(self.state)
        self.refresh_data()

    def remove_position(self, sym: str):
        self.state["portfolio"] = [
            p for p in self.state["portfolio"] if p["symbol"] != sym
        ]
        DataStore.save(self.state)
        self.analyses.pop(sym, None)
        self._portfolio_tab.populate(self.analyses)
        self._refresh_cards()
        self._chart.reset()
        self._signal_panel.clear()

    def add_watchlist(self, sym: str, alert: bool):
        # Don't duplicate
        if any(e["symbol"] == sym for e in self.state["watchlist"]):
            return
        self.state["watchlist"].append({"symbol": sym, "alert_enabled": alert})
        DataStore.save(self.state)
        self.refresh_data()

    def remove_watchlist(self, sym: str):
        self.state["watchlist"] = [
            e for e in self.state["watchlist"] if e["symbol"] != sym
        ]
        DataStore.save(self.state)
        self.analyses.pop(sym, None)
        self._watchlist_tab.populate(self.analyses)
        self._chart.reset()
        self._signal_panel.clear()

    def save_alert_config(self, sym: str, cfg: AlertConfig):
        self.state.setdefault("alert_configs", {})[sym] = asdict(cfg)
        DataStore.save(self.state)
        # Reset fired alerts for this symbol
        self._fired = {k for k in self._fired if not k.startswith(sym)}
        self._alert_feed.add("PRICE", sym, "Alert configuration updated.")
        self._refresh_cards()

    def get_alert_config(self, sym: str) -> Optional[AlertConfig]:
        raw = self.state.get("alert_configs", {}).get(sym)
        if raw:
            try: return AlertConfig(**raw)
            except Exception: pass
        return None

    def _apply_settings(self, s: dict):
        self.state["settings"] = s
        DataStore.save(self.state)
        # Restart refresh timer with new interval
        self._refresh_timer.stop()
        self._refresh_timer.start(s["refresh_interval"] * 1000)
        self._countdown = s["refresh_interval"]
        self._alert_feed.add("INFO", "SYSTEM", "Settings saved.")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _all_symbols(self) -> List[str]:
        seen = set()
        out  = []
        for p in self.state.get("portfolio", []):
            if p["symbol"] not in seen:
                seen.add(p["symbol"])
                out.append(p["symbol"])
        for w in self.state.get("watchlist", []):
            if w["symbol"] not in seen:
                seen.add(w["symbol"])
                out.append(w["symbol"])
        return out

    def _all_alert_symbols(self) -> List[str]:
        syms = []
        for p in self.state.get("portfolio", []):
            if p.get("alert_enabled"): syms.append(p["symbol"])
        for w in self.state.get("watchlist", []):
            if w.get("alert_enabled"): syms.append(w["symbol"])
        return syms

    def _find_position(self, sym: str) -> Optional[dict]:
        return next((p for p in self.state["portfolio"] if p["symbol"] == sym), None)

    def _find_watchlist(self, sym: str) -> Optional[dict]:
        return next((w for w in self.state["watchlist"] if w["symbol"] == sym), None)

    def _tick(self):
        if self._countdown > 0:
            self._countdown -= 1
        self._cd_lbl.setText(f"  Next refresh in  {self._countdown} s  ")

    def closeEvent(self, event):
        self._refresh_timer.stop()
        self._cd_timer.stop()
        self._adv_timer.stop()
        if self._fetcher and self._fetcher.isRunning():
            self._fetcher.quit()
            self._fetcher.wait(2000)
        event.accept()


# ══════════════════════════════════════════════════════════════════════════════
#  §12  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Stock Tracker")
    app.setApplicationVersion("2.0")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 11))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
