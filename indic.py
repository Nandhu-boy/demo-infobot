from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator

def transliterate_text(text, source_lang, target_lang):
    """
    Transliterate text from source language to target language.

    Parameters:
    - text (str): Text to transliterate.
    - source_lang (str): Source language code (e.g., 'hi' for Hindi).
    - target_lang (str): Target language code (e.g., 'en' for English).

    Returns:
    - str: Transliterated text.
    """
    try:
        return UnicodeIndicTransliterator.transliterate(text, source_lang, target_lang)
    except Exception as e:
        print(f"Error in transliteration: {e}")
        return text

# Example usage:
if __name__ == "__main__":
    text = "नमस्ते"
    transliterated_text = transliterate_text(text, 'hi', 'en')
    print(transliterated_text)
