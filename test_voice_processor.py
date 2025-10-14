"""
Test script for voice processor module
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from voice_processor import VoiceProcessor
    print("VoiceProcessor imported successfully")
    
    # Test initialization
    processor = VoiceProcessor()
    print("VoiceProcessor initialized successfully")
    
    # Test methods
    print("Testing available methods:")
    print("- record_audio:", hasattr(processor, 'record_audio'))
    print("- speech_to_text:", hasattr(processor, 'speech_to_text'))
    print("- generate_response:", hasattr(processor, 'generate_response'))
    print("- text_to_speech:", hasattr(processor, 'text_to_speech'))
    
except ImportError as e:
    print(f"Failed to import VoiceProcessor: {e}")
except Exception as e:
    print(f"Error testing VoiceProcessor: {e}")