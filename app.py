from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import tempfile
import uuid
import uvicorn
import logging
from dotenv import load_dotenv
from key_manager import create_ephemeral_key, validate_ephemeral_key, get_openai_api_key
import openai


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    openai.api_key = get_openai_api_key()
    logger.info("OpenAI API key set successfully")
except Exception as e:
    logger.error(f"Failed to set OpenAI API key: {e}")
    raise
# Create storage directory for audio files
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_responses")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Create FastAPI app
app = FastAPI(title="Voice Assistant API")

app = FastAPI(title="Voice Assistant API")

# 1) serve index.html at /
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(os.path.join("static", "index.html"))

# 2) mount all other static assets under /static
app.mount("/static", StaticFiles(directory="static"), name="static")
# Mount static files for frontend


@app.get("/api/key")
async def get_key():
    """Get an ephemeral API key"""
    return create_ephemeral_key()

@app.post("/api/process-voice")
async def process_voice(
    audio: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    """Process voice: speech-to-text → AI response → text-to-speech"""
    # Validate ephemeral key
    if not validate_ephemeral_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid or expired API key")
    
    try:
        # Save uploaded audio temporarily
        temp_audio_path = f"{tempfile.gettempdir()}/{uuid.uuid4()}.webm"
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())
        
        # Step 1: Transcribe audio to text
        with open(temp_audio_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
        
        user_text = transcript.text
        logger.info(f"Transcribed: {user_text}")
        
        # Step 2: Generate AI response
        chat_completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Keep responses brief and conversational."},
                {"role": "user", "content": user_text}
            ]
        )
        
        response_text = chat_completion.choices[0].message.content
        logger.info(f"AI response: {response_text}")
        
        # Step 3: Convert response to speech
        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)
        
        speech_response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=response_text
        )
        
        # Save the audio response
        speech_response.stream_to_file(output_path)
        
        # Clean up temp file
        os.remove(temp_audio_path)
        
        # Return response with text and audio URL
        return {
            "text": response_text,
            "audio_url": f"/audio/{filename}"
        }
    
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing voice: {str(e)}")

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve audio files"""
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(file_path, media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)