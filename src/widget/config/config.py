# QCryptoWidget/src/widget/config/config.py

import os
from dotenv import load_dotenv
from pathlib import Path
import sys

def get_project_root() -> Path:
    """
    Finds the project root for both development and a packaged .exe file.
    """
    # Check if the application is running as a bundled executable
    if getattr(sys, 'frozen', False):
        # If so, the root is the directory of the executable
        return Path(sys.executable).parent
    else:
        # Otherwise (running from .py source), find the root by looking for .env
        current_path = Path.cwd()
        if (current_path / ".env").exists():
            return current_path
        for parent in Path(__file__).resolve().parents:
            if (parent / ".env").exists():
                return parent
    
    # Fallback if no path is found
    print("Error: Could not determine the project root directory.", file=sys.stderr)
    sys.exit(1)


def load_config():
    """
    Loads configuration from the .env file located in the project root.

    Returns:
        dict: A dictionary containing configuration values.
    """
    root_path = get_project_root()
    load_dotenv(dotenv_path=root_path / ".env")

    api_key = os.getenv("CMC_API_KEY")
    interval_str = os.getenv("DEFAULT_REFRESH_INTERVAL", "5")

    if not api_key or "YOUR_COINMARKETCAP_API_KEY_HERE" in api_key:
        raise ValueError("CMC_API_KEY is not set or is invalid. Please update your .env file.")

    try:
        interval = int(interval_str)
    except (ValueError, TypeError):
        print("Warning: Invalid DEFAULT_REFRESH_INTERVAL. Using default value of 5 minutes.", file=sys.stderr)
        interval = 5

    return {
        "api_key": api_key,
        "refresh_interval": interval,
        "root_path": root_path
    }