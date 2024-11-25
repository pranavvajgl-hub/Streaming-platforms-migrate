import os
import json
import time
from main import get_last_progress, save_progress
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_get_last_progress_no_file():
    progress = get_last_progress("nonexistent_file.json")
    assert progress == {}


def test_save_progress():

    time.sleep(1)
    temp_filename = "temp_progress.json"
    test_data = {"test_playlist": {"id": "test_id", "last_track_index": 1}}
    save_progress(test_data, temp_filename)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, temp_filename)

    with open(file_path, "r") as f:
        loaded_data = json.load(f)
    assert loaded_data == test_data

    os.remove(file_path)