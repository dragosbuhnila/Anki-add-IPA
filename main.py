import argparse

from utils.scraper import extract_ipa_for_language, get_content


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Wiktionary IPA Scraper and Anki Updater')
    parser.add_argument('--test_word', nargs=2, metavar=('WORD', 'LANGUAGE'),
                      help='Parse a single word and see the extracted IPA. Takes two arguments: WORD and LANGUAGE (e.g., "책 korean")')

    return parser.parse_args()

def test_word(word: str):
    content = get_content(word, save_response=True)

    ipa = extract_ipa_for_language(content, "korean", word)
    if ipa:
        print(ipa)


if __name__ == "__main__":
    args = parse_args()
    
    if args.test_word:
        word, language = args.test_word
        print(f"Testing {language} language: {word}")
        test_word(word, language)