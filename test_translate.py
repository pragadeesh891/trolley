# Test the translate library directly
try:
    from translate import Translator
    print("Translate library imported successfully")
    
    # Test translation
    translator = Translator(from_lang="en", to_lang="hi")
    result = translator.translate("Where is the milk?")
    print(f"Translation result: {result}")
    print(f"Type: {type(result)}")
    
    # Test with explicit encoding
    text = "Where is the milk?"
    result = translator.translate(text)
    print(f"Encoded result: {result.encode('utf-8')}")
    print(f"Decoded result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()