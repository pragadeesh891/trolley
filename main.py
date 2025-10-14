import sys
import io

# Ensure proper encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi import FastAPI, WebSocket, Request, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

# Import additional libraries for multilingual support
try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
    translator = Translator()
except ImportError:
    TRANSLATOR_AVAILABLE = False
    translator = None

from langdetect import detect
import json

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

# Try to import voice processor
try:
    from voice_processor import VoiceProcessor
    VOICE_PROCESSOR_AVAILABLE = True
except ImportError:
    VOICE_PROCESSOR_AVAILABLE = False
    print("Voice processor not available")

app = FastAPI()

# Global voice processor instance
voice_processor = None

# Initialize voice processor with Ollama support
def initialize_voice_processor():
    global voice_processor
    # Check if Ollama model is specified
    ollama_model = os.getenv("OLLAMA_MODEL", "gemma:2b")
    # Local model path (optional)
    llama_model_path = os.getenv("LLAMA_MODEL_PATH")
    
    try:
        voice_processor = VoiceProcessor(
            whisper_model="base",
            llama_model_path=llama_model_path,
            ollama_model=ollama_model
        )
        print("Voice processor initialized with Ollama support")
    except Exception as e:
        print(f"Failed to initialize voice processor: {e}")
        # Fallback initialization
        voice_processor = VoiceProcessor(whisper_model="base")

# Initialize on startup
initialize_voice_processor()

# ===== Models =====
class PairRequest(BaseModel):
    code: str

class AskRequest(BaseModel):
    query: str
    language: str = "en"  # Added language field

class Item(BaseModel):
    name: str
    price: float
    qty: int

class CheckoutRequest(BaseModel):
    cart: List[Item]

class VoiceRequest(BaseModel):
    text: str
    language: str = "en"

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "en"

class LlamaConfig(BaseModel):
    model_path: Optional[str] = None
    ollama_model: Optional[str] = None

# ===== API Endpoints =====
@app.post("/api/pair")
def pair_cart(req: PairRequest):
    if req.code.upper() == "SC1234":
        return {"success": True, "cartId": 1234, "battery": 94}
    return {"success": False, "error": "Invalid code"}

@app.post("/api/ask")
def ask_ai(req: AskRequest):
    # Detect language if not provided
    if not req.language:
        try:
            detected_lang = detect(req.query)
            req.language = detected_lang
        except:
            req.language = "en"
    
    # Translate query to English if needed
    translated_query = req.query
    if req.language != "en":
        try:
            # Try to decode if it's bytes
            if isinstance(req.query, bytes):
                req.query = req.query.decode('utf-8')
            
            # Use translate library with proper encoding
            from translate import Translator as TextTranslator
            text_translator = TextTranslator(from_lang=req.language, to_lang="en")
            translated_query = text_translator.translate(req.query)
        except Exception as e:
            print(f"Translation error: {e}")
            translated_query = req.query  # Use original query if translation fails
    
    # Use Hugging Face model to get AI response if available
    if HF_AVAILABLE and hf_client:
        try:
            # Using a general question-answering model that's more widely supported
            response = hf_client.text_generation(
                f"Question: {translated_query}\nAnswer:",
                model="google/flan-t5-base",  # Using a more widely supported model
                max_new_tokens=100,
                temperature=0.7
            )
            
            response_text = response
        except Exception as e:
            # Fallback to voice processor if available
            response_text = get_response_from_voice_processor(translated_query)
    else:
        # Fallback to voice processor if available
        response_text = get_response_from_voice_processor(translated_query)
    
    # Translate response back to original language if needed
    if req.language != "en":
        try:
            # Use translate library with proper encoding
            from translate import Translator as TextTranslator
            text_translator = TextTranslator(from_lang="en", to_lang=req.language)
            response_text = text_translator.translate(response_text)
        except Exception as e:
            print(f"Response translation error: {e}")
            # Keep English response if translation fails
    
    # Ensure proper encoding for response
    if isinstance(response_text, bytes):
        response_text = response_text.decode('utf-8')
    
    return {"response": response_text, "language": req.language}

