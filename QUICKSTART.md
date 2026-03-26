# Quick Start Guide

Get your Gemini Voice Agent up and running in 3 minutes!

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Modern web browser (Chrome, Firefox, Edge, or Safari)
- [ ] Microphone connected and working
- [ ] Google API key ready

## Step 1: Get Your Google API Key (2 minutes)

1. Visit https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

## Step 2: Setup (1 minute)

### On Linux/Mac:

```bash
# Clone and enter directory
cd Two_step_gemini_agent

# Run the startup script
./start.sh
```

### On Windows:

```batch
# Double-click start.bat
# Or run from command prompt:
start.bat
```

### Manual Setup:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env

# 3. Edit .env and add your API key
# GOOGLE_API_KEY=your_actual_api_key_here

# 4. Start the server
cd backend
python main.py
```

## Step 3: Use the App

1. Open browser: http://localhost:8000
2. Allow microphone access when prompted
3. Click and hold the microphone button
4. Speak your message
5. Release the button
6. Listen to the agent's response!

## Troubleshooting

### "GOOGLE_API_KEY not set" error
- Make sure you created the `.env` file
- Verify the API key is on the correct line: `GOOGLE_API_KEY=your_key_here`
- No quotes needed around the API key

### "Cannot access microphone"
- Grant microphone permissions in your browser
- Check if another app is using your microphone
- Try a different browser

### "Connection failed"
- Make sure the backend server is running
- Check if port 8000 is available
- Verify no firewall is blocking the connection

### Audio doesn't play
- Check your speaker/audio output
- Try refreshing the browser page
- Check browser console for errors (F12)

## Next Steps

- Check out the full README.md for advanced configuration
- Customize the UI in `frontend/style.css`
- Adjust VAD sensitivity in `backend/vad.py`
- Add MCP server integration for tool calling

## Tips for Best Experience

1. **Speak clearly**: Pause before and after your message
2. **Good microphone**: Use a decent quality microphone
3. **Quiet environment**: Reduce background noise
4. **Stable internet**: Ensure good connection for API calls
5. **Hold button**: Keep holding until you finish speaking

## Common Use Cases

- **Voice assistant**: Ask questions and get spoken answers
- **Transcription**: Convert speech to text quickly
- **Accessibility**: Hands-free interaction with AI
- **Practice conversations**: Language learning or interview prep
- **Quick notes**: Dictate ideas and get them processed

## Getting Help

- Read the full documentation in README.md
- Check the troubleshooting section above
- Look at browser console for error messages
- Verify your Google API key has the right permissions

---

**Ready to talk to your AI agent? Let's go! 🎤**
