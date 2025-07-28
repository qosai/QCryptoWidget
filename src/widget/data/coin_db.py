# QCryptoWidget/src/widget/data/coin_db.py

import json
import os
from pathlib import Path

COIN_FILE = "coins.json"

def get_coin_db_path(root_path: Path) -> Path:
    """Returns the full path to the coin database file."""
    return root_path / COIN_FILE

def load_coins(db_path: Path) -> list:
    """
    Loads the list of coin codes from the JSON file.

    Args:
        db_path (Path): The path to the coin database file.

    Returns:
        list: A list of coin codes (e.g., ['BTC', 'ETH']).
              Returns a default list if the file doesn't exist.
    """
    if not db_path.exists():
        return ["BTC", "ETH", "ADA", "BNB"]  # Default coins
    try:
        with open(db_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return ["BTC", "ETH", "ADA", "BNB"] # Return default on error

def save_coins(db_path: Path, coins: list):
    """
    Saves the list of coin codes to the JSON file.

    Args:
        db_path (Path): The path to the coin database file.
        coins (list): The list of coin codes to save.
    """
    try:
        with open(db_path, 'w') as f:
            json.dump(coins, f, indent=4)
    except IOError as e:
        print(f"Error saving coin list: {e}")