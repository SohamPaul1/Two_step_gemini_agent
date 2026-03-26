import asyncio
import json
import os
import base64
from typing import Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import httpx

app = FastAPI()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=GOOGLE_API_KEY)

# Model configuration
model = genai.GenerativeModel(
    "gemini-2.0-flash-exp",
    generation_config={
        "temperature": 0.7,
        "max_output_tokens": 2048,
    },
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversation_history: Dict[str, list] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.conversation_history[client_id] = []

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.conversation_history:
            del self.conversation_history[client_id]

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)


manager = ConnectionManager()


async def process_audio_with_gemini(audio_data: bytes, client_id: str) -> str:
    """Process audio through Gemini for transcription and response"""
    try:
        # Convert audio bytes to base64
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')

        # Create the prompt with audio
        prompt = "Transcribe and respond to this audio message naturally. If you need to use any tools, do so."

        # Use Gemini's audio processing
        response = model.generate_content([
            {
                "mime_type": "audio/wav",
                "data": audio_b64
            },
            prompt
        ])

        return response.text
    except Exception as e:
        print(f"Error processing audio with Gemini: {e}")
        return f"Sorry, I encountered an error: {str(e)}"


async def text_to_speech_gemini(text: str) -> bytes:
    """Convert text to speech using Google Cloud TTS"""
    try:
        # Using Google Cloud TTS API
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_API_KEY
        }

        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": "en-US",
                "name": "en-US-Neural2-C",
                "ssmlGender": "FEMALE"
            },
            "audioConfig": {
                "audioEncoding": "LINEAR16",
                "sampleRateHertz": 24000,
                "pitch": 0,
                "speakingRate": 1.0
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)

            if response.status_code == 200:
                result = response.json()
                audio_content = base64.b64decode(result["audioContent"])
                return audio_content
            else:
                print(f"TTS Error: {response.status_code} - {response.text}")
                return b""
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return b""


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    print(f"Client {client_id} connected")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive()

            if "bytes" in data:
                # Audio data received
                audio_data = data["bytes"]

                # Send acknowledgment
                await manager.send_message({
                    "type": "audio_received",
                    "status": "processing"
                }, client_id)

                # Process audio with Gemini
                response_text = await process_audio_with_gemini(audio_data, client_id)

                # Send text response
                await manager.send_message({
                    "type": "text_response",
                    "text": response_text
                }, client_id)

                # Convert response to speech
                audio_response = await text_to_speech_gemini(response_text)

                if audio_response:
                    # Send audio response
                    await manager.send_message({
                        "type": "audio_response",
                        "audio": base64.b64encode(audio_response).decode('utf-8')
                    }, client_id)

            elif "text" in data:
                # Handle text messages (for commands like stop/interrupt)
                message = json.loads(data["text"])

                if message.get("type") == "interrupt":
                    # Handle barge-in/interruption
                    await manager.send_message({
                        "type": "interrupted",
                        "status": "ready"
                    }, client_id)

                elif message.get("type") == "ping":
                    # Keep-alive
                    await manager.send_message({
                        "type": "pong"
                    }, client_id)

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
        manager.disconnect(client_id)
    except Exception as e:
        print(f"Error in websocket: {e}")
        manager.disconnect(client_id)


# Serve static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.get("/")
async def get_index():
    with open("../frontend/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
