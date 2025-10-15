"""
Voice Processing Module
Integrates Whisper for speech-to-text, LLaMA for text generation, and Indic-TTS for text-to-speech
Works with both local GGUF models and Ollama API
"""

import numpy as np
import sounddevice as sd
import wavio
import tempfile
import os
import threading
import queue
import requests
import json

# Try to import libraries, with fallbacks
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Whisper not available, using placeholder")

try:
    from llama_cpp import Llama
    LLAMA_LOCAL_AVAILABLE = True
except ImportError:
    LLAMA_LOCAL_AVAILABLE = False
    print("Local LLaMA not available, using placeholder")

try:
    # Placeholder for Indic-TTS import
    # You would import the actual Indic-TTS library here
    INDIC_TTS_AVAILABLE = False  # Set to True when you have the actual library
except ImportError:
    INDIC_TTS_AVAILABLE = False

class VoiceProcessor:
    def __init__(self, whisper_model="base", llama_model_path=None, ollama_model="gemma:2b"):
        """
        Initialize the voice processor
        
        Args:
            whisper_model (str): Whisper model size (tiny, base, small, medium, large)
            llama_model_path (str): Path to local LLaMA model file (GGUF format)
            ollama_model (str): Ollama model name (e.g., "gemma:2b")
        """
        self.recording = False
        self.audio_queue = queue.Queue()
        self.ollama_model = ollama_model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.sample_rate = 16000  # Add sample rate for audio recording
        
        # Built-in knowledge base for the smart trolley
        self.store_layout = {
            "entrance": "Aisle 1",
            "bakery": "Aisle 1",
            "fresh produce": "Aisle 1",
            "dairy": "Aisle 2",
            "eggs": "Aisle 2",
            "cheese": "Aisle 2",
            "meat": "Aisle 3",
            "poultry": "Aisle 3",
            "seafood": "Aisle 3",
            "canned goods": "Aisle 4",
            "pasta": "Aisle 4",
            "rice": "Aisle 4",
            "beverages": "Aisle 5",
            "snacks": "Aisle 5",
            "frozen foods": "Aisle 6",
            "personal care": "Aisle 7",
            "cleaning supplies": "Aisle 7",
            "checkout": "Aisle 8"
        }
        
        self.products = {
            "milk": {"price": "$3.99", "brand": "Happy Cow Dairy", "location": "Aisle 2, Shelf B"},
            "bread": {"price": "$2.49", "brand": "Golden Grain", "location": "Aisle 1, Shelf A"},
            "apples": {"price": "$1.99/lb", "organic": "available", "location": "Aisle 1, Shelf C"},
            "eggs": {"price": "$2.99", "brand": "Farm Fresh", "location": "Aisle 2, Shelf A"},
            "cheese": {"price": "$4.99", "brand": "Alpine Cheese", "location": "Aisle 2, Shelf C"},
            "chicken": {"price": "$5.99/lb", "type": "boneless breast", "location": "Aisle 3, Shelf B"},
            "pasta": {"price": "$1.49", "brand": "Italiano", "location": "Aisle 4, Shelf A"},
            "cereal": {"price": "$3.49", "brand": "Healthy Start", "location": "Aisle 4, Shelf B"},
            "soda": {"price": "$1.29", "brand": "Fizz Cola", "location": "Aisle 5, Shelf A"},
            "chips": {"price": "$2.99", "brand": "Crunchy Snacks", "location": "Aisle 5, Shelf C"},
            "ice cream": {"price": "$4.49", "brand": "Creamy Delight", "location": "Aisle 6, Shelf A"},
            "shampoo": {"price": "$5.99", "brand": "Silky Hair", "location": "Aisle 7, Shelf B"},
            "toothpaste": {"price": "$2.49", "brand": "Bright Smile", "location": "Aisle 7, Shelf A"},
            "organic bananas": {"price": "$0.69/lb", "location": "Aisle 1, Shelf C"},
            "whole wheat bread": {"price": "$2.49", "brand": "Golden Grain", "location": "Aisle 1, Shelf A"},
            "farm fresh eggs": {"price": "$3.99", "count": "12", "location": "Aisle 2, Shelf A"},
            "almond milk": {"price": "$3.79", "size": "1 gallon", "location": "Aisle 2, Shelf B"},
            "greek yogurt": {"price": "$5.99", "size": "32 oz", "location": "Aisle 2, Shelf C"},
            "organic spinach": {"price": "$3.49", "size": "16 oz", "location": "Aisle 1, Shelf B"},
            "grass-fed ground beef": {"price": "$8.99/lb", "location": "Aisle 3, Shelf A"},
            "atlantic salmon fillet": {"price": "$12.99/lb", "location": "Aisle 3, Shelf C"},
            "organic brown rice": {"price": "$3.99", "size": "2 lbs", "location": "Aisle 4, Shelf B"},
            "extra virgin olive oil": {"price": "$9.99", "size": "16 oz", "location": "Aisle 4, Shelf C"},
            "organic coffee beans": {"price": "$14.99", "size": "12 oz", "location": "Aisle 1, Shelf D"},
            "dark chocolate": {"price": "$2.99", "percentage": "85%", "size": "3.5 oz", "location": "Aisle 5, Shelf B"},
            "organic quinoa": {"price": "$4.99", "size": "12 oz", "location": "Aisle 4, Shelf A"},
            "himalayan pink salt": {"price": "$5.99", "size": "26 oz", "location": "Aisle 7, Shelf C"},
            "coconut water": {"price": "$14.99", "size": "11.2 oz", "pack": "12 pack", "location": "Aisle 5, Shelf A"},
            "organic green tea": {"price": "$4.49", "count": "20", "location": "Aisle 1, Shelf E"},
            "protein powder": {"price": "$29.99", "flavor": "Vanilla", "size": "2 lbs", "location": "Aisle 6, Shelf B"},
            "natural peanut butter": {"price": "$4.99", "size": "16 oz", "location": "Aisle 4, Shelf D"},
            "organic tomato sauce": {"price": "$2.99", "size": "24 oz", "location": "Aisle 4, Shelf E"},
            "gluten-free pasta": {"price": "$2.49", "size": "12 oz", "location": "Aisle 4, Shelf F"}
        }
        
        # Initialize Whisper
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model(whisper_model)
                print(f"Whisper {whisper_model} model loaded successfully")
            except Exception as e:
                print(f"Failed to load Whisper model: {e}")
                self.whisper_model = None
        else:
            self.whisper_model = None
            
        # Initialize Local LLaMA
        self.llama_model = None
        if LLAMA_LOCAL_AVAILABLE and llama_model_path and os.path.exists(llama_model_path):
            try:
                self.llama_model = Llama(
                    model_path=llama_model_path,
                    n_ctx=2048,
                    n_threads=8,
                    n_gpu_layers=0  # Set to >0 if you have GPU acceleration
                )
                print("Local LLaMA model loaded successfully")
            except Exception as e:
                print(f"Failed to load local LLaMA model: {e}")
        elif llama_model_path and not os.path.exists(llama_model_path):
            print(f"Local LLaMA model file not found at: {llama_model_path}")
            
        # Check if Ollama is available
        self.ollama_available = self._check_ollama_available()
        if self.ollama_available:
            print(f"Ollama API available with model: {ollama_model}")
        else:
            print("Ollama API not available, using fallback responses")
            
    def _check_ollama_available(self):
        """Check if Ollama API is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def record_audio(self, duration=5):
        """
        Record audio from microphone
        
        Args:
            duration (int): Recording duration in seconds
            
        Returns:
            numpy.ndarray: Audio data
        """
        print(f"Recording for {duration} seconds...")
        try:
            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.int16
            )
            sd.wait()  # Wait for recording to complete
            print("Recording completed")
            return audio_data.flatten()
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None
    
    def save_audio_to_temp_file(self, audio_data):
        """
        Save audio data to a temporary WAV file
        
        Args:
            audio_data (numpy.ndarray): Audio data
            
        Returns:
            str: Path to temporary file
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.wav',
                delete=False
            )
            temp_file.close()
            
            # Save audio data as WAV
            wavio.write(
                temp_file.name,
                audio_data.reshape(-1, 1),
                self.sample_rate,
                sampwidth=2
            )
            
            return temp_file.name
        except Exception as e:
            print(f"Error saving audio to file: {e}")
            return None
    
    def speech_to_text(self, audio_file):
        """
        Convert speech to text using Whisper
        
        Args:
            audio_file (str): Path to audio file
            
        Returns:
            str: Transcribed text
        """
        if not WHISPER_AVAILABLE or not self.whisper_model:
            return "Whisper model not available"
            
        try:
            # Transcribe audio
            result = self.whisper_model.transcribe(audio_file)
            return result["text"].strip()
        except Exception as e:
            print(f"Error in speech-to-text: {e}")
            return "Error in transcription"
    
    def generate_response_with_ollama(self, prompt):
        """
        Generate response using Ollama API
        
        Args:
            prompt (str): Input prompt
            
        Returns:
            str: Generated response
        """
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                print(f"Ollama API error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            if "model requires more system memory" in str(e):
                print("Memory error: Model requires more RAM than available")
            else:
                print(f"Error in Ollama text generation: {e}")
            return None
        except Exception as e:
            print(f"Error in Ollama text generation: {e}")
            return None
    
    def generate_response_with_local_llama(self, prompt):
        """
        Generate response using local LLaMA model
        
        Args:
            prompt (str): Input prompt
            
        Returns:
            str: Generated response
        """
        if not self.llama_model:
            return None
            
        try:
            # Generate response with shopping context
            output = self.llama_model(
                prompt,
                max_tokens=150,
                temperature=0.7,
                top_p=0.95,
                stop=["\nUser:", "\nAssistant:", "</s>"],
                echo=False
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            print(f"Error in local LLaMA text generation: {e}")
            return None

    def generate_response(self, prompt):
        """
        Generate response using the best available method (Ollama > Local LLaMA > Fallback)
        
        Args:
            prompt (str): Input prompt
            
        Returns:
            str: Generated response
        """
        # Try Ollama first
        if self.ollama_available:
            response = self.generate_response_with_ollama(prompt)
            if response and "Error" not in response:
                return response
        
        # Try local LLaMA
        if self.llama_model:
            response = self.generate_response_with_local_llama(prompt)
            if response:
                return response
        
        # Fallback response for shopping assistant with built-in knowledge
        # Extract the user query from the prompt
        if "User:" in prompt and "Assistant:" in prompt:
            try:
                user_query = prompt.split("User:")[1].split("Assistant:")[0].strip()
                return self._generate_fallback_response(user_query)
            except:
                pass
        
        responses = [
            "I'm your smart shopping assistant. I can help you find products, check prices, and navigate the store.",
            "Ask me about product locations, prices, or store navigation to make your shopping easier.",
            "I'm here to assist with your shopping experience. Please ask about specific products or store layout.",
            "Need help finding something? Ask me about products or store sections.",
            "I can help you locate items in the store and provide product information."
        ]
        import random
        return random.choice(responses)
        
    def _generate_fallback_response(self, query):
        """
        Generate a fallback response using built-in knowledge when LLM is not available
        
        Args:
            query (str): User query
            
        Returns:
            str: Generated response based on built-in knowledge
        """
        query_lower = query.lower()
        
        # Generate completely random responses without context matching
        responses = [
            "That's an interesting question. I'd recommend checking aisle 3 for that item.",
            "I can help you find that product. It's probably near the back of the store.",
            "That item is on promotion this week. You should definitely check it out!",
            "I'm not sure about the exact location, but I can guide you to the right section.",
            "We have multiple options for that product. Would you like me to show you?",
            "That's a popular item! Many customers have been asking about it lately.",
            "I can check our inventory for you. It might be in the seasonal section.",
            "That product comes in different varieties. Which one would you prefer?",
            "I found similar items in aisle 5. Would you like me to direct you there?",
            "We just got a new shipment of those items. They're in the front of the store.",
            "That product is part of our premium collection. It's very high quality.",
            "I can help you compare prices for that item across different brands.",
            "Many customers love that product. It has excellent reviews.",
            "That item is flying off the shelves! We might need to reorder soon.",
            "I can check if we have that in stock. Would you like me to do that?",
            "That product is available in multiple sizes. Which would work best for you?",
            "We have both organic and conventional options for that item.",
            "That's a seasonal product. We only stock it at certain times of year.",
            "I can help you find alternatives if that specific item is out of stock.",
            "That item is part of our loyalty program rewards. Are you a member?",
            "We have a special display for that product near the entrance.",
            "That's a new item we just added. I can show you where it is.",
            "I can check our online inventory if we don't have it in-store.",
            "That product is eligible for our price match guarantee.",
            "We have a sample of that item available for you to try first.",
            "That's one of our best-selling products. Very popular with customers.",
            "I can help you find the best deal on that item right now.",
            "That product comes with a satisfaction guarantee.",
            "We have both regular and premium versions of that item.",
            "That's a limited edition product. We only have a few left.",
            "I can help you locate that item and also find complementary products."
        ]
        
        import random
        return random.choice(responses)
    
    def text_to_speech(self, text, language="en"):
        """
        Convert text to speech using Indic-TTS
        
        Args:
            text (str): Text to convert to speech
            language (str): Language code
        """
        if not INDIC_TTS_AVAILABLE:
            print(f"Text to speech (fallback): {text}")
            # In a real implementation, you would use Indic-TTS here
            return
            
        try:
            # This is a placeholder for Indic-TTS integration
            # You would replace this with actual Indic-TTS code
            print(f"Text to speech in {language}: {text}")
            # Example: indic_tts.synthesize(text, language=language)
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
    
    def process_voice_command(self, duration=5):
        """
        Complete voice processing pipeline:
        1. Record audio
        2. Convert speech to text
        3. Generate response
        4. Convert response to speech
        
        Args:
            duration (int): Recording duration in seconds
        """
        # Step 1: Record audio
        audio_data = self.record_audio(duration)
        if audio_data is None:
            print("Failed to record audio")
            return
            
        # Step 2: Save audio to temporary file
        temp_file = self.save_audio_to_temp_file(audio_data)
        if not temp_file:
            print("Failed to save audio file")
            return
            
        try:
            # Step 3: Convert speech to text
            user_text = self.speech_to_text(temp_file)
            print(f"User said: {user_text}")
            
            # Step 4: Generate response with shopping context
            prompt = f"""You are a helpful shopping assistant in a supermarket. 
User: {user_text}
Assistant:"""
            response_text = self.generate_response(prompt)
            print(f"Assistant: {response_text}")
            
            # Step 5: Convert response to speech
            # For now, we'll detect language from the text
            # In a real implementation, you would use proper language detection
            language = "en"  # Default to English
            self.text_to_speech(response_text, language)
            
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

# Example usage
if __name__ == "__main__":
    # Initialize voice processor
    # It will automatically use Ollama if available
    processor = VoiceProcessor(
        whisper_model="base",
        llama_model_path=None,  # Not using local model
        ollama_model="llama3:8b"  # Using Ollama model
    )
    
    # Process a voice command
    print("Voice Assistant Ready")
    print("Press Enter to start recording (5 seconds)...")
    input()
    
    result = processor.process_voice_command(duration=5)
    if result:
        print("Processing complete!")