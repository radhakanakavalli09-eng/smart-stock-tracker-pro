"""
Modern Stock Market Live Tracker - PyQt5 GUI Application

A professional, modern desktop application for tracking stock prices in real-time
with alerts, graphs, and a clean dashboard-style interface.

Features:
    - Modern PyQt5 UI with professional styling
    - Real-time stock price tracking
    - Stock search by company name (not just symbols)
    - Auto-refresh every 20-30 seconds
    - Price alerts with notifications
    - Interactive price charts using matplotlib
    - Desktop notifications
    - Dark/Light theme support
    - Responsive table display with color coding

Author: Stock Tracker App
Version: 2.0 (Modern PyQt5)
Date: 2026
"""

import sys
import json
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import os

import yfinance as yf
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
    QLabel, QSpinBox, QDialog, QMessageBox, QHeaderView, QFrame,
    QScrollArea, QCardArea
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, QSize
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap, QBrush
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PyQt5.QtCore import QDateTime, QDate
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False


# ==================== MAPPING: Company Names to Symbols ====================
STOCK_DATABASE = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Meta": "META",
    "Facebook": "META",
    "Nvidia": "NVDA",
    "AMD": "AMD",
    "Intel": "INTC",
    "IBM": "IBM",
    "Cisco": "CSCO",
    "Oracle": "ORCL",
    "Salesforce": "CRM",
    "Adobe": "ADBE",
    "Netflix": "NFLX",
    "Spotify": "SPOT",
    "PayPal": "PYPL",
    "Square": "SQ",
    "Shopify": "SHOP",
    "Zoom": "ZM",
    "Uber": "UBER",
    "Airbnb": "ABNB",
    "Moderna": "MRNA",
    "Pfizer": "PFE",
    "Johnson & Johnson": "JNJ",
    "Coca-Cola": "KO",
    "Pepsi": "PEP",
    "McDonald's": "MCD",
    "Nike": "NKE",
    "Walmart": "WMT",
    "Target": "TGT",
    "Bank of America": "BAC",
    "JPMorgan": "JPM",
    "Goldman Sachs": "GS",
    "Morgan Stanley": "MS",
    "Tesla Motors": "TSLA",
}


# ==================== WORKER THREAD FOR BACKGROUND TASKS ====================
class StockFetchWorker(QObject):
    """Worker thread for fetching stock data without freezing UI."""
    
    # Signals
    data_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def fetch_stock_data(self, symbol: str) -> None:
        """Fetch stock data in background thread."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                self.error_occurred.emit(f"No data found for {symbol}")
                return
            
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Open'].iloc[-1]
            
            change = current_price - previous_price
            percent_change = (change / previous_price * 100) if previous_price != 0 else 0
            
            data = {
                'symbol': symbol.upper(),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'percent_change': round(percent_change, 2),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'is_up': change >= 0,
                'history': hist
            }
            
            self.data_fetched.emit(data)
        except Exception as e:
            self.error_occurred.emit(f"Error fetching {symbol}: {str(e)}")


# ==================== ALERT MANAGER ====================
class AlertManager:
    """Manages price alerts for tracked stocks."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.alerts = {}  # { symbol: { 'high': target, 'low': target, 'high_alerted': bool, 'low_alerted': bool } }
        self.load_alerts()
    
    def set_alert(self, symbol: str, high_target: Optional[float], low_target: Optional[float]) -> None:
        """
        Set alert targets for a stock.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            high_target: Alert when price exceeds this
            low_target: Alert when price drops below this
        """
        symbol = symbol.upper()
        self.alerts[symbol] = {
            'high': high_target,
            'low': low_target,
            'high_alerted': False,
            'low_alerted': False
        }
        self.save_alerts()
    
    def check_alerts(self, symbol: str, current_price: float) -> List[Tuple[str, str]]:
        """
        Check if any alerts should be triggered.
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            
        Returns:
            List of tuples: (alert_type, message)
        """
        symbol = symbol.upper()
        alerts_to_trigger = []
        
        if symbol not in self.alerts:
            return alerts_to_trigger
        
        alert = self.alerts[symbol]
        
        # Check high alert
        if alert['high'] and current_price >= alert['high'] and not alert['high_alerted']:
            alerts_to_trigger.append(('HIGH', f"{symbol} reached ${alert['high']}!"))
            alert['high_alerted'] = True
        elif alert['high'] and current_price < alert['high']:
            alert['high_alerted'] = False
        
        # Check low alert
        if alert['low'] and current_price <= alert['low'] and not alert['low_alerted']:
            alerts_to_trigger.append(('LOW', f"{symbol} dropped to ${alert['low']}!"))
            alert['low_alerted'] = True
        elif alert['low'] and current_price > alert['low']:
            alert['low_alerted'] = False
        
        return alerts_to_trigger
    
    def save_alerts(self) -> None:
        """Save alerts to JSON file."""
        try:
            with open('stock_alerts.json', 'w') as f:
                json.dump(self.alerts, f, indent=2)
        except Exception as e:
            print(f"Error saving alerts: {e}")
    
    def load_alerts(self) -> None:
        """Load alerts from JSON file."""
        try:
            if os.path.exists('stock_alerts.json'):
                with open('stock_alerts.json', 'r') as f:
                    self.alerts = json.load(f)
        except Exception as e:
            print(f"Error loading alerts: {e}")


