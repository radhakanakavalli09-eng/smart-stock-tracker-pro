# 🛠️ Detailed Installation Guide - Windows

Complete step-by-step guide for installing and running the Stock Market Live Tracker on Windows.

---

## ✅ Prerequisites Check

Before starting, verify you have:
- ✅ **Windows 7 / 8 / 10 / 11** (any version)
- ✅ **Python 3.7+** installed
- ✅ **Internet connection** (for stock data)

### Check Python Installation

Open **PowerShell** or **Command Prompt** and type:
```bash
python --version
```

**Expected output:** `Python 3.x.x` (at least 3.7)

❌ **Not installed?** Download from https://www.python.org/downloads/
- ✅ Make sure to **check "Add Python to PATH"** during installation
- ✅ Then restart your computer

---

## 📥 Step 1: Prepare Your Folder

1. **Navigate to your project folder:**
   - Open File Explorer
   - Go to: `C:\Users\[YourName]\OneDrive\Desktop\STOCK_MARKET`
   - Or wherever you saved the project

2. **Copy Path** (you'll need it):
   - Click on the folder path bar
   - Select all and copy (Ctrl+C)

---

## 📦 Step 2: Install Python Packages

### Method 1: Automatic (Recommended)

1. **Open PowerShell in the folder:**
   - In File Explorer, click on the address bar
   - Type: `powershell`
   - Press Enter

2. **Run this command:**
   ```bash
   pip install -r requirements.txt
   ```

   **Wait for completion** ⏳ (2-3 minutes typically)

3. **You should see:**
   ```
   Successfully installed yfinance pandas PyQt5 matplotlib plyer ...
   ```

### Method 2: Manual Installation

If the automatic method doesn't work:

```bash
pip install yfinance
pip install pandas
pip install PyQt5
pip install PyQt5-sip
pip install matplotlib
pip install plyer
```

### Verify Installation

Test that all packages were installed:
```bash
python -c "import PyQt5; import yfinance; import pandas; print('✅ All packages installed!')"
```

✅ **Should print:** `✅ All packages installed!`

---

## 🚀 Step 3: Launch the Application

### Quick Start

In PowerShell (in your project folder), type:
```bash
python modern_stock_tracker.py
```

**Wait 2-3 seconds...** the app window should open! 🎉

### Alternative: Create a Shortcut

**To launch from anywhere:**

1. **Create a batch file** (.bat):
   - Right-click in your STOCK_MARKET folder
   - New → Text Document
   - Name it: `run.bat`
   - Open it and paste:
     ```batch
     @echo off
     cd /d "%~dp0"
     python modern_stock_tracker.py
     pause
     ```
   - Save and close

2. **Double-click `run.bat`** to launch the app anytime!

---

## 🎯 Step 4: First Use

1. ✅ Select a stock from the dropdown (e.g., "Apple")
2. ✅ Click "➕ Add Stock"
3. ✅ Watch the data appear in the table
4. ✅ Click "📊 Chart" to see price trends
5. ✅ Click "🔔 Alert" to set price alerts

---

## ⚠️ Troubleshooting

### Issue: "ModuleNotFoundError"

**Error looks like:**
```
ModuleNotFoundError: No module named 'PyQt5'
```

**Solution:**
```bash
# Reinstall packages
pip install --upgrade PyQt5 yfinance pandas matplotlib

# If still broken, use:
pip install --force-reinstall -r requirements.txt
```

---

### Issue: "python: The term 'python' is not recognized"

**This means Python isn't in your PATH**

**Solution:**
1. **Test with full path:**
   ```bash
   python.exe modern_stock_tracker.py
   ```

2. **Or reinstall Python:**
   - Go to https://www.python.org/downloads/
   - Download Python 3.11 (latest)
   - **IMPORTANT:** Check ✅ "Add Python to PATH" during setup
   - Click "Install Now"
   - Restart PowerShell
   - Try again

---

### Issue: App Opens but No Data Shows

**Possible causes:**
- ❌ No internet connection - fix: check WiFi/ethernet
- ❌ Stock doesn't exist - fix: try "Apple" or "Microsoft"
- ❌ Market is closed - fix: works during US market hours (9:30 AM - 4:00 PM EST)

**Solution:**
1. Check internet: Open browser, visit google.com
2. Try a different stock
3. Wait for market hours
4. Restart the app

---

### Issue: Notifications/Alerts Don't Work

**Expected behavior:**
- ✅ Alert popup ALWAYS appears
- ⚠️ Desktop notifications might not show

**Solution:**
1. **Enable Windows Notifications:**
   - Settings → System → Notifications & actions
   - Make sure "Show notifications" is ON

2. **Check notification settings:**
   - Settings → Privacy & Security → Notifications
   - Allow Python notifications

3. Popups will still work even if desktop notifications fail!

---

### Issue: Very Slow / Freezing

**Solution:**
1. Update packages:
   ```bash
   pip install --upgrade PyQt5 yfinance
   ```

2. Reduce update frequency in code:
   - Open `modern_stock_tracker.py`
   - Find: `self.refresh_timer.start(25000)`
   - Change to: `self.refresh_timer.start(60000)` (60 seconds)

---

## 🎨 Customization

### Change Update Speed

**Edit `modern_stock_tracker.py`**

Find this line (around line 505):
```python
self.refresh_timer.start(25000)  # 25 seconds
```

Change `25000`:
- 10 seconds: `10000`
- 30 seconds: `30000`
- 60 seconds: `60000`
- 2 minutes: `120000`

### Add More Stocks

**Edit the stock database:**

Find `STOCK_DATABASE` (around line 30):
```python
STOCK_DATABASE = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    # Add here:
    "My Company": "SYMBOL",
}
```

For symbols, visit https://finance.yahoo.com/ and search for the stock.

---

## 🔧 Advanced Setup (Optional)

### Create Virtual Environment (Best Practice)

For experienced users wanting isolated dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Run app
python modern_stock_tracker.py

# Deactivate when done
deactivate
```

### Build Standalone Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed modern_stock_tracker.py
```

Find executable in `dist/` folder!

---

## ✨ Tips & Tricks

### 1. Keep App Running
- Minimize to system tray
- Alerts still trigger!
- Auto-updates continue

### 2. Monitor Multiple Stocks
- Add unlimited stocks
- All update simultaneously
- Great for portfolio tracking

### 3. Use Charts
- Click "📊 Chart"
- See 5-day trend
- Spot patterns

### 4. Set Smart Alerts
- Set high alert 10% above current
- Set low alert 10% below current
- Get notified of big moves

### 5. Save Alerts
- Alerts save automatically
- Restart app, they persist
- Edit anytime via "🔔 Alert" button

---

## 📞 Need Help?

### Common Fixes (In Order)

1. **Restart the app** ↻
2. **Check internet** 🌐
3. **Reinstall packages** 📦
   ```bash
   pip install --upgrade -r requirements.txt
   ```
4. **Restart computer** 💻
5. **Reinstall Python** 🐍

---

## 📚 Resources

- **Python Docs:** https://python.org/docs
- **PyQt5 Guide:** https://doc.qt.io/qtforpython/
- **yfinance:** https://github.com/ranaroussi/yfinance
- **Yahoo Finance:** https://finance.yahoo.com/

---

## 🎉 You're All Set!

Everything should be working now. Launch with:

```bash
python modern_stock_tracker.py
```

**Enjoy tracking your stocks!** 📈

---

**Last Updated:** April 2026
**Version:** 2.0 (Modern PyQt5)
