// Gemini Voice Agent - Frontend Application

class VoiceAgent {
    constructor() {
        this.ws = null;
        this.clientId = this.generateClientId();
        this.isConnected = false;
        this.isRecording = false;
        this.isPlaying = false;
        this.mediaRecorder = null;
        this.audioContext = null;
        this.analyser = null;
        this.audioChunks = [];
        this.visualizer = null;

        this.initializeUI();
        this.initializeAudio();
        this.connect();
    }

    generateClientId() {
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }

    initializeUI() {
        this.elements = {
            statusIndicator: document.getElementById('status-indicator'),
            statusText: document.getElementById('status-text'),
            connectionId: document.getElementById('connection-id'),
            micButton: document.getElementById('mic-button'),
            interruptButton: document.getElementById('interrupt-button'),
            transcript: document.getElementById('transcript'),
            vadStatus: document.getElementById('vad-status'),
            levelFill: document.getElementById('level-fill'),
            canvas: document.getElementById('audio-visualizer')
        };

        // Set connection ID
        this.elements.connectionId.textContent = `ID: ${this.clientId}`;

        // Event listeners
        this.elements.micButton.addEventListener('mousedown', () => this.startRecording());
        this.elements.micButton.addEventListener('mouseup', () => this.stopRecording());
        this.elements.micButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        this.elements.micButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        this.elements.interruptButton.addEventListener('click', () => this.interrupt());

        // Initialize visualizer
        this.visualizer = new AudioVisualizer(this.elements.canvas);
    }