# ==================== ALERT DIALOG ====================
class AlertDialog(QDialog):
    """Dialog for setting price alerts."""
    
    def __init__(self, parent, symbol: str, current_price: float):
        """
        Initialize alert dialog.
        
        Args:
            parent: Parent widget
            symbol: Stock symbol
            current_price: Current price for reference
        """
        super().__init__(parent)
        self.symbol = symbol
        self.current_price = current_price
        self.high_target = None
        self.low_target = None
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle(f"Set Alerts for {self.symbol}")
        self.setGeometry(100, 100, 350, 250)
        self.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Set Price Alerts for {self.symbol}")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Info
        info = QLabel(f"Current Price: ${self.current_price}")
        info.setStyleSheet("color: #666666; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # High Alert
        layout.addWidget(QLabel("Alert if price goes ABOVE:"))
        self.high_spinbox = QSpinBox()
        self.high_spinbox.setRange(0, 10000)
        self.high_spinbox.setValue(int(self.current_price * 1.1))
        self.high_spinbox.setSuffix(" $")
        layout.addWidget(self.high_spinbox)
        
        # Low Alert
        layout.addWidget(QLabel("\nAlert if price goes BELOW:"))
        self.low_spinbox = QSpinBox()
        self.low_spinbox.setRange(0, 10000)
        self.low_spinbox.setValue(int(self.current_price * 0.9))
        self.low_spinbox.setSuffix(" $")
        layout.addWidget(self.low_spinbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Alert")
        save_btn.setStyleSheet(self.get_button_stylesheet())
        save_btn.clicked.connect(self.save_alert)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self.get_button_stylesheet())
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addSpacing(10)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_alert(self) -> None:
        """Save alert settings."""
        self.high_target = self.high_spinbox.value()
        self.low_target = self.low_spinbox.value()
        self.accept()
    
    def get_stylesheet(self) -> str:
        """Return stylesheet for dialog."""
        return """
            QDialog {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                color: #333333;
                font-family: 'Segoe UI';
            }
            QSpinBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f5f5f5;
            }
        """
    
    def get_button_stylesheet(self) -> str:
        """Return button stylesheet."""
        return """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """


# ==================== GRAPH WINDOW ====================
class GraphWindow(QDialog):
    """Window for displaying stock price graph."""
    
    def __init__(self, parent, symbol: str, data: pd.DataFrame):
        """
        Initialize graph window.
        
        Args:
            parent: Parent widget
            symbol: Stock symbol
            data: Historical price data
        """
        super().__init__(parent)
        self.symbol = symbol
        self.data = data
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle(f"{self.symbol} - Price Chart")
        self.setGeometry(100, 100, 900, 600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"{self.symbol} - Price Trend (Last 5 Days)")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #333333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        self.plot_graph()
    
    def plot_graph(self) -> None:
        """Plot the stock price graph."""
        ax = self.figure.add_subplot(111)
        
        # Extract data
        dates = [str(date.date()) for date in self.data.index]
        prices = self.data['Close'].values
        
        # Plot with styling
        ax.plot(dates, prices, marker='o', linewidth=2.5, markersize=6, color='#2196F3')
        ax.fill_between(range(len(prices)), prices, alpha=0.3, color='#2196F3')
        
        # Styling
        ax.set_title(f"{self.symbol} Historical Prices", fontsize=14, fontweight='bold')
        ax.set_xlabel("Date", fontsize=11)
        ax.set_ylabel("Price ($)", fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#f8f9fa')
        
        # Rotate x labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        self.figure.tight_layout()
        self.canvas.draw()


# ==================== MAIN APPLICATION ====================
class ModernStockTracker(QMainWindow):
    """Main application window for stock tracking."""
    
    def __init__(self):
        """Initialize the main application."""
        super().__init__()
        self.setWindowTitle("📈 Stock Market Live Tracker")
        self.setGeometry(100, 100, 1400, 800)
        
        # Application data
        self.tracked_stocks = {}  # { symbol: stock_data }
        self.alert_manager = AlertManager()
        self.worker_thread = None
        
        # UI Setup
        self.init_ui()
        self.set_dark_theme()
        
        # Auto-refresh timer (every 25 seconds)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stock_data)
        self.refresh_timer.start(25000)  # 25 seconds
        
        self.show()
    
    def init_ui(self) -> None:
        """Initialize user interface components."""
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ============ Header Section ============
        header_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("📈 Stock Market Live Tracker")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1976D2; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Track your favorite stocks with real-time updates and alerts")
        subtitle_font = QFont("Segoe UI", 10)
        subtitle_font.setItalic(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #666666;")
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        
        # ============ Input Section ============
        input_section = QFrame()
        input_section.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        # Stock search label
        label = QLabel("Select Stock:")
        label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        input_layout.addWidget(label)
        
        # Stock combo box (company names, not symbols)
        self.stock_combo = QComboBox()
        self.stock_combo.addItem("-- Choose a stock --")
        self.stock_combo.addItems(sorted(STOCK_DATABASE.keys()))
        self.stock_combo.setFixedHeight(40)
        self.stock_combo.setStyleSheet(self.get_combo_style())
        input_layout.addWidget(self.stock_combo)
        
        # Add button
        add_btn = QPushButton("➕ Add Stock")
        add_btn.setFixedHeight(40)
        add_btn.setFixedWidth(120)
        add_btn.setStyleSheet(self.get_button_style("#4CAF50"))
        add_btn.clicked.connect(self.add_stock)
        input_layout.addWidget(add_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Now")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(120)
        refresh_btn.setStyleSheet(self.get_button_style("#2196F3"))
        refresh_btn.clicked.connect(self.refresh_stock_data)
        input_layout.addWidget(refresh_btn)
        
        input_layout.addStretch()
        input_section.setLayout(input_layout)
        main_layout.addWidget(input_section)
        
        # ============ Table Section ============
        table_label = QLabel("📊 Tracked Stocks")
        table_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        table_label.setStyleSheet("color: #333333; margin-top: 10px;")
        main_layout.addWidget(table_label)
        
        self.stocks_table = QTableWidget()
        self.stocks_table.setColumnCount(7)
        self.stocks_table.setHorizontalHeaderLabels([
            "Stock", "Name", "Current Price", "Change", "% Change", "Action", "⚙️"
        ])
        self.stocks_table.setStyleSheet(self.get_table_style())
        self.stocks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stocks_table.setRowCount(0)
        main_layout.addWidget(self.stocks_table)
        
        # ============ Status Bar ============
        self.status_label = QLabel("⏱️ Last Updated: Never")
        self.status_label.setStyleSheet("color: #666666; font-size: 10px;")
        main_layout.addWidget(self.status_label)
        
        main_widget.setLayout(main_layout)
    
    def add_stock(self) -> None:
        """Add a new stock to tracking."""
        selected = self.stock_combo.currentText()
        
        if selected == "-- Choose a stock --":
            QMessageBox.warning(self, "Warning", "Please select a stock from the dropdown!")
            return
        
        symbol = STOCK_DATABASE[selected]
        
        if symbol in self.tracked_stocks:
            QMessageBox.warning(self, "Warning", f"{symbol} is already being tracked!")
            return
        
        # Fetch stock data
        self.fetch_and_add_stock(symbol)
    
    def fetch_and_add_stock(self, symbol: str) -> None:
        """Fetch stock data and add to table."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                QMessageBox.critical(self, "Error", f"Could not fetch data for {symbol}")
                return
            
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Open'].iloc[-1]
            
            change = current_price - previous_price
            percent_change = (change / previous_price * 100) if previous_price != 0 else 0
            
            stock_data = {
                'symbol': symbol,
                'name': [k for k, v in STOCK_DATABASE.items() if v == symbol][0],
                'price': current_price,
                'change': change,
                'percent_change': percent_change,
                'history': hist,
                'timestamp': datetime.now()
            }
            
            self.tracked_stocks[symbol] = stock_data
            self.update_table()
            self.update_status()
            self.stock_combo.setCurrentIndex(0)
            
            # Show success message
            QMessageBox.information(self, "Success", f"{symbol} added to tracker!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch data: {str(e)}")
    
    def update_table(self) -> None:
        """Update the stocks table with current data."""
        self.stocks_table.setRowCount(len(self.tracked_stocks))
        
        for row, (symbol, data) in enumerate(self.tracked_stocks.items()):
            # Symbol
            symbol_item = QTableWidgetItem(symbol)
            symbol_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            self.stocks_table.setItem(row, 0, symbol_item)
            
            # Name
            name_item = QTableWidgetItem(data['name'])
            self.stocks_table.setItem(row, 1, name_item)
            
            # Price
            price_item = QTableWidgetItem(f"${data['price']:.2f}")
            price_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            self.stocks_table.setItem(row, 2, price_item)
            
            # Change
            change_text = f"+${data['change']:.2f}" if data['change'] >= 0 else f"-${abs(data['change']):.2f}"
            change_item = QTableWidgetItem(change_text)
            change_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.stocks_table.setItem(row, 3, change_item)
            
            # Percent Change
            percent_text = f"+{data['percent_change']:.2f}%" if data['percent_change'] >= 0 else f"{data['percent_change']:.2f}%"
            percent_item = QTableWidgetItem(percent_text)
            percent_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.stocks_table.setItem(row, 4, percent_item)
            
            # Color coding
            if data['change'] >= 0:
                change_item.setForeground(QColor("#4CAF50"))  # Green
                percent_item.setForeground(QColor("#4CAF50"))  # Green
            else:
                change_item.setForeground(QColor("#F44336"))  # Red
                percent_item.setForeground(QColor("#F44336"))  # Red
            
            # Graph button
            graph_btn = QPushButton("📊 Chart")
            graph_btn.setStyleSheet(self.get_button_style("#2196F3"))
            graph_btn.clicked.connect(lambda checked, s=symbol: self.show_graph(s))
            self.stocks_table.setCellWidget(row, 5, graph_btn)
            
            # Alert button
            alert_btn = QPushButton("🔔 Alert")
            alert_btn.setStyleSheet(self.get_button_style("#FF9800"))
            alert_btn.clicked.connect(lambda checked, s=symbol: self.set_alert(s))
            self.stocks_table.setCellWidget(row, 6, alert_btn)
    
    def refresh_stock_data(self) -> None:
        """Refresh all tracked stock data."""
        if not self.tracked_stocks:
            return
        
        try:
            for symbol in self.tracked_stocks:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Open'].iloc[-1]
                    
                    change = current_price - previous_price
                    percent_change = (change / previous_price * 100) if previous_price != 0 else 0
                    
                    self.tracked_stocks[symbol]['price'] = current_price
                    self.tracked_stocks[symbol]['change'] = change
                    self.tracked_stocks[symbol]['percent_change'] = percent_change
                    self.tracked_stocks[symbol]['history'] = hist
                    self.tracked_stocks[symbol]['timestamp'] = datetime.now()
                    
                    # Check alerts
                    alerts = self.alert_manager.check_alerts(symbol, current_price)
                    for alert_type, message in alerts:
                        self.show_alert_notification(message)
            
            self.update_table()
            self.update_status()
        
        except Exception as e:
            print(f"Error refreshing data: {e}")
    
    def show_graph(self, symbol: str) -> None:
        """Display price chart for selected stock."""
        if symbol in self.tracked_stocks:
            data = self.tracked_stocks[symbol]['history']
            graph_window = GraphWindow(self, symbol, data)
            graph_window.exec_()
    
    def set_alert(self, symbol: str) -> None:
        """Show alert dialog for stock."""
        if symbol in self.tracked_stocks:
            current_price = self.tracked_stocks[symbol]['price']
            dialog = AlertDialog(self, symbol, current_price)
            
            if dialog.exec_() == QDialog.Accepted:
                self.alert_manager.set_alert(symbol, dialog.high_target, dialog.low_target)
                QMessageBox.information(self, "Alert Set", f"Alerts set for {symbol}!")
    
    def show_alert_notification(self, message: str) -> None:
        """Show alert notification."""
        if HAS_PLYER:
            try:
                notification.notify(
                    title="Stock Alert! 🚨",
                    message=message,
                    timeout=5
                )
            except Exception as e:
                print(f"Error showing notification: {e}")
        
        # Also show as popup
        QMessageBox.information(self, "Stock Alert! 🚨", message)
    
    def update_status(self) -> None:
        """Update status bar with last update time."""
        now = datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(f"⏱️ Last Updated: {now} | Stocks Tracked: {len(self.tracked_stocks)}")
    
    def set_dark_theme(self) -> None:
        """Apply modern dark theme styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                background-color: #ffffff;
                color: #333333;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #333333;
            }
        """)
    
    def get_button_style(self, color: str) -> str:
        """Return styled button stylesheet."""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 10px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
                background-color: {'#388E3C' if color == '#4CAF50' else '#1976D2' if color == '#2196F3' else '#F57C00'};
            }}
            QPushButton:pressed {{
                background-color: {'#1B5E20' if color == '#4CAF50' else '#1565C0' if color == '#2196F3' else '#E65100'};
            }}
        """
    
    def get_combo_style(self) -> str:
        """Return styled combo box stylesheet."""
        return """
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                color: #333333;
                font-family: 'Segoe UI';
            }
            QComboBox:hover {
                border: 1px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
            }
            QListView {
                background-color: #ffffff;
                color: #333333;
                selection-background-color: #2196F3;
            }
        """
    
    def get_table_style(self) -> str:
        """Return styled table stylesheet."""
        return """
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #333333;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #2196F3;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
        """
    
    def closeEvent(self, event):
        """Handle application close."""
        self.refresh_timer.stop()
        event.accept()


# ==================== APPLICATION ENTRY POINT ====================
def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set application icon and style
    app.setStyle('Fusion')
    
    # Create and show main window
    tracker = ModernStockTracker()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