# Hugging Face powered multilingual endpoint
@app.post("/api/ai-assist-multilingual")
async def ai_assist_multilingual(req: AskRequest):
    """
    Uses Hugging Face models to assist shopping with multilingual support.
    """
    # Detect language if not provided
    if not req.language:
        try:
            detected_lang = detect(req.query)
            req.language = detected_lang
        except:
            req.language = "en"
    
    # Translate query to English for processing
    translated_query = req.query
    if req.language != "en":
        try:
            if TRANSLATOR_AVAILABLE and translator:
                translation = translator.translate(req.query, src=req.language, dest='en')
                translated_query = translation.text
            else:
                # Fallback to simple approach
                from translate import Translator as TextTranslator
                text_translator = TextTranslator(from_lang=req.language, to_lang="en")
                translated_query = text_translator.translate(req.query)
        except Exception as e:
            print(f"Translation error: {e}")
            translated_query = req.query  # Use original query if translation fails
    
    if HF_AVAILABLE and hf_client:
        # Create prompt for Hugging Face model
        prompt = f"Question: {translated_query}\nAnswer:"
        
        try:
            # Use Hugging Face model (using a more widely supported model)
            response = hf_client.text_generation(
                prompt,
                model="google/flan-t5-base",
                max_new_tokens=100,
                temperature=0.7
            )
            
            answer = response.strip()
        except Exception as e:
            # Fallback response in case of API error
            answer = "I'm here to help with your shopping! Please ask about specific products or shopping advice."
    else:
        # Fallback to simple response if Hugging Face is not available
        answer = "I'm here to help with your shopping! Please ask about specific products or shopping advice."
    
    # Translate response back to original language if needed
    if req.language != "en":
        try:
            if TRANSLATOR_AVAILABLE and translator:
                translation = translator.translate(answer, src='en', dest=req.language)
                answer = translation.text
            else:
                # Fallback to simple approach
                from translate import Translator as TextTranslator
                text_translator = TextTranslator(from_lang="en", to_lang=req.language)
                answer = text_translator.translate(answer)
        except Exception as e:
            print(f"Response translation error: {e}")
            # Keep English response if translation fails
    
    return {"response": answer, "language": req.language}

@app.post("/api/checkout")
def checkout(req: CheckoutRequest):
    total = sum(item.price * item.qty for item in req.cart)
    return {"success": True, "message": "Payment successful", "total": total}

# Language detection endpoint
@app.post("/api/detect-language")
async def detect_language(req: TranslationRequest):
    try:
        if req.source_lang == "auto":
            detected_lang = detect(req.text)
            language_name = get_language_name(detected_lang)
            return {"language": detected_lang, "language_name": language_name}
        else:
            language_name = get_language_name(req.source_lang)
            return {"language": req.source_lang, "language_name": language_name}
    except Exception as e:
        return {"error": str(e)}

# Translation endpoint
@app.post("/api/translate")
async def translate_text(req: TranslationRequest):
    try:
        # Try to decode if it's bytes
        if isinstance(req.text, bytes):
            req.text = req.text.decode('utf-8')
            
        if req.source_lang == "auto":
            # Detect source language
            source_lang = detect(req.text)
        else:
            source_lang = req.source_lang
            
        # Translate text
        from translate import Translator as TextTranslator
        text_translator = TextTranslator(from_lang=source_lang, to_lang=req.target_lang)
        translated_text = text_translator.translate(req.text)
        
        # Ensure proper encoding for response
        if isinstance(translated_text, bytes):
            translated_text = translated_text.decode('utf-8')
            
        return {
            "original_text": req.text,
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": req.target_lang
        }
    except Exception as e:
        return {"error": str(e)}