    async initializeAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 48000
                }
            });

            // Set up analyser for visualization
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 2048;
            const source = this.audioContext.createMediaStreamSource(stream);
            source.connect(this.analyser);

            // Start visualization
            this.visualize();

            // Set up MediaRecorder
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus',
                audioBitsPerSecond: 128000
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.sendAudio();
            };

            console.log('Audio initialized successfully');
        } catch (error) {
            console.error('Error initializing audio:', error);
            this.addMessage('system', 'Error: Could not access microphone. Please grant permission.');
        }
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('Connected to server');
            this.isConnected = true;
            this.updateStatus('connected', 'Connected');
            this.elements.micButton.disabled = false;
            this.addMessage('system', 'Connected! Click and hold the microphone to start speaking.');
        };

        this.ws.onclose = () => {
            console.log('Disconnected from server');
            this.isConnected = false;
            this.updateStatus('disconnected', 'Disconnected');
            this.elements.micButton.disabled = true;
            this.addMessage('system', 'Disconnected from server. Reconnecting...');

            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connect(), 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.addMessage('system', 'Connection error occurred.');
        };

        this.ws.onmessage = (event) => {
            this.handleMessage(JSON.parse(event.data));
        };
    }

    handleMessage(message) {
        console.log('Received message:', message.type);

        switch (message.type) {
            case 'audio_received':
                this.addMessage('system', 'Processing your audio...');
                break;

            case 'text_response':
                this.addMessage('agent', message.text);
                break;

            case 'audio_response':
                this.playAudioResponse(message.audio);
                break;

            case 'interrupted':
                this.addMessage('system', 'Playback interrupted. Ready for your input.');
                this.isPlaying = false;
                this.elements.interruptButton.disabled = true;
                break;

            case 'pong':
                // Keep-alive response
                break;

            default:
                console.log('Unknown message type:', message.type);
        }
    }

    async startRecording() {
        if (!this.isConnected || this.isRecording) return;

        try {
            this.isRecording = true;
            this.audioChunks = [];

            this.elements.micButton.classList.add('recording');
            this.elements.micButton.querySelector('.mic-text').textContent = 'Recording...';
            this.updateStatus('speaking', 'Recording');
            this.updateVAD(true);

            this.mediaRecorder.start(100); // Capture in 100ms chunks

            this.addMessage('user', '🎤 Speaking...');
        } catch (error) {
            console.error('Error starting recording:', error);
            this.isRecording = false;
        }
    }

    stopRecording() {
        if (!this.isRecording) return;

        this.isRecording = false;
        this.mediaRecorder.stop();

        this.elements.micButton.classList.remove('recording');
        this.elements.micButton.querySelector('.mic-text').textContent = 'Click to Start';
        this.updateStatus('connected', 'Connected');
        this.updateVAD(false);
    }

    async sendAudio() {
        if (this.audioChunks.length === 0) {
            console.log('No audio data to send');
            return;
        }

        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });

            // Convert to WAV format
            const arrayBuffer = await audioBlob.arrayBuffer();

            // Send via WebSocket
            this.ws.send(arrayBuffer);

            console.log('Audio sent, size:', arrayBuffer.byteLength);
            this.addMessage('user', 'Audio sent. Waiting for response...');
        } catch (error) {
            console.error('Error sending audio:', error);
            this.addMessage('system', 'Error sending audio. Please try again.');
        }
    }

    async playAudioResponse(audioBase64) {
        try {
            // Decode base64 audio
            const audioData = atob(audioBase64);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(arrayBuffer);
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }

            // Decode and play audio
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.audioContext.destination);

            this.isPlaying = true;
            this.elements.interruptButton.disabled = false;
            this.addMessage('system', '🔊 Playing response...');

            source.onended = () => {
                this.isPlaying = false;
                this.elements.interruptButton.disabled = true;
                this.addMessage('system', 'Ready for your input.');
            };

            source.start(0);
        } catch (error) {
            console.error('Error playing audio:', error);
            this.addMessage('system', 'Error playing audio response.');
            this.isPlaying = false;
            this.elements.interruptButton.disabled = true;
        }
    }

    interrupt() {
        if (!this.isPlaying) return;

        // Stop any playing audio
        if (this.audioContext) {
            this.audioContext.suspend();
            setTimeout(() => this.audioContext.resume(), 100);
        }

        // Send interrupt message to server
        this.ws.send(JSON.stringify({ type: 'interrupt' }));

        this.isPlaying = false;
        this.elements.interruptButton.disabled = true;
        this.addMessage('user', '⏹️ Interrupted');
    }

    visualize() {
        const draw = () => {
            requestAnimationFrame(draw);

            if (!this.analyser) return;

            const bufferLength = this.analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            this.analyser.getByteTimeDomainData(dataArray);

            // Update visualizer
            this.visualizer.draw(dataArray);

            // Update audio level
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                const value = (dataArray[i] - 128) / 128;
                sum += value * value;
            }
            const rms = Math.sqrt(sum / bufferLength);
            const level = Math.min(100, rms * 200);
            this.elements.levelFill.style.width = `${level}%`;
        };

        draw();
    }

    updateStatus(status, text) {
        this.elements.statusIndicator.className = `status-indicator ${status}`;
        this.elements.statusText.textContent = text;
    }

    updateVAD(active) {
        const vadStatus = this.elements.vadStatus;
        if (active) {
            vadStatus.textContent = 'Active';
            vadStatus.classList.add('active');
        } else {
            vadStatus.textContent = 'Inactive';
            vadStatus.classList.remove('active');
        }
    }

    addMessage(type, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const label = document.createElement('span');
        label.className = 'message-label';
        label.textContent = type === 'user' ? 'You:' : type === 'agent' ? 'Agent:' : 'System:';

        const messageText = document.createElement('span');
        messageText.className = 'message-text';
        messageText.textContent = text;

        messageDiv.appendChild(label);
        messageDiv.appendChild(messageText);

        this.elements.transcript.appendChild(messageDiv);
        this.elements.transcript.scrollTop = this.elements.transcript.scrollHeight;
    }
}

class AudioVisualizer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }

    draw(dataArray) {
        const width = this.canvas.width;
        const height = this.canvas.height;
        const ctx = this.ctx;

        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(0, 0, width, height);

        ctx.lineWidth = 2;
        ctx.strokeStyle = '#667eea';
        ctx.beginPath();

        const sliceWidth = width / dataArray.length;
        let x = 0;

        for (let i = 0; i < dataArray.length; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * height / 2;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        ctx.lineTo(width, height / 2);
        ctx.stroke();
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new VoiceAgent();
});
