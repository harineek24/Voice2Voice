import os
import time
import uuid
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Ensure .env is loaded before accessing variables
if not load_dotenv():
    logger.error(".env file not found")
    raise FileNotFoundError(".env file not found in project root")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in .env file")
    raise ValueError("OPENAI_API_KEY not found in .env file")

# Ephemeral key settings
KEY_EXPIRY = 300  # 5 minutes in seconds

# In-memory storage for ephemeral keys
ephemeral_keys = {}

def create_ephemeral_key() -> dict:
    """
    Create a temporary key that expires after KEY_EXPIRY seconds
    """
    key = str(uuid.uuid4())
    expiry = time.time() + KEY_EXPIRY
    ephemeral_keys[key] = {
        "expiry": expiry
    }
    return {"key": key, "expires_in": KEY_EXPIRY}

def validate_ephemeral_key(key: str) -> bool:
    """
    Validate if the ephemeral key is valid and not expired
    """
    if key not in ephemeral_keys:
        return False
    
    key_data = ephemeral_keys[key]
    
    # Check if key has expired
    if time.time() > key_data["expiry"]:
        # Remove expired key
        ephemeral_keys.pop(key)
        return False
    
    return True

def get_openai_api_key() -> str:
    """
    Get the OpenAI API key
    """
    return OPENAI_API_KEY