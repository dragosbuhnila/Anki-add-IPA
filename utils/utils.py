import re
import os
from datetime import datetime
import json
import unicodedata

from config import OUTPUT_DIRECTORY, DATE_FORMAT

def parse_date(filename):
    # Extract date string from "something@YYYYMMDD-HHMMSS.json" 
    pattern = re.compile(r"\w+@(\d{8}-\d{6}).json")
    match = pattern.search(filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, "%Y%m%d-%H%M%S")
    else:
        return None

def load_anki_json(filename: str):
    if not (filename.startswith("anki@") or filename.startswith("after_anki@")) and not filename.endswith(".json"):
        raise ValueError(f"Invalid filename: {filename}")

    original_time = parse_date(filename).strftime(DATE_FORMAT)

    if original_time is None:
        raise ValueError(f"Invalid filename for parsing timestamp: {filename}")

    # Load and return the file contents
    with open(os.path.join(OUTPUT_DIRECTORY, filename), 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data, original_time

def load_most_recent_anki_json():
    """Load the most recent anki json file from the outputs directory
    
    Returns:
        dict: The contents of the most recent anki json file
    """
    # List all anki json files in the output directory
    anki_files = [f for f in os.listdir(OUTPUT_DIRECTORY) if f.startswith("anki@") and f.endswith(".json")]
    
    if not anki_files:
        raise FileNotFoundError("No anki json files found in outputs directory")
    
    most_recent = max(anki_files, key=parse_date)
    print(f"Loading most recent file: {most_recent}")

    return load_anki_json(most_recent)

def is_word(string: str) -> bool:
    """Check if a string is a word (contains only letters, hyphens, Japanese, and Korean characters)

    Args:
        string (str): The string to check

    Returns:
        bool: True if the string is a word, False otherwise
    """
    for char in string:
        category = unicodedata.category(char)
        if not (category.startswith('L') or char == '-'):  # 'L' for Letter in any language
            return False
    return True

def preprocess_word(word: str) -> str:
    """Preprocess a word for IPA extraction"""
    return word.lower().strip().strip("-").strip("?")

def preprocess_phrase(phrase: str, verbose: bool = False) -> str:
    phrase_as_list = []
    words = phrase.split()
    for word in words:
        word = preprocess_word(word)
        if is_word(word):
            phrase_as_list.append(word)
    return " ".join(phrase_as_list)