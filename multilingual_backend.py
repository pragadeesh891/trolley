"""
Multilingual Voice Integration and Trolley Control Backend
Supports 10 Indian languages including English
"""

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from translate import Translator as TextTranslator
from langdetect import detect
import json
import re

# Try to import Hugging Face, but provide fallback if not available
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
    # Initialize Hugging Face Inference Client
    HF_API_KEY = os.getenv("HF_API_KEY", "your-huggingface-api-key-here")
    hf_client = InferenceClient(api_key=HF_API_KEY)
except ImportError:
    HF_AVAILABLE = False
    hf_client = None

# Initialize FastAPI app
app = FastAPI()

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "kn": "Kannada",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi"
}

# Shopping cart
cart = []

# Define command patterns for different actions
COMMAND_PATTERNS = {
    "movement": {
        "forward": ["move forward", "go forward", "forward", "ahead"],
        "backward": ["move backward", "go backward", "backward", "back", "reverse"],
        "left": ["turn left", "left"],
        "right": ["turn right", "right"],
        "stop": ["stop", "halt", "pause"]
    },
    "speed": {
        "increase": ["faster", "speed up", "increase speed", "go faster"],
        "decrease": ["slower", "slow down", "decrease speed", "go slower"]
    },
    "cart": ["show cart", "cart", "my items", "what's in my cart"],
    "checkout": ["checkout", "pay", "bill", "check out"],
    "help": ["help", "assist", "support", "what can you do"]
}

class VoiceRequest(BaseModel):
    text: str
    language: str = "en"

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "en"

class TrolleyCommand(BaseModel):
    command: str
    language: str = "en"

# Language detection endpoint
@app.post("/api/detect-language")
async def detect_language(req: TranslationRequest):
    try:
        if req.source_lang == "auto":
            detected_lang = detect(req.text)
            return {"language": detected_lang, "language_name": SUPPORTED_LANGUAGES.get(detected_lang, "Unknown")}
        else:
            return {"language": req.source_lang, "language_name": SUPPORTED_LANGUAGES.get(req.source_lang, "Unknown")}
    except Exception as e:
        return {"error": str(e)}

# Translation endpoint
@app.post("/api/translate")
async def translate_text(req: TranslationRequest):
    try:
        if req.source_lang == "auto":
            # Detect source language
            source_lang = detect(req.text)
        else:
            source_lang = req.source_lang
            
        # Translate text
        translator = TextTranslator(from_lang=source_lang, to_lang=req.target_lang)
        translated_text = translator.translate(req.text)
        
        return {
            "original_text": req.text,
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": req.target_lang
        }
    except Exception as e:
        return {"error": str(e)}

