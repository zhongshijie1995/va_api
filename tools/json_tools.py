import json
import os.path
from typing import Dict


def load(filename: str) -> Dict:
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}


def save(data: Dict, filename: str):
    with open(filename, 'w') as f:
        json.dump(data, f)
    return None
