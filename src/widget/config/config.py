# QCryptoWidget/src/widget/config/config.py

import os
from dotenv import load_dotenv
from pathlib import Path
import sys

def get_project_root() -> Path:
    """Finds the project root by looking for the .env file."""
    # This is robust enough to work in both development and when installed.
    # In development, it finds the .env file in the project root.
    # When installed via setup.py, scripts might be elsewhere, so we search up.
    current_path = Path.cwd()
    if (current_path / ".env").exists():
        return current_path
    # Check parent directories if running from a different location
    for parent in Path(__file__).resolve().parents:
        if (parent / ".env").exists():
            return parent
    # Fallback if .env is not found
    print("Error: .env file not found. Please ensure it is in the project root.", file=sys.stderr)
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