# Multilingual voice processing endpoint
@app.post("/api/voice-command")
async def process_voice_command(req: VoiceRequest):
    """
    Process voice commands using pattern matching with Hugging Face fallback
    """
    try:
        # Normalize the text
        text = req.text.lower().strip()
        
        # If language is not English, translate to English for processing
        processed_text = text
        if req.language != "en":
            try:
                translator = TextTranslator(from_lang=req.language, to_lang="en")
                processed_text = translator.translate(text).lower().strip()
            except:
                pass
        
        # Try to use Hugging Face for command classification if available
        if HF_AVAILABLE and hf_client:
            try:
                # Create a prompt for the Hugging Face model to determine the action
                prompt = f"""
                Classify the following shopping command into one of these categories:
                movement, speed, cart, checkout, help, product_info, unknown
                
                Command: "{processed_text}"
                
                Category:
                """
                
                # Get response from Hugging Face model
                response = hf_client.text_generation(
                    prompt,
                    model="google/flan-t5-base",
                    max_new_tokens=20,
                    temperature=0.3  # Low temperature for more deterministic responses
                )
                
                # Extract the category from the response
                category = response.strip().lower()
                
                # Determine the appropriate response based on category
                if "movement" in category:
                    if "forward" in processed_text:
                        response_data = {"action": "movement", "direction": "forward", "message": "Moving forward"}
                    elif "backward" in processed_text or "back" in processed_text:
                        response_data = {"action": "movement", "direction": "backward", "message": "Moving backward"}
                    elif "left" in processed_text:
                        response_data = {"action": "movement", "direction": "left", "message": "Turning left"}
                    elif "right" in processed_text:
                        response_data = {"action": "movement", "direction": "right", "message": "Turning right"}
                    elif "stop" in processed_text:
                        response_data = {"action": "movement", "direction": "stop", "message": "Stopping"}
                    else:
                        response_data = {"action": "movement", "direction": "forward", "message": "Moving forward"}
                elif "speed" in category:
                    if "increase" in processed_text or "faster" in processed_text:
                        response_data = {"action": "speed", "change": "increase", "message": "Increasing speed"}
                    else:
                        response_data = {"action": "speed", "change": "decrease", "message": "Decreasing speed"}
                elif "cart" in category:
                    response_data = {"action": "cart", "message": "Showing your cart contents"}
                elif "checkout" in category:
                    response_data = {"action": "checkout", "message": "Proceeding to checkout"}
                elif "help" in category:
                    response_data = {"action": "help", "message": "Available commands: move forward, turn left, turn right, stop, faster, slower, show cart, checkout, help"}
                elif "product" in category:
                    response_data = {"action": "product_info", "product": processed_text, "message": f"Getting information about {processed_text}"}
                else:
                    response_data = {"action": "unknown", "message": "Sorry, I didn't understand that command. Say 'help' for available commands."}
                    
            except Exception as e:
                # Fallback to pattern matching if Hugging Face fails
                response_data = process_command_with_patterns(processed_text)
        else:
            # Use pattern matching if Hugging Face is not available
            response_data = process_command_with_patterns(processed_text)
        
        # Translate response back to original language if needed
        if req.language != "en":
            try:
                translator = TextTranslator(from_lang="en", to_lang=req.language)
                response_data["message"] = translator.translate(response_data["message"])
            except:
                pass
        
        return response_data
    except Exception as e:
        return {"action": "error", "message": f"Error processing voice command: {str(e)}"}

def process_command_with_patterns(text):
    """Process command using pattern matching"""
    # Check for movement commands
    for direction, patterns in COMMAND_PATTERNS["movement"].items():
        for pattern in patterns:
            if pattern in text:
                return {"action": "movement", "direction": direction, "message": f"Moving {direction}"}
    
    # Check for speed commands
    for change, patterns in COMMAND_PATTERNS["speed"].items():
        for pattern in patterns:
            if pattern in text:
                return {"action": "speed", "change": change, "message": f"{'Increasing' if change == 'increase' else 'Decreasing'} speed"}
    
    # Check for other commands
    for pattern in COMMAND_PATTERNS["cart"]:
        if pattern in text:
            return {"action": "cart", "message": "Showing your cart contents"}
    
    for pattern in COMMAND_PATTERNS["checkout"]:
        if pattern in text:
            return {"action": "checkout", "message": "Proceeding to checkout"}
    
    for pattern in COMMAND_PATTERNS["help"]:
        if pattern in text:
            return {"action": "help", "message": "Available commands: move forward, turn left, turn right, stop, faster, slower, show cart, checkout, help"}
    
    # Default response
    return {"action": "unknown", "message": "Sorry, I didn't understand that command. Say 'help' for available commands."}

# Trolley control endpoint
@app.post("/api/trolley-control")
async def trolley_control(cmd: TrolleyCommand):
    """Direct trolley control endpoint"""
    try:
        # Reuse the voice command processing logic
        voice_req = VoiceRequest(text=cmd.command, language=cmd.language)
        return await process_voice_command(voice_req)
    except Exception as e:
        return {"action": "error", "message": f"Error controlling trolley: {str(e)}"}

# WebSocket endpoint for real-time communication
@app.websocket("/ws/trolley/{trolley_id}")
async def trolley_websocket(websocket: WebSocket, trolley_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process the received data
            response = {"status": "received", "data": data}
            await websocket.send_json(response)
    except Exception as e:
        await websocket.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Multilingual voice integration backend is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)