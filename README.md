# 📈 Stock Market Live Tracker - Modern PyQt5 GUI Application

A **professional, modern desktop application** for real-time stock price tracking with a clean dashboard design, price alerts, interactive charts, and desktop notifications.

## ✨ Features

### Core Features
- **📊 Real-Time Stock Tracking** - Updates every 25 seconds automatically
- **💰 Live Price Data** - Current prices, price changes, and percentage changes
- **🎯 Price Alerts** - Get notified when stocks reach target prices
- **📉 Interactive Charts** - View 5-day price trends for each stock
- **🔔 Desktop Notifications** - Cross-platform alert notifications
- **🌐 Wide Stock Database** - 30+ major US stocks pre-loaded
- **💾 Alert Persistence** - Your alerts are saved locally

### UI/UX Features
- **Modern Dashboard Design** - Professional, clean interface
- **Color-Coded Data** - Green (📈 up) and Red (📉 down) indicators
- **Responsive Layout** - Works on different screen sizes
- **Search by Company Name** - No need to remember stock symbols!
- **One-Click Actions** - Quick access to charts and alerts
- **Status Bar** - Shows last update time and number of tracked stocks

## 🎯 Quick Start

### Prerequisites
- **Python 3.7+** installed on your system
- **Internet connection** (for fetching stock data)

### Installation (First Time Setup)

#### Step 1: Install Dependencies
Open PowerShell or Command Prompt in the STOCK_MARKET folder and run:

```bash
pip install -r requirements.txt
```

**Or manually:**
```bash
pip install yfinance pandas PyQt5 PyQt5-sip matplotlib plyer requests
```

#### Step 2: Run the Application
```bash
python modern_stock_tracker.py
```

The application window will open automatically! 🚀

## 📖 How to Use

### Adding Stocks

1. **Open Dropdown** - Click the "Select Stock:" dropdown menu
2. **Choose Company** - Search and select a company name (e.g., "Apple", "Tesla", "Microsoft")
   - No need to remember stock symbols!
3. **Click "Add Stock"** - The stock is added to your tracker
4. **View Data** - Stock info appears in the table below

### Viewing Stock Data

The table displays:
- **Stock** - Stock symbol (AAPL, TSLA, etc.)
- **Name** - Company full name
- **Current Price** - Latest stock price in USD
- **Change** - $ change since previous close
- **% Change** - Percentage change (colored: green/red)
- **Action Buttons**:
  - 📊 **Chart** - View 5-day price trend
  - 🔔 **Alert** - Set price alerts

### Setting Price Alerts

1. **Click 🔔 Alert Button** - Next to any stock
2. **Set Targets**:
   - **Above Target** - Alert when price goes UP to this value
   - **Below Target** - Alert when price goes DOWN to this value
3. **Click Save** - Alerts are now active and saved

### Viewing Charts

1. **Click 📊 Chart Button** - Next to any stock
2. **View Graph** - Shows 5-day price trend with markers
3. **Close Window** - Click X to return to main app

### Manual Refresh

- **Click 🔄 Refresh Now** - Immediately update all stock prices
- **Auto-Refresh** - Happens automatically every 25 seconds

## 📋 Available Stocks

The application includes these pre-loaded stocks:

**Technology:**
- Apple, Microsoft, Google, Amazon, Tesla, Meta, Nvidia, AMD, Intel, IBM, Cisco, Oracle

**Services:**
- Salesforce, Adobe, Netflix, Spotify, PayPal, Square, Shopify, Zoom, Uber, Airbnb

**Healthcare:**
- Moderna, Pfizer, Johnson & Johnson

**Consumer:**
- Coca-Cola, Pepsi, McDonald's, Nike, Walmart, Target

**Finance:**
- Bank of America, JPMorgan, Goldman Sachs, Morgan Stanley

**To add more stocks:** Edit the `STOCK_DATABASE` dictionary in `modern_stock_tracker.py`

## 🔧 Troubleshooting

### Application Won't Start
```bash
# Update pip first
python -m pip install --upgrade pip

# Install dependencies again
pip install -r requirements.txt

# Run with verbose output
python modern_stock_tracker.py
```

### No Data for Stock
- Check internet connection
- Verify stock symbol is correct
- Try adding a different stock to test
- Some stocks may not have data on weekends/holidays

### Alerts Not Working
- Desktop notifications require plyer: `pip install plyer`
- On Windows, ensure notifications are enabled in Settings
- Alerts still show as popup messages if plyer fails

### "ModuleNotFoundError" Errors
```bash
# Make sure you're in the STOCK_MARKET folder
# Then reinstall all dependencies
pip install -r requirements.txt --upgrade
```

## 📁 Project Structure

```
STOCK_MARKET/
├── modern_stock_tracker.py      # Main application (Modern PyQt5)
├── stock_tracker.py             # Legacy Tkinter version (optional)
├── stocks_watchlist.json        # Your saved watchlist
├── stock_alerts.json            # Your saved alerts
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── QUICKSTART.md               # Quick start guide
└── .venv/                      # Virtual environment (optional)
```

## 🎨 UI Customization

### Change Update Frequency

Edit `modern_stock_tracker.py`, find this line:
```python
self.refresh_timer.start(25000)  # 25 seconds
```