# Helper function to get language name
def get_language_name(lang_code):
    languages = {
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
    return languages.get(lang_code, "Unknown")

# ===== WebSocket =====
@app.websocket("/ws/cart/{cart_id}")
async def cart_ws(websocket: WebSocket, cart_id: int):
    await websocket.accept()
    await websocket.send_text(f"Connected to cart {cart_id}")
    await websocket.send_text("Head to Aisle 3 for Bread")
    await websocket.send_text("Proceed to Aisle 7 for Milk")
    await websocket.send_text("Checkout lane ready")
    await websocket.close()

# ===== Voice Command Processing =====
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

# ===== Local LLM Voice Processing =====
@app.post("/api/local-voice-process")
async def local_voice_process(duration: int = 5):
    """
    Process voice using local Whisper, LLaMA, and Indic-TTS
    """
    global voice_processor
    
    if not VOICE_PROCESSOR_AVAILABLE or not voice_processor:
        return {"error": "Voice processor not available"}
    
    try:
        # Record audio
        audio_data = voice_processor.record_audio(duration)
        if audio_data is None:
            return {"error": "Failed to record audio"}
            
        # Save audio to temporary file
        temp_file = voice_processor.save_audio_to_temp_file(audio_data)
        if not temp_file:
            return {"error": "Failed to save audio file"}
            
        try:
            # Convert speech to text
            user_text = voice_processor.speech_to_text(temp_file)
            
            # Generate response
            prompt = f"""You are a helpful shopping assistant in a supermarket. 
User: {user_text}
Assistant:"""
            response_text = voice_processor.generate_response(prompt)
            
            # Return results
            return {
                "user_text": user_text,
                "assistant_response": response_text,
                "status": "success"
            }
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass
                
    except Exception as e:
        return {"error": f"Error processing voice: {str(e)}"}

# ===== LLaMA Model Configuration =====
@app.post("/api/configure-llama")
async def configure_llama(config: LlamaConfig):
    """
    Configure the LLaMA model (either local or Ollama)
    """
    global voice_processor
    
    try:
        # Reinitialize voice processor with new configuration
        voice_processor = VoiceProcessor(
            whisper_model="base",
            llama_model_path=config.model_path,
            ollama_model=config.ollama_model or "llama3:8b"
        )
        
        # Set environment variables for future use
        if config.model_path:
            os.environ["LLAMA_MODEL_PATH"] = config.model_path
        if config.ollama_model:
            os.environ["OLLAMA_MODEL"] = config.ollama_model
        
        return {"status": "success", "message": "LLM configured successfully"}
    except Exception as e:
        return {"error": f"Failed to configure LLM: {str(e)}"}

# ===== Serve Frontend =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "index.html")
VOICE_CONTROL_FILE = os.path.join(BASE_DIR, "voice_control.html")

@app.get("/")
def serve_home():
    return FileResponse(HTML_FILE)

@app.get("/voice-control", response_class=HTMLResponse)
def serve_voice_control():
    return FileResponse(VOICE_CONTROL_FILE)

def get_response_from_voice_processor(query):
    """
    Get response from voice processor using Ollama/LLaMA
    """
    global voice_processor
    
    if VOICE_PROCESSOR_AVAILABLE and voice_processor:
        try:
            # Enhanced prompt with built-in knowledge for shopping context
            prompt = f"""You are a smart shopping trolley assistant with built-in knowledge of a supermarket.
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
- Eggs: $2.99, Brand: Farm Fresh, Location: Aisle 2, Shelf A
- Cheese: $4.99, Brand: Alpine Cheese, Location: Aisle 2, Shelf C
- Chicken: $5.99/lb, Type: Boneless breast, Location: Aisle 3, Shelf B
- Pasta: $1.49, Brand: Italiano, Location: Aisle 4, Shelf A
- Cereal: $3.49, Brand: Healthy Start, Location: Aisle 4, Shelf B
- Soda: $1.29, Brand: Fizz Cola, Location: Aisle 5, Shelf A
- Chips: $2.99, Brand: Crunchy Snacks, Location: Aisle 5, Shelf C
- Ice Cream: $4.49, Brand: Creamy Delight, Location: Aisle 6, Shelf A
- Shampoo: $5.99, Brand: Silky Hair, Location: Aisle 7, Shelf B
- Toothpaste: $2.49, Brand: Bright Smile, Location: Aisle 7, Shelf A

User: {query}
Assistant:"""
            
            # Try to get response from Ollama
            response_text = voice_processor.generate_response(prompt)
            
            # If we got a response, use it
            if response_text and "Error" not in response_text and response_text.strip():
                print(f"LLM Response: {response_text}")
                return response_text
            else:
                # Check if it's a memory issue
                if voice_processor.ollama_available:
                    print("LLM not available due to memory constraints, using fallback response")
                return f"🤖 I'm your smart shopping assistant. You asked about: {query}. I can help you find products in the store."
        except Exception as e:
            print(f"Error getting response from voice processor: {e}")
            return f"🤖 Suggestion: Try Store Brand to save 10% on {query}"
    else:
        return f"🤖 Suggestion: Try Store Brand to save 10% on {query}"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
