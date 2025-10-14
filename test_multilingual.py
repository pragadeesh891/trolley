import requests
import json

def test_multilingual_support():
    """Test the multilingual support for different Indian languages"""
    
    # Test cases for different Indian languages
    test_cases = [
        {"query": "Where is the milk?", "language": "en", "expected": "milk"},
        {"query": "दूध कहाँ है?", "language": "hi", "expected": "दूध"},
        {"query": "பால் எங்கே?", "language": "ta", "expected": "பால்"},
        {"query": "పాల ఎక్కడ?", "language": "te", "expected": "పాల"},
    ]
    
    url = "http://127.0.0.1:8000/api/ask"
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['language']} - {test_case['query']}")
        
        payload = {
            "query": test_case["query"],
            "language": test_case["language"]
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"  Response: {data.get('response', 'No response')}")
                print(f"  Language: {data.get('language', 'Unknown')}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  Connection error: {e}")

def test_translation_endpoint():
    """Test the translation endpoint directly"""
    url = "http://127.0.0.1:8000/api/translate"
    
    # Test translation from English to Hindi
    payload = {
        "text": "Where is the milk?",
        "source_lang": "en",
        "target_lang": "hi"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"\nTranslation Test:")
            print(f"  Original: {data.get('original_text', 'N/A')}")
            print(f"  Translated: {data.get('translated_text', 'N/A')}")
            print(f"  Source Language: {data.get('source_language', 'N/A')}")
            print(f"  Target Language: {data.get('target_language', 'N/A')}")
        else:
            print(f"  Translation Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  Translation Connection error: {e}")

if __name__ == "__main__":
    print("Testing multilingual support...")
    test_multilingual_support()
    test_translation_endpoint()