Change `25000` to desired milliseconds:
- 10 seconds = `10000`
- 30 seconds = `30000`
- 60 seconds = `60000`

### Add More Stocks

Edit `STOCK_DATABASE` dictionary in `modern_stock_tracker.py`:
```python
STOCK_DATABASE = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    # Add new entries like:
    "New Company": "SYMBOL",
}
```

### Change Color Theme

Edit color values in this section:
```python
# Current colors:
POSITIVE_COLOR = "#4CAF50"  # Green
NEGATIVE_COLOR = "#F44336"  # Red
PRIMARY_COLOR = "#2196F3"   # Blue
```

## 🚀 Advanced Usage

### Data Storage

- **Alerts**: Saved in `stock_alerts.json`
- **Watchlist**: Can be saved to `stocks_watchlist.json`

### Running Without Python

To create a standalone executable:
```bash
pip install pyinstaller
pyinstaller --onefile modern_stock_tracker.py
```

Executable will be in `dist/` folder.

## 📊 Data Sources

- **Stock Prices**: Yahoo Finance (via yfinance)
- **Historical Data**: 5-day historical prices for charts
- **Updates**: Real-time during market hours

## 🔐 Disclaimer

This application is for **educational and informational purposes only**. It is not financial advice. Always do your own research before making investment decisions.

## 📝 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Found a bug or want to suggest a feature? Feel free to modify and improve the code!

## 📧 Support

For issues:
1. Check the **Troubleshooting** section
2. Verify all dependencies are installed
3. Check your internet connection
4. Restart the application

## 🎓 Learning Resources

If you want to understand the code:

1. **PyQt5 Basics** - Check `init_ui()` method
2. **Data Fetching** - See `fetch_and_add_stock()` method
3. **Alerts** - Review `AlertManager` class
4. **Charts** - Check `GraphWindow` class
5. **UI Styling** - See `get_*_style()` methods

## 📈 Version History

- **v2.0** (2026) - Modern PyQt5 GUI with graphs and alerts
- **v1.0** - Legacy Tkinter version

---

**Made with ❤️ for stock tracking enthusiasts**

**Last Updated:** April 2026

### Setting Alert Targets
1. Right-click on a stock in the table
2. Select "Set Alert Targets"
3. Enter a High Target (alert when price goes ABOVE this) and/or Low Target (alert when price goes BELOW this)
4. Click "Save"

### Viewing Alert Targets
1. Right-click on a stock
2. Select "View Targets" to see your current targets

### Removing Stocks
1. Click on a stock in the table to select it
2. Click "Remove Selected" or right-click and choose "Remove Stock"

### Auto-Refresh
Stock data automatically updates every 30 seconds. You'll see the price, change ($), and change (%) update in the table.

When a stock price crosses your alert target, a popup notification will appear.

## Example Usage

```
1. Add AAPL (Apple Inc.)
   - See current price, e.g., $185.50
   - See if it's up (green) or down (red)

2. Set Alert Targets for AAPL
   - High Target: $190.00 (alert me if price goes above $190)
   - Low Target: $180.00 (alert me if price drops below $180)

3. Wait 30 seconds (auto-refresh happens)
   - If price crosses $190 or $180, you'll get a popup alert

4. Close the app
   - Your watchlist is saved automatically
   - Next time you open, your stocks and targets are still there
```

## Color Indicators

- 🟢 **Green** - Stock price went UP since last refresh
- 🔴 **Red** - Stock price went DOWN since last refresh

## File Structure

```
STOCK_MARKET/
├── stock_tracker.py          # Main application code
├── requirements.txt          # Python packages to install
├── stocks_watchlist.json     # Your saved watchlist (auto-created)
└── README.md                 # This file
```

## Troubleshooting

### "Module not found: yfinance"
Install the required packages:
```bash
pip install -r requirements.txt
```

### "Invalid symbol" error
Make sure the stock symbol is correct. Examples:
- Apple: AAPL
- Tesla: TSLA
- Microsoft: MSFT
- Google: GOOGL
- Amazon: AMZN
- Meta: META

### Data not updating
Check your internet connection. The app fetches data every 30 seconds. If API is down, it will retry on next cycle.

### GUI freezes
If the GUI freezes during API calls, that's a bug! The app uses threading to prevent this. If it happens, restart the app.

## Code Structure (for learning)

**Classes:**
- `StockData` - Fetches stock prices from yfinance
- `AlertManager` - Manages price targets and alerts
- `StockTracker` - Main GUI application

**Key Functions:**
- `add_stock()` - Add a stock to the watchlist
- `background_update_worker()` - Thread that fetches data every 30 seconds
- `check_queue()` - Listen for updates from background thread
- `set_alert_targets()` - User sets price targets
- `save_watchlist()` / `load_watchlist()` - JSON persistence

## Future Enhancements (Bonus Ideas)

- Add price history graph using matplotlib
- Export data to CSV
- More alert options (e.g., percentage change alerts)
- Sound notifications
- Dark mode theme
- Multiple watchlists

## Legal Notice

This app uses yfinance to fetch data from Yahoo! Finance. It's for personal use and educational purposes only. See [yfinance license](https://github.com/ranaroussi/yfinance) for details.

## License

This project is open-source and free to use.

## Author

Created for stock market learners and enthusiasts!

---

**Enjoy tracking your stocks! 📈**
