# QCryptoWidget/main.py

import sys
from PySide6.QtWidgets import QApplication

# Correctly import the renamed class 'QCryptoWidget'
from widget.ui.widget import QCryptoWidget

def main():
    """
    The main entry point for the application.
    """
    app = QApplication(sys.argv)
    
    # Prevents the app from closing when the last window is hidden
    app.setQuitOnLastWindowClosed(False)

    # Instantiate the correct class name
    widget = QCryptoWidget()
    widget.show() # Initially show the widget
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()