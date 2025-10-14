"""
Simple test for Hugging Face client
"""

import os
from huggingface_hub import InferenceClient

# Initialize Hugging Face Inference Client
HF_API_KEY = os.getenv("HF_API_KEY", "your-huggingface-api-key-here")
hf_client = InferenceClient(api_key=HF_API_KEY)

try:
    # Test with a simple prompt
    response = hf_client.text_generation(
        "Question: What is the capital of France?\nAnswer:",
        model="google/flan-t5-base",
        max_new_tokens=50,
        temperature=0.7
    )
    
    print("Response:", response)
except Exception as e:
    print("Error:", str(e))