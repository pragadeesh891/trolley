from googletrans import Translator

def test_translation():
    translator = Translator()
    
    # Test English to Hindi translation
    result = translator.translate('Where is the milk?', src='en', dest='hi')
    print(f"English to Hindi:")
    print(f"  Original: Where is the milk?")
    print(f"  Translated: {result.text}")
    print(f"  Pronunciation: {result.pronunciation}")
    
    # Test Hindi to English translation
    result = translator.translate('दूध कहाँ है?', src='hi', dest='en')
    print(f"\nHindi to English:")
    print(f"  Original: दूध कहाँ है?")
    print(f"  Translated: {result.text}")
    print(f"  Pronunciation: {result.pronunciation}")
    
    # Test other Indian languages
    languages = [
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('ml', 'Malayalam'),
        ('kn', 'Kannada'),
        ('bn', 'Bengali'),
        ('mr', 'Marathi'),
        ('gu', 'Gujarati'),
        ('pa', 'Punjabi')
    ]
    
    print(f"\nEnglish to other Indian languages:")
    for lang_code, lang_name in languages:
        try:
            result = translator.translate('Where is the milk?', src='en', dest=lang_code)
            print(f"  {lang_name} ({lang_code}): {result.text}")
        except Exception as e:
            print(f"  {lang_name} ({lang_code}): Error - {e}")

if __name__ == "__main__":
    test_translation()