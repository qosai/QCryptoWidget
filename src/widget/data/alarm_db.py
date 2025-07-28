# QCryptoWidget/src/widget/data/alarm_db.py

import json
from pathlib import Path
from typing import List, Dict

ALARM_FILE = "alarms.json"

def get_alarm_db_path(root_path: Path) -> Path:
    """Returns the full path to the alarm database file."""
    return root_path / ALARM_FILE

def load_alarms(db_path: Path) -> List[Dict]:
    """
    Loads alarms from the JSON file.

    Args:
        db_path (Path): The path to the alarm database file.

    Returns:
        List[Dict]: A list of alarm dictionaries. Returns an empty list on failure.
    """
    if not db_path.exists():
        return []
    try:
        with open(db_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_alarms(db_path: Path, alarms: List[Dict]):
    """
    Saves alarms to the JSON file.

    Args:
        db_path (Path): The path to the alarm database file.
        alarms (List[Dict]): The list of alarm dictionaries to save.
    """
    try:
        with open(db_path, 'w') as f:
            json.dump(alarms, f, indent=4)
    except IOError as e:
        print(f"Error saving alarms: {e}")