"""
Stock Market Tracker - Desktop GUI Application using Tkinter
Features:
- Real-time stock price tracking
- Price alerts (above/below target)
- Auto-refresh every 30 seconds
- Visual indicators (green/red)
- Local JSON storage for watchlist

Author: Stock Tracker App
Date: 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import queue
import json
import os
from datetime import datetime
import yfinance as yf
from typing import Dict, Optional, Tuple


class StockData:
    """Handles fetching and processing stock data from yfinance."""
    
    @staticmethod
    def fetch_stock_data(symbol: str) -> Optional[Dict]:
        """
        Fetch current stock price and calculate change.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dict with keys: price, change, percent_change, timestamp
            None if fetch fails
        """
        try:
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Get historical data (last 2 days to calculate change)
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
            
            # Get current price (most recent)
            current_price = hist['Close'].iloc[-1]
            
            # Get previous close
            if len(hist) > 1:
                previous_price = hist['Close'].iloc[-2]
            else:
                # If only 1 day available, use opening price
                previous_price = hist['Open'].iloc[-1]
            
            # Calculate change
            change = current_price - previous_price
            percent_change = (change / previous_price * 100) if previous_price != 0 else 0
            
            return {
                'symbol': symbol.upper(),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'percent_change': round(percent_change, 2),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'is_up': change >= 0
            }
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None


class AlertManager:
    """Manages price alerts for each stock."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.alerts = {}  # { symbol: { 'high': target, 'low': target, 'high_alerted': bool, 'low_alerted': bool } }
    
    def set_target(self, symbol: str, high_target: Optional[float], low_target: Optional[float]) -> None:
        """
        Set upper and lower target prices for a stock.
        
        Args:
            symbol: Stock ticker symbol
            high_target: Alert when price goes above this
            low_target: Alert when price goes below this
        """
        symbol = symbol.upper()
        self.alerts[symbol] = {
            'high': high_target,
            'low': low_target,
            'high_alerted': False,
            'low_alerted': False
        }
    
    def get_target(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        """Get target prices for a stock."""
        symbol = symbol.upper()
        if symbol in self.alerts:
            return self.alerts[symbol]['high'], self.alerts[symbol]['low']
        return None, None
    
    def check_alerts(self, symbol: str, current_price: float) -> Optional[str]:
        """
        Check if price crossed any target threshold.
        
        Args:
            symbol: Stock ticker symbol
            current_price: Current stock price
            
        Returns:
            Alert message if triggered, None otherwise
        """
        symbol = symbol.upper()
        if symbol not in self.alerts:
            return None
        
        alert_data = self.alerts[symbol]
        alert_msg = None
        
        # Check high target
        if alert_data['high'] is not None:
            if current_price > alert_data['high'] and not alert_data['high_alerted']:
                alert_msg = f"{symbol}: Price ${current_price} is ABOVE target ${alert_data['high']}!"
                alert_data['high_alerted'] = True
                alert_data['low_alerted'] = False  # Reset low alert when price goes up
            elif current_price <= alert_data['high']:
                alert_data['high_alerted'] = False
        
        # Check low target
        if alert_data['low'] is not None:
            if current_price < alert_data['low'] and not alert_data['low_alerted']:
                alert_msg = f"{symbol}: Price ${current_price} is BELOW target ${alert_data['low']}!"
                alert_data['low_alerted'] = True
                alert_data['high_alerted'] = False  # Reset high alert when price goes down
            elif current_price >= alert_data['low']:
                alert_data['low_alerted'] = False
        
        return alert_msg
    
    def remove_stock(self, symbol: str) -> None:
        """Remove a stock from alerts."""
        symbol = symbol.upper()
        if symbol in self.alerts:
            del self.alerts[symbol]


class StockTracker:
    """Main GUI application for stock tracking."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Stock Market Tracker")
        self.root.geometry("900x500")
        self.root.resizable(True, True)
        
        # Initialize data structures
        self.alert_manager = AlertManager()
        self.stocks = {}  # { symbol: { price, change, etc } }
        self.watchlist_file = "stocks_watchlist.json"
        
        # Threading components
        self.update_queue = queue.Queue()
        self.running = True
        self.fetch_thread = None
        
        # Create GUI
        self.setup_ui()
        
        # Load previous watchlist
        self.load_watchlist()
        
        # Start background update thread
        self.start_background_update()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_ui(self) -> None:
        """Set up the user interface."""
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # ===== TOP FRAME: Input Section =====
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        # Label
        ttk.Label(top_frame, text="Stock Symbol:").pack(side=tk.LEFT, padx=5)
        
        # Entry field
        self.symbol_entry = ttk.Entry(top_frame, width=15)
        self.symbol_entry.pack(side=tk.LEFT, padx=5)
        self.symbol_entry.bind('<Return>', lambda e: self.add_stock())
        
        # Add button
        add_btn = ttk.Button(top_frame, text="Add Stock", command=self.add_stock)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Remove button
        remove_btn = ttk.Button(top_frame, text="Remove Selected", command=self.remove_stock)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # ===== MIDDLE FRAME: Table =====
        middle_frame = ttk.Frame(self.root, padding="10")
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        columns = ('Symbol', 'Price', 'Change', '% Change', 'High Target', 'Low Target', 'Status')
        self.tree = ttk.Treeview(middle_frame, columns=columns, height=15, show='headings')
        
        # Define column headings
        headings = {
            'Symbol': 'Symbol',
            'Price': 'Current Price',
            'Change': 'Change ($)',
            '% Change': 'Change (%)',
            'High Target': 'High Target',
            'Low Target': 'Low Target',
            'Status': 'Status'
        }
        
        # Configure columns
        column_widths = {
            'Symbol': 80,
            'Price': 100,
            'Change': 100,
            '% Change': 100,
            'High Target': 100,
            'Low Target': 100,
            'Status': 80
        }
        
        for col, heading in headings.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=column_widths[col], anchor=tk.CENTER)
        
        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(middle_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(middle_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        
        # Configure tags for colors
        self.tree.tag_configure('up', foreground='green', font=('Arial', 10, 'bold'))
        self.tree.tag_configure('down', foreground='red', font=('Arial', 10, 'bold'))
        self.tree.tag_configure('neutral', foreground='black')
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        middle_frame.grid_rowconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(0, weight=1)
        
        # Bind right-click for context menu
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        # ===== BOTTOM FRAME: Status =====
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(bottom_frame, text="Status: Initializing...", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X)
    
    def add_stock(self) -> None:
        """Add a new stock to the watchlist."""
        symbol = self.symbol_entry.get().strip().upper()
        
        if not symbol:
            messagebox.showwarning("Input Error", "Please enter a stock symbol")
            return
        
        if symbol in self.stocks:
            messagebox.showinfo("Duplicate", f"{symbol} is already being tracked")
            return
        
        # Fetch stock data
        data = StockData.fetch_stock_data(symbol)
        
        if data is None:
            messagebox.showerror("Error", f"Could not fetch data for {symbol}.\nPlease check the symbol and try again.")
            return
        
        # Add to stocks dictionary
        self.stocks[symbol] = data
        
        # Add row to tree
        tag = 'up' if data['is_up'] else 'down'
        self.tree.insert('', 'end', iid=symbol, values=(
            symbol,
            f"${data['price']}",
            f"${data['change']}",
            f"{data['percent_change']}%",
            "-",
            "-",
            "OK"
        ), tags=(tag,))
        
        # Clear entry
        self.symbol_entry.delete(0, tk.END)
        
        # Save watchlist
        self.save_watchlist()
        
        messagebox.showinfo("Success", f"Added {symbol} to watchlist")
    
    def remove_stock(self) -> None:
        """Remove selected stock from watchlist."""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a stock to remove")
            return
        
        symbol = selected[0]
        self.tree.delete(symbol)
        del self.stocks[symbol]
        self.alert_manager.remove_stock(symbol)
        
        # Save watchlist
        self.save_watchlist()
        
        messagebox.showinfo("Success", f"Removed {symbol} from watchlist")
    
    def show_context_menu(self, event) -> None:
        """Show right-click context menu."""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        self.tree.selection_set(item)
        
        # Create context menu
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Set Alert Targets", command=lambda: self.set_alert_targets(item))
        menu.add_command(label="View Targets", command=lambda: self.view_targets(item))
        menu.add_command(label="Remove Stock", command=self.remove_stock)
        
        menu.tk_popup(event.x_root, event.y_root)
    
    def on_tree_click(self, event) -> None:
        """Handle tree click."""
        pass
    
    def set_alert_targets(self, symbol: str) -> None:
        """Set alert targets for a stock."""
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Set Targets for {symbol}")
        popup.geometry("300x200")
        popup.transient(self.root)
        
        # High target
        ttk.Label(popup, text="High Target ($):").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        high_entry = ttk.Entry(popup, width=15)
        high_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Low target
        ttk.Label(popup, text="Low Target ($):").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        low_entry = ttk.Entry(popup, width=15)
        low_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Get existing targets
        high, low = self.alert_manager.get_target(symbol)
        if high:
            high_entry.insert(0, str(high))
        if low:
            low_entry.insert(0, str(low))
        
        def save_targets():
            try:
                high_val = float(high_entry.get()) if high_entry.get() else None
                low_val = float(low_entry.get()) if low_entry.get() else None
                
                if high_val is None and low_val is None:
                    messagebox.showwarning("Input Error", "Enter at least one target price")
                    return
                
                if high_val and low_val and high_val <= low_val:
                    messagebox.showwarning("Input Error", "High target must be greater than low target")
                    return
                
                self.alert_manager.set_target(symbol, high_val, low_val)
                self.save_watchlist()
                messagebox.showinfo("Success", f"Targets set for {symbol}")
                popup.destroy()
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers")
        
        ttk.Button(popup, text="Save", command=save_targets).grid(row=2, column=0, columnspan=2, pady=20)
    
    def view_targets(self, symbol: str) -> None:
        """View current alert targets for a stock."""
        high, low = self.alert_manager.get_target(symbol)
        
        msg = f"Alert Targets for {symbol}:\n\n"
        msg += f"High Target: ${high if high else 'Not set'}\n"
        msg += f"Low Target: ${low if low else 'Not set'}"
        
        messagebox.showinfo("Target Prices", msg)
    
    def start_background_update(self) -> None:
        """Start the background update thread."""
        self.fetch_thread = threading.Thread(target=self.background_update_worker, daemon=True)
        self.fetch_thread.start()
        
        # Start listening to queue
        self.check_queue()
    
    def background_update_worker(self) -> None:
        """Background thread that fetches stock data every 30 seconds."""
        import time
        
        while self.running:
            try:
                for symbol in list(self.stocks.keys()):
                    if not self.running:
                        break
                    
                    data = StockData.fetch_stock_data(symbol)
                    if data:
                        self.update_queue.put(('update', symbol, data))
                    else:
                        self.update_queue.put(('error', symbol, None))
                
                self.update_queue.put(('status', 'Updated at ' + datetime.now().strftime('%H:%M:%S'), None))
                
                # Wait 30 seconds before next update
                time.sleep(30)
            except Exception as e:
                print(f"Background update error: {e}")
                time.sleep(30)
    
    def check_queue(self) -> None:
        """Check for updates from background thread."""
        try:
            while True:
                msg_type, param1, param2 = self.update_queue.get_nowait()
                
                if msg_type == 'update':
                    symbol, data = param1, param2
                    self.handle_stock_update(symbol, data)
                elif msg_type == 'error':
                    symbol = param1
                    self.handle_stock_error(symbol)
                elif msg_type == 'status':
                    self.status_label.config(text=f"Status: {param1}")
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(200, self.check_queue)
    
    def handle_stock_update(self, symbol: str, data: Dict) -> None:
        """Handle stock data update from background thread."""
        self.stocks[symbol] = data
        
        # Check for alerts
        alert_msg = self.alert_manager.check_alerts(symbol, data['price'])
        if alert_msg:
            messagebox.showwarning("Price Alert!", alert_msg)
        
        # Update tree
        if symbol in self.tree.get_children():
            tag = 'up' if data['is_up'] else 'down'
            high, low = self.alert_manager.get_target(symbol)
            
            self.tree.item(symbol, values=(
                symbol,
                f"${data['price']}",
                f"${data['change']}",
                f"{data['percent_change']}%",
                f"${high}" if high else "-",
                f"${low}" if low else "-",
                "OK"
            ), tags=(tag,))
    
    def handle_stock_error(self, symbol: str) -> None:
        """Handle error fetching stock data."""
        if symbol in self.tree.get_children():
            self.tree.item(symbol, values=(
                symbol,
                "ERROR",
                "-",
                "-",
                "-",
                "-",
                "FAILED"
            ), tags=('down',))
    
    def save_watchlist(self) -> None:
        """Save watchlist and alert targets to JSON file."""
        data_to_save = {
            'stocks': list(self.stocks.keys()),
            'alerts': {}
        }
        
        # Save alert targets
        for symbol, alert_data in self.alert_manager.alerts.items():
            data_to_save['alerts'][symbol] = {
                'high': alert_data['high'],
                'low': alert_data['low']
            }
        
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        except Exception as e:
            print(f"Error saving watchlist: {e}")
    
    def load_watchlist(self) -> None:
        """Load watchlist and alert targets from JSON file."""
        if not os.path.exists(self.watchlist_file):
            return
        
        try:
            with open(self.watchlist_file, 'r') as f:
                data = json.load(f)
            
            # Load previous stocks
            for symbol in data.get('stocks', []):
                self.stocks[symbol] = {'price': 0}  # Placeholder
                self.tree.insert('', 'end', iid=symbol, values=(
                    symbol,
                    "Loading...",
                    "-",
                    "-",
                    "-",
                    "-",
                    "Loading..."
                ), tags=('neutral',))
            
            # Load alert targets
            for symbol, alert_data in data.get('alerts', {}).items():
                high = alert_data.get('high')
                low = alert_data.get('low')
                self.alert_manager.set_target(symbol, high, low)
        except Exception as e:
            print(f"Error loading watchlist: {e}")
    
    def on_close(self) -> None:
        """Handle window close event."""
        self.running = False
        if self.fetch_thread:
            self.fetch_thread.join(timeout=2)
        self.root.destroy()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = StockTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
