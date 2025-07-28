# QCryptoWidget/main.py
import sys
from PySide6.QtWidgets import QApplication

# This import will now work because of Step 2
from widget.ui.widget import QCryptoWidget

def main():
    """
    The main entry point for the application.
    """
    app = QApplication(sys.argv)
    
    # Prevents the app from closing when the last window is hidden
    app.setQuitOnLastWindowClosed(False)

    widget = QCryptoWidget()
    widget.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()