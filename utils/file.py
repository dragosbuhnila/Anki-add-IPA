from bs4 import BeautifulSoup
from config import OUTPUT_DIRECTORY
import json

def get_readable_html(parsed_html: str):
    soup = BeautifulSoup(parsed_html, 'html.parser')
    parsed_html = soup.prettify()

    larger_indentation_html = parsed_html.replace("  ", "    ")
    return larger_indentation_html

def save(data: dict, filename: str):
    def _save_text(data: str, filename: str):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(data)
            print(f"Data saved to {filename} as text")
            
    def _save_json(data: dict, filename: str):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Data saved to {filename} as JSON")
    
    def _save_html(data: str, filename: str):
        with open(filename, "w", encoding="utf-8") as file:
            data = get_readable_html(data)
            file.write(data)
            print(f"Data saved to {filename} as HTML")

    if OUTPUT_DIRECTORY:
        filename = f"{OUTPUT_DIRECTORY}/{filename}"

    if filename.endswith(".json"):
        _save_json(data, filename)
    elif filename.endswith(".html"):
        _save_html(data, filename)
    else:
        _save_text(data, filename)
    return