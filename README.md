# QCryptoWidget

**QCryptoWidget** is a lightweight, customizable desktop widget for Windows that displays real-time cryptocurrency prices. It's designed to be simple, efficient, and always accessible on your desktop.

---

## 📦 Features

- **Real-Time Prices**: Tracks prices for user-selected coins (BTC, ETH, etc.)
- **Customizable Display**: Shows price changes over 24 hours or 7 days with colored up/down arrows
- **Movable UI**: Frameless, always-on-top window that you can place anywhere on your screen
- **Quick Info Links**: Click to open detailed CoinMarketCap page for any coin
- **Price Alarms**: Set custom price or % alerts with optional sound notifications
- **Portable**: All settings, coins, and alarms are stored locally – fully portable!

---

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### ✅ Prerequisites

- Python 3.8 or newer

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/qosai/QCryptoWidget.git
cd QCryptoWidget


--------------
2. Get a CoinMarketCap API Key
Go to CoinMarketCap API

Click “Get Your API Key Now” and sign up for a Basic (Free) plan

After logging in, copy your API key from the dashboard

3. Configure the Application
Open the .env file in your project folder

Paste your API key into .env file :
CMC_API_KEY="a1b2c3d4-e5f6-7890-1234-56789abcdef0"



🧪 Usage
Run from Source

Install dependencies:
  pip install -r requirements.txt

Run the application:
  python main.py




📦 Create a Standalone Executable (.exe)
You can bundle everything into a .exe for Windows.

1. Install PyInstaller:
pip install pyinstaller

2. Build the Executable
python -m PyInstaller --clean --name QCryptoWidget --onefile --windowed \
  --icon="assets/icon.ico" \
  --add-data "about.txt:." \
  --add-data ".env:." \
  --add-data "coins.json:." \
  --add-data "alarms.json:." \
  --add-data "assets:assets" \
  --hidden-import=PySide6.QtSvg \
  --hidden-import=PySide6.QtNetwork \
  main.py

3. Find Your App
The executable will be in the dist/ folder:
dist/QCryptoWidget.exe
You can run this file or create a desktop shortcut.

👤 Author
Qosai Samara

📝 License
This project is open source.
