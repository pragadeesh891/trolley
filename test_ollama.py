import requests
import json

def test_ollama_connection():
    """Test the Ollama connection and get a response from the gemma model"""
    url = "http://localhost:11434/api/generate"
    
    # Test prompt for a shopping assistant
    prompt = """You are a smart shopping trolley assistant with built-in knowledge of a supermarket.
Store layout:
- Aisle 1: Entrance, Bakery, Fresh Produce
- Aisle 2: Dairy, Eggs, Cheese
- Aisle 3: Meat, Poultry, Seafood
- Aisle 4: Canned Goods, Pasta, Rice
- Aisle 5: Beverages, Snacks
- Aisle 6: Frozen Foods
- Aisle 7: Personal Care, Cleaning Supplies
- Aisle 8: Checkout

Product information:
- Milk: $3.99, Brand: Happy Cow Dairy, Location: Aisle 2, Shelf B
- Bread: $2.49, Brand: Golden Grain, Location: Aisle 1, Shelf A
- Apples: $1.99/lb, Organic available, Location: Aisle 1, Shelf C

User: Where is the milk?
Assistant:"""
    
    payload = {
        "model": "gemma:2b",
        "prompt": prompt,
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Ollama Response:")
            print(data.get("response", "No response received"))
            return data.get("response", "")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

if __name__ == "__main__":
    print("Testing Ollama connection with gemma:2b model...")
    response = test_ollama_connection()
    if response:
        print("\nSuccess! Ollama is working correctly.")
    else:
        print("\nFailed to connect to Ollama.")