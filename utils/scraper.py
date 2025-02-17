import requests
import json
import re
from bs4 import BeautifulSoup

from config import OUTPUT_DIRECTORY
from utils.file import save

def get_content(word: str, save_response: bool = False, verbose: bool = False):
    url = rf"https://en.wiktionary.org/w/api.php?action=parse&page={word}&format=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        # print("Request was successful")
        response.encoding = 'utf-8'  # Set the encoding to UTF-8
        
        response_text = json.loads(response.text)
        # if save_response:
        #     save(response_text, f"{word}_response_text.json")
        try:
            response_text_content = response_text["parse"]["text"]["*"]
        except KeyError:
            if verbose: print(f"Content (.text) not found for {word}. The page may not exist or other.")
            return None
        if save_response:
            save(response_text_content, f"{word}_response_text_content.html")

        return str(response_text_content)
    else:
        if verbose: print(f"Request for {word} failed with status code: {response.status_code}")

def isolate_language_section(soup: str, language: str, word: str, verbose: bool = False):
    # Find the language of interest section
    # print(f"Isolating {language} section")
    language_section = soup.find(id=language)
    if not language_section:
        if verbose: print(f"{language} section not found: {word}")
        return None
    
    # Remove all previous siblings of their parent
    for sibling in language_section.parent.find_previous_siblings():
        sibling.decompose()

    # Find the next language section, if present
    next_language_section = language_section.find_next("h2")
    if not next_language_section:
        return soup

    # Remove all next siblings of their parent
    for sibling in next_language_section.parent.find_next_siblings():
        sibling.decompose()

    return soup

def extract_ipa_for_language(content: str, language: str, word: str, verbose: bool = False):
    language = language.capitalize()

    soup = BeautifulSoup(content, 'html.parser')
    
    # Remove Unwanted Languages
    soup = isolate_language_section(soup, language, word, verbose=verbose)
    if not soup:
        return None
    # save(str(soup), f"{og_filename.split(".")[0]}_{language}_section.html")
    
    # Check if more then one etymology
    more_sections = False
    etymology_sections = soup.find_all(id=re.compile(r"Pronunciation"))
    if len(etymology_sections) > 1:
        more_sections = True

    # Find the first IPA that has a sibling with text IPA
    found_IPA_keyword = False
    first_ipa_section = None
    ipa_sections = soup.find_all("span", {"class": "IPA"})
    for ipa_section in ipa_sections:
        for sibling in ipa_section.find_previous_siblings():
            if sibling.text == "IPA":
                found_IPA_keyword = True
                first_ipa_section = ipa_section
                break
        if found_IPA_keyword:
            break
    
    ipa_section = first_ipa_section

    if ipa_section:
        # 1)  Try pattern like [t͡ɕʰɛk̚] ~ [t͡ɕʰe̞k̚] or [t͡ɕʌ̹] first (e.g. for Korean)
        ipa_pattern = re.compile(r"(\[.*\])")

        ipa_section = ipa_section.text
        ipa = ipa_pattern.search(ipa_section)
        if ipa:
            ipa = ipa.group(1)
            return (ipa, more_sections)
        else:
            # 2)  Try pattern like /t͡ɕʰɛk̚/ ~ /t͡ɕʰe̞k̚/ or /t͡ɕʌ̹/ next (e.g. for Italian)
            ipa_pattern = re.compile(r"(/.*/)")

            ipa = ipa_pattern.search(ipa_section)
            if ipa:
                ipa = ipa.group(1)
                return (ipa, more_sections)
            else:
                if verbose: print(f"IPA not found as [abcd] or /abcd/ for {language}: {word}, {ipa_section}")
                return None
    else:
        # 3) The IPA section wasn't present at all as class IPA
        if verbose: print(f"IPA not found as class=IPA for {language}: {word}")
        return None   
