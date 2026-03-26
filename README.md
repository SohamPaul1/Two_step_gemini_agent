# Gemini Voice Agent

A real-time voice conversation agent powered by Google's Gemini 2.0 Flash model with audio-to-text, text-to-speech, and tool calling capabilities.

## Features

- 🎤 **Real-time Voice Interaction**: Push-to-talk interface for seamless voice conversations
- 🔊 **Low-latency Audio**: Fast audio processing and playback with minimal delay
- 🎯 **Voice Activity Detection**: RNNoise-based VAD for detecting speech start/end
- 🛑 **Barge-in Support**: Interrupt the agent at any time during playback
- 🔧 **MCP Tool Calling**: Integration with Model Context Protocol servers for tool usage
- 🎨 **Modern UI**: Clean, responsive interface with audio visualization
- ⚡ **WebSocket Communication**: Efficient real-time bidirectional communication

## Architecture

### Frontend (HTML/CSS/JS)
- Pure vanilla JavaScript, no frameworks required
- WebSocket client for real-time communication
- MediaRecorder API for audio capture
- Web Audio API for playback and visualization
- Push-to-talk interface with visual feedback

### Backend (Python/FastAPI)
- FastAPI server with WebSocket support
- Google Gemini API integration for audio processing
- Google Cloud TTS for speech synthesis
- Voice Activity Detection (VAD) module
- MCP client for tool calling

## Workflow

1. **User visits website** → Click microphone button
2. **User starts speaking** → VAD triggers (speech detected)
3. **Audio collection** → Bytes collected in real-time
4. **User stops speaking** → VAD triggers (speech ended)
5. **Audio sent to Gemini** → Model processes and generates response
6. **Tool calling** (if needed) → MCP server integration
7. **TTS conversion** → Text converted to speech
8. **Audio playback** → Response played to user
9. **Barge-in support** → User can interrupt at any time

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Google Cloud API key with Gemini and TTS access
- Modern web browser with microphone access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Two_step_gemini_agent
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```bash
   GOOGLE_API_KEY=your_google_api_key_here
   ```

   To get a Google API key:
   - Visit https://makersuite.google.com/app/apikey
   - Create a new API key
   - Enable Gemini API and Cloud Text-to-Speech API

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   python main.py
   ```

   The server will start on `http://localhost:8000`

2. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

3. **Grant microphone permissions**
   When prompted, allow microphone access for the application to work.

### Using the Application

1. **Connect**: The app automatically connects to the WebSocket server
2. **Start conversation**: Click and hold the microphone button
3. **Speak**: Talk while holding the button
4. **Release**: Release the button when done speaking
5. **Listen**: Wait for the agent's response
6. **Interrupt**: Click the "Stop" button to interrupt playback

## Project Structure

```
Two_step_gemini_agent/
├── backend/
│   ├── main.py              # FastAPI server and WebSocket handler
│   ├── vad.py               # Voice Activity Detection module
│   └── mcp_client.py        # MCP server integration
├── frontend/
│   ├── index.html           # Main HTML interface
│   ├── style.css            # Styling and animations
│   └── app.js               # Frontend application logic
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

### Backend Configuration

Edit `backend/main.py` to customize:

- **Model selection**: Change `gemini-2.0-flash-exp` to another Gemini model
- **Generation config**: Adjust temperature, max_output_tokens
- **Safety settings**: Modify content filtering levels
- **Port**: Change the port in `uvicorn.run()`

### Frontend Configuration

Edit `frontend/app.js` to customize:

- **Audio settings**: Modify sample rate, bit rate
- **Recording mode**: Change from push-to-talk to continuous
- **Visualization**: Customize the audio visualizer appearance

### VAD Configuration

Edit `backend/vad.py` to adjust:

- **Threshold**: Sensitivity for voice detection
- **Frame size**: Audio processing chunk size
- **Speech/Silence frames**: Trigger sensitivity

## MCP Server Integration

To add MCP server support:

1. **Configure MCP server URL** in your environment:
   ```bash
   MCP_SERVER_URL=http://your-mcp-server-url
   ```

2. **Update backend/main.py** to use the MCP client:
   ```python
   from mcp_client import MCPManager

   mcp_manager = MCPManager()
   mcp_manager.add_server("default", os.getenv("MCP_SERVER_URL"))
   ```

3. **Tool calls** will be automatically processed when Gemini requests them

## Troubleshooting

### Microphone not working
- Check browser permissions
- Ensure HTTPS connection (required for microphone access in production)
- Try a different browser

### Connection errors
- Verify the backend server is running
- Check firewall settings
- Ensure WebSocket port is not blocked

### Audio quality issues
- Adjust sample rate in the frontend
- Check network connection quality
- Ensure sufficient bandwidth for audio streaming

### API errors
- Verify your Google API key is valid
- Check API quotas and limits
- Ensure required APIs are enabled in Google Cloud Console

## Development

### Running in Development Mode

For development with auto-reload:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing WebSocket Connection

You can test the WebSocket connection using a tool like `wscat`:

```bash
npm install -g wscat
wscat -c ws://localhost:8000/ws/test_client
```

## Security Considerations

- **API Keys**: Never commit API keys to version control
- **HTTPS**: Use HTTPS in production for secure WebSocket connections
- **Input Validation**: Audio data is validated before processing
- **Rate Limiting**: Consider adding rate limiting for production use
- **CORS**: Configure CORS settings for production deployment

## Performance Optimization

- **Audio Compression**: WebM/Opus provides good compression
- **Streaming**: Audio is processed in chunks for lower latency
- **Caching**: Consider caching TTS responses for common phrases
- **Connection Pooling**: Reuse HTTP connections for API calls

## Browser Compatibility

Tested and supported on:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

## Known Limitations

- Push-to-talk mode only (continuous mode not yet implemented)
- Single conversation per client (no multi-user support yet)
- Audio format limited to WebM/WAV
- No conversation history persistence

## Future Enhancements

- [ ] Continuous conversation mode with automatic VAD
- [ ] Multi-language support
- [ ] Conversation history and replay
- [ ] Custom wake word detection
- [ ] Speaker identification
- [ ] Audio recording export
- [ ] Mobile app version

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

## Credits

- Google Gemini API
- Google Cloud Text-to-Speech
- FastAPI framework
- RNNoise VAD algorithm
