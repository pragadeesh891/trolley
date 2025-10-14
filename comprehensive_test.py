import requests
import json

def test_multilingual_support():
    """Comprehensive test for multilingual support"""
    
    # Test cases for different Indian languages
    test_cases = [
        {
            "name": "English",
            "query": "Where is the milk?",
            "language": "en",
            "expected_keywords": ["milk", "aisle"]
        },
        {
            "name": "Hindi",
            "query": "दूध कहाँ है?",
            "language": "hi",
            "expected_keywords": ["दूध"]  # We expect the response to be in Hindi
        },
        {
            "name": "Tamil",
            "query": "பால் எங்கே?",
            "language": "ta",
            "expected_keywords": ["பால்"]
        },
        {
            "name": "Telugu",
            "query": "పాల ఎక్కడ?",
            "language": "te",
            "expected_keywords": ["పాల"]
        }
    ]
    
    url = "http://127.0.0.1:8000/api/ask"
    
    print("Testing multilingual support...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        
        payload = {
            "query": test_case["query"],
            "language": test_case["language"]
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', 'No response')
                language = data.get('language', 'Unknown')
                
                print(f"  Response: {response_text}")
                print(f"  Language: {language}")
                
                # Check if response contains expected keywords
                found_keywords = [kw for kw in test_case["expected_keywords"] if kw.lower() in response_text.lower()]
                if found_keywords:
                    print(f"  ✅ Contains expected keywords: {found_keywords}")
                else:
                    print(f"  ⚠️  May not contain expected keywords")
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Connection error: {e}")
    
    # Test direct translation
    print("\n" + "=" * 50)
    print("Testing direct translation...")
    
    translation_url = "http://127.0.0.1:8000/api/translate"
    translation_payload = {
        "text": "Where is the milk?",
        "source_lang": "en",
        "target_lang": "hi"
    }
    
    try:
        response = requests.post(translation_url, json=translation_payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Translation Test:")
            print(f"  Original: {data.get('original_text', 'N/A')}")
            print(f"  Translated: {data.get('translated_text', 'N/A')}")
            print(f"  Source Language: {data.get('source_language', 'N/A')}")
            print(f"  Target Language: {data.get('target_language', 'N/A')}")
        else:
            print(f"  ❌ Translation Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  ❌ Translation Connection error: {e}")

if __name__ == "__main__":
    test_multilingual_support()