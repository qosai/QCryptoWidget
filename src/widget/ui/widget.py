# QCryptoWidget/src/widget/ui/widget.py

import sys
import time
from pathlib import Path
from typing import Dict, List
import webbrowser # **CHANGE**: To open web links

from PySide6.QtCore import (Qt, QTimer, QUrl, QPoint)
from PySide6.QtGui import (QAction, QIcon)
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QSystemTrayIcon, QMenu, QInputDialog, QMessageBox,
    QDialog, QListWidget, QLineEdit, QFileDialog, QListWidgetItem, QStyle
)
# **CHANGE**: pyqtgraph is no longer needed for the UI
# import pyqtgraph as pg 

# Import project modules
from widget.config.config import load_config
from widget.data.coin_db import load_coins, save_coins, get_coin_db_path
from widget.data.alarm_db import load_alarms, save_alarms, get_alarm_db_path
from widget.api.coin_api import get_current_prices

# --- Constants ---
DARK_STYLESHEET = """
QWidget {
    background-color: #2E2E2E;
    color: #F0F0F0;
    font-family: Segoe UI;
}
QPushButton {
    background-color: #555555;
    border: 1px solid #777777;
    padding: 5px;
    border-radius: 3px;
}
QPushButton:hover {
    background-color: #666666;
}
QPushButton:pressed {
    background-color: #444444;
}
QPushButton#windowButton {
    background-color: transparent;
    border: none;
    font-size: 14px;
    font-weight: bold;
    max-width: 30px;
}
QPushButton#windowButton:hover {
    background-color: #666666;
}
QPushButton#closeButton:hover {
    background-color: #E81123;
}
QLineEdit, QComboBox, QListWidget {
    background-color: #444444;
    border: 1px solid #666666;
    padding: 4px;
    border-radius: 3px;
}
QDialog {
    background-color: #383838;
}
QLabel#coinCodeLabel {
    font-weight: bold;
    color: white;
}
"""

# **CHANGE**: ChartDialog class is no longer needed and has been removed.

# --- Alarm Dialog (Unchanged) ---
class AlarmDialog(QDialog):
    def __init__(self, alarms: List[Dict], coins: List[str], parent=None):
        super().__init__(parent)
        self.alarms = alarms
        self.coins = coins
        self.setWindowTitle("Alarm Settings")
        self.setMinimumWidth(500)
        self.setStyleSheet(DARK_STYLESHEET)
        self.init_ui()
        self.load_alarms_to_list()
    def init_ui(self):
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.populate_form_from_selection)
        layout.addWidget(QLabel("Existing Alarms:"))
        layout.addWidget(self.list_widget)
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Add/Edit Alarm:"))
        self.coin_combo = QComboBox()
        self.coin_combo.addItems(self.coins)
        form_layout.addWidget(self.coin_combo)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Price above", "Price below", "% increase (24h)", "% decrease (24h)"])
        form_layout.addWidget(self.type_combo)
        self.threshold_input = QLineEdit()
        self.threshold_input.setPlaceholderText("Enter numeric threshold (e.g., 65000 or 5 for %)")
        form_layout.addWidget(self.threshold_input)
        sound_layout = QHBoxLayout()
        self.sound_path_label = QLineEdit()
        self.sound_path_label.setPlaceholderText("Optional: Path to sound file (.wav)")
        self.sound_path_label.setReadOnly(True)
        sound_layout.addWidget(self.sound_path_label)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_sound_file)
        sound_layout.addWidget(browse_btn)
        form_layout.addLayout(sound_layout)
        layout.addLayout(form_layout)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add/Update")
        add_btn.clicked.connect(self.add_or_update_alarm)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_alarm)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)
        dialog_btns = QHBoxLayout()
        save_btn = QPushButton("Save & Close")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        dialog_btns.addWidget(save_btn)
        dialog_btns.addWidget(cancel_btn)
        layout.addLayout(dialog_btns)
    def load_alarms_to_list(self):
        self.list_widget.clear()
        for i, alarm in enumerate(self.alarms):
            text = f"{alarm['coin']} - {alarm['type']} {alarm['threshold']}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, i)
            self.list_widget.addItem(item)
    def populate_form_from_selection(self, item):
        index = item.data(Qt.UserRole)
        alarm = self.alarms[index]
        self.coin_combo.setCurrentText(alarm['coin'])
        self.type_combo.setCurrentText(alarm['type'])
        self.threshold_input.setText(str(alarm['threshold']))
        self.sound_path_label.setText(alarm.get('sound', ''))
    def browse_sound_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Sound File", "", "Sound Files (*.wav)")
        if filepath:
            self.sound_path_label.setText(filepath)
    def add_or_update_alarm(self):
        coin = self.coin_combo.currentText()
        alarm_type = self.type_combo.currentText()
        threshold_str = self.threshold_input.text()
        sound = self.sound_path_label.text()
        if not threshold_str:
            QMessageBox.warning(self, "Input Error", "Threshold cannot be empty.")
            return
        try:
            threshold = float(threshold_str)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Threshold must be a valid number.")
            return
        new_alarm = {"coin": coin, "type": alarm_type, "threshold": threshold, "sound": sound}
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            index = selected_items[0].data(Qt.UserRole)
            self.alarms[index] = new_alarm
        else:
            self.alarms.append(new_alarm)
        self.load_alarms_to_list()
        self.clear_form()
    def remove_alarm(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select an alarm to remove.")
            return
        indices_to_remove = sorted([item.data(Qt.UserRole) for item in selected_items], reverse=True)
        for index in indices_to_remove:
            del self.alarms[index]
        self.load_alarms_to_list()
        self.clear_form()
    def clear_form(self):
        self.list_widget.clearSelection()
        self.threshold_input.clear()
        self.sound_path_label.clear()
        if self.coin_combo.count() > 0: self.coin_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)

# --- Main Widget ---
class QCryptoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_pos = None
        try:
            self.config = load_config()
        except ValueError as e:
            QMessageBox.critical(self, "Configuration Error", str(e))
            sys.exit(1)

        self.root_path = self.config['root_path']
        self.coin_db_path = get_coin_db_path(self.root_path)
        self.alarm_db_path = get_alarm_db_path(self.root_path)
        
        self.coins = load_coins(self.coin_db_path)
        self.alarms = load_alarms(self.alarm_db_path)
        self.price_data: Dict[str, Dict] = {}
        # **ENHANCEMENT**: State for the selected change interval
        self.change_interval = '24h'
        
        self.init_ui()
        self.init_tray_icon()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_prices)
        self.set_update_interval()
        self.update_prices()

    def init_ui(self):
        self.setWindowTitle("QCryptoWidget")
        self.setMinimumWidth(350) # Increased width for new dropdown
        self.setStyleSheet(DARK_STYLESHEET)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.Tool)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 1, 1, 1)
        self.main_layout.setSpacing(5)

        title_bar_layout = QHBoxLayout()
        title_label = QLabel(" QCryptoWidget")
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        minimize_btn = QPushButton("—")
        minimize_btn.setObjectName("windowButton")
        minimize_btn.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(minimize_btn)
        close_btn = QPushButton("✕")
        close_btn.setObjectName("windowButton")
        close_btn.setProperty("id", "closeButton")
        close_btn.clicked.connect(self.hide)
        title_bar_layout.addWidget(close_btn)
        self.main_layout.addLayout(title_bar_layout)
        
        self.price_layout = QVBoxLayout()
        self.price_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.addLayout(self.price_layout)
        self.main_layout.addStretch()

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line)

        # Bottom controls layout
        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(10, 5, 10, 10)
        
        # Row 1: Refresh and Change Interval
        config_row_layout = QHBoxLayout()
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["5 min", "15 min", "1 hour"])
        self.interval_combo.currentTextChanged.connect(self.set_update_interval)
        config_row_layout.addWidget(QLabel("Refresh:"))
        config_row_layout.addWidget(self.interval_combo)

        # **ENHANCEMENT**: Add dropdown for change interval
        self.change_combo = QComboBox()
        self.change_combo.addItems(["Change (24h)", "Change (7d)"])
        self.change_combo.currentTextChanged.connect(self.on_change_interval_selected)
        config_row_layout.addStretch()
        config_row_layout.addWidget(self.change_combo)
        controls_layout.addLayout(config_row_layout)
        
        # Row 2: Action buttons
        button_row_layout = QHBoxLayout()
        add_btn = QPushButton("Add Coin (+)")
        add_btn.setToolTip("Add Coin")
        add_btn.clicked.connect(self.add_coin)
        button_row_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove (-)")
        remove_btn.setToolTip("Remove Coin")
        remove_btn.clicked.connect(self.remove_coin)
        button_row_layout.addWidget(remove_btn)

        # ADD THE NEW BUTTON "ABOUT" HERE
        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.show_about_dialog)
        button_row_layout.addWidget(about_btn)

        alarm_btn = QPushButton("Alarms")
        alarm_btn.clicked.connect(self.open_alarm_dialog)
        button_row_layout.addWidget(alarm_btn)
        controls_layout.addLayout(button_row_layout)

        self.main_layout.addLayout(controls_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        event.accept()

# In the QCryptoWidget class within src/widget/ui/widget.py

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)

        # **CHANGE**: Load the custom icon from the assets folder
        icon_path = self.root_path / "assets" / "icon.ico"

        if icon_path.exists():
            icon = QIcon(str(icon_path))
        else:
            print("Warning: Custom icon 'assets/icon.ico' not found. Using default system icon.")
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        
        self.tray_icon.setIcon(icon)

        # ... the rest of the method is unchanged ...
        show_action = QAction("Show/Hide Widget", self)
        quit_action = QAction("Exit", self)
        show_action.triggered.connect(self.toggle_visibility)
        quit_action.triggered.connect(self.quit_application)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.setToolTip("QCryptoWidget")

    def toggle_visibility(self):
        self.setVisible(not self.isVisible())
        
    def quit_application(self):
        save_coins(self.coin_db_path, self.coins)
        save_alarms(self.alarm_db_path, self.alarms)
        QApplication.quit()

    def update_price_display(self):
        while self.price_layout.count():
            item = self.price_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                layout = item.layout()
                while layout.count():
                    sub_item = layout.takeAt(0)
                    if sub_item.widget(): sub_item.widget().deleteLater()
        
        for coin in self.coins:
            if coin not in self.price_data: continue
            data = self.price_data[coin]
            price = data['price']
            
            # **ENHANCEMENT**: Get the correct percent change based on user selection
            percent_change = data.get(f'percent_change_{self.change_interval}', 0)
            
            arrow = "●"
            price_color = "#F0F0F0"
            if percent_change > 0:
                arrow = "▲"
                price_color = "#32CD32"
            elif percent_change < 0:
                arrow = "▼"
                price_color = "#FF4500"

            row_layout = QHBoxLayout()
            code_label = QLabel(coin)
            code_label.setObjectName("coinCodeLabel")
            
            price_str = f"{price:,.4f}"
            parts = price_str.split('.')
            integer_part = parts[0]
            fractional_part = ""
            if len(parts) > 1:
                fractional_part = f".{parts[1]}".rstrip('0').rstrip('.')

            arrow_label = QLabel(arrow)
            arrow_label.setStyleSheet(f"color: {price_color}; font-size: 12px; margin-right: 5px;")

            price_text_label = QLabel(f"<b>${integer_part}</b><i>{fractional_part}</i>")
            price_text_label.setTextFormat(Qt.TextFormat.RichText)
            
            # **CHANGE**: The button now opens a web URL
            chart_btn = QPushButton("Info")
            chart_btn.setFixedSize(60, 28)
            # Pass the coin's slug to the click handler
            chart_btn.clicked.connect(lambda checked, slug=data['slug']: self.open_coin_url(slug))
            
            row_layout.addWidget(code_label)
            row_layout.addStretch()
            row_layout.addWidget(arrow_label)
            row_layout.addWidget(price_text_label)
            row_layout.addStretch()
            row_layout.addWidget(chart_btn)
            
            self.price_layout.addLayout(row_layout)
        
        self.adjustSize()

    def update_prices(self):
        print(f"[{time.ctime()}] Fetching prices...")
        new_data = get_current_prices(self.coins, self.config['api_key'])
        if new_data is not None:
            self.price_data = new_data
            self.update_price_display()
            self.check_alarms()
        else:
            self.tray_icon.showMessage("API Error", "Could not fetch new prices.", QSystemTrayIcon.Warning)

    def on_change_interval_selected(self, text: str):
        """Handle selection from the 'Change' dropdown."""
        if "24h" in text:
            self.change_interval = '24h'
        elif "7d" in text:
            self.change_interval = '7d'
        # Redraw the UI with the new interval choice
        self.update_price_display()

    def set_update_interval(self):
        interval_text = self.interval_combo.currentText()
        if "min" in interval_text:
            minutes = int(interval_text.split()[0])
            self.timer.start(minutes * 60 * 1000)
        elif "hour" in interval_text:
            hours = int(interval_text.split()[0])
            self.timer.start(hours * 60 * 60 * 1000)

    def add_coin(self):
        text, ok = QInputDialog.getText(self, "Add Coin", "Enter 3-5 letter coin code (e.g., SOL):")
        if ok and text:
            code = text.upper()
            if not (3 <= len(code) <= 5):
                QMessageBox.warning(self, "Invalid Code", "Coin code must be 3-5 letters long.")
                return
            if code in self.coins:
                QMessageBox.warning(self, "Duplicate Coin", f"{code} is already in your list.")
                return
            self.coins.append(code)
            save_coins(self.coin_db_path, self.coins)
            self.update_prices()
    
    def remove_coin(self):
        text, ok = QInputDialog.getText(self, "Remove Coin", "Enter coin code to remove:")
        if ok and text:
            code = text.upper()
            if code not in self.coins:
                QMessageBox.warning(self, "Not Found", f"{code} is not in your list.")
                return
            self.coins.remove(code)
            self.price_data.pop(code, None)
            save_coins(self.coin_db_path, self.coins)
            self.update_price_display()
            self.alarms = [alarm for alarm in self.alarms if alarm['coin'] != code]
            save_alarms(self.alarm_db_path, self.alarms)

    def open_coin_url(self, slug: str):
        """Opens the CoinMarketCap page for the coin."""
        if not slug:
            QMessageBox.warning(self, "Error", "Could not determine the URL for this coin.")
            return
        url = f"https://coinmarketcap.com/currencies/{slug}/"
        webbrowser.open_new_tab(url)


    # ADD ABOUT - THIS ENTIRE METHOD
    def show_about_dialog(self):
        """Reads and displays the content of about.txt in an interactive message box."""
        about_file_path = self.root_path / "about.txt"
        try:
            with open(about_file_path, "r", encoding="utf-8") as f:
                about_content = f.read()
            
            # Create a message box instance for more control
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("About QCryptoWidget")
            msg_box.setTextFormat(Qt.RichText)  # Set text format to handle HTML
            msg_box.setText(about_content)
            msg_box.setIcon(QMessageBox.Information)
            # Make text selectable and links clickable
            msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction) 
            msg_box.exec()

        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "about.txt file not found.")
            

    def open_alarm_dialog(self):
        dialog = AlarmDialog(self.alarms.copy(), self.coins, self)
        if dialog.exec():
            self.alarms = dialog.alarms
            save_alarms(self.alarm_db_path, self.alarms)
            QMessageBox.information(self, "Success", "Alarms have been saved.")

    def check_alarms(self):
        for alarm in self.alarms:
            if alarm['coin'] not in self.price_data: continue
            price = self.price_data[alarm['coin']]['price']
            percent_change = self.price_data[alarm['coin']]['percent_change_24h']
            threshold = alarm['threshold']
            triggered = False
            if alarm['type'] == "Price above" and price > threshold: triggered = True
            elif alarm['type'] == "Price below" and price < threshold: triggered = True
            elif alarm['type'] == "% increase (24h)" and percent_change > threshold: triggered = True
            elif alarm['type'] == "% decrease (24h)" and percent_change < -abs(threshold): triggered = True
            if triggered: self.trigger_alarm_alert(alarm)
    
    def trigger_alarm_alert(self, alarm: Dict):
        message = f"Alarm for {alarm['coin']}: {alarm['type']} {alarm['threshold']}"
        print(f"ALARM TRIGGERED: {message}")
        self.tray_icon.showMessage("QCryptoWidget Alarm!", message, QSystemTrayIcon.Information, 5000)
        sound_path = alarm.get('sound')
        if sound_path and Path(sound_path).exists():
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(sound_path))
            effect.play()
            self.sound_effect = effect

    def closeEvent(self, event):
        event.ignore()
        self.hide()