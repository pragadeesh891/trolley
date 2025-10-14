"""
Test script for the updated implementation
"""

import os
import requests
import json

# Test the voice command endpoint
def test_voice_command():
    url = "http://127.0.0.1:8000/api/voice-command"
    
    # Test data
    test_data = {
        "text": "move forward",
        "language": "en"
    }
    
    try:
        response = requests.post(url, json=test_data)
        print("Status Code:", response.status_code)
        print("Response:", response.json())
    except Exception as e:
        print("Error:", str(e))

# Test the ask endpoint
def test_ask():
    url = "http://127.0.0.1:8000/api/ask"
    
    # Test data
    test_data = {
        "query": "What is the price of milk?",
        "language": "en"
    }
    
    try:
        response = requests.post(url, json=test_data)
        print("Status Code:", response.status_code)
        print("Response:", response.json())
    except Exception as e:
        print("Error:", str(e))

# Test product info
def test_product_info():
    url = "http://127.0.0.1:8000/api/voice-command"
    
    # Test data
    test_data = {
        "text": "show cart",
        "language": "en"
    }
    
    try:
        response = requests.post(url, json=test_data)
        print("Status Code:", response.status_code)
        print("Response:", response.json())
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    print("Testing voice command endpoint...")
    test_voice_command()
    
    print("\nTesting ask endpoint...")
    test_ask()
    
    print("\nTesting cart command...")
    test_product_info()