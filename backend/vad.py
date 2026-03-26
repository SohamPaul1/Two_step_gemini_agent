import numpy as np
import struct
import subprocess
import os
from typing import Optional


class RNNoiseVAD:
    """Voice Activity Detection using RNNoise"""

    def __init__(self, threshold: float = 0.5, frame_size: int = 480):
        """
        Initialize RNNoise VAD

        Args:
            threshold: VAD threshold (0.0 - 1.0)
            frame_size: Frame size in samples (default 480 for 10ms at 48kHz)
        """
        self.threshold = threshold
        self.frame_size = frame_size
        self.sample_rate = 48000
        self.is_speaking = False
        self.speech_frames = 0
        self.silence_frames = 0
        self.speech_threshold = 3  # consecutive frames to trigger speech
        self.silence_threshold = 10  # consecutive frames to trigger silence

        # Energy-based VAD as fallback
        self.energy_threshold = 0.01

    def process_frame(self, audio_frame: bytes) -> bool:
        """
        Process an audio frame and detect voice activity

        Args:
            audio_frame: Audio data as bytes (16-bit PCM)

        Returns:
            True if voice activity detected, False otherwise
        """
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_frame, dtype=np.int16)

        # Calculate energy-based VAD
        energy = np.sum(audio_array.astype(np.float32) ** 2) / len(audio_array)
        normalized_energy = energy / (32768.0 ** 2)  # Normalize for 16-bit audio

        # Simple energy-based VAD
        is_voice = normalized_energy > self.energy_threshold

        # Update state machine
        if is_voice:
            self.speech_frames += 1
            self.silence_frames = 0
            if self.speech_frames >= self.speech_threshold:
                self.is_speaking = True
        else:
            self.silence_frames += 1
            self.speech_frames = 0
            if self.silence_frames >= self.silence_threshold:
                self.is_speaking = False

        return self.is_speaking

    def reset(self):
        """Reset VAD state"""
        self.is_speaking = False
        self.speech_frames = 0
        self.silence_frames = 0


class AudioProcessor:
    """Process audio streams with VAD"""

    def __init__(self, sample_rate: int = 48000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.vad = RNNoiseVAD()
        self.audio_buffer = bytearray()
        self.recording = False
        self.recorded_audio = bytearray()

    def process_chunk(self, audio_chunk: bytes) -> tuple[bool, Optional[bytes]]:
        """
        Process an audio chunk

        Args:
            audio_chunk: Audio data chunk

        Returns:
            Tuple of (is_speaking, completed_audio)
            completed_audio is not None when speech segment ends
        """
        # Add to buffer
        self.audio_buffer.extend(audio_chunk)

        # Process frames
        frame_bytes = self.vad.frame_size * 2  # 16-bit = 2 bytes per sample

        completed_audio = None

        while len(self.audio_buffer) >= frame_bytes:
            frame = bytes(self.audio_buffer[:frame_bytes])
            self.audio_buffer = self.audio_buffer[frame_bytes:]

            is_speaking = self.vad.process_frame(frame)

            if is_speaking:
                if not self.recording:
                    # Start recording
                    self.recording = True
                    self.recorded_audio = bytearray()
                    print("🎤 Speech started")

                self.recorded_audio.extend(frame)
            else:
                if self.recording:
                    # End recording
                    self.recording = False
                    completed_audio = bytes(self.recorded_audio)
                    self.recorded_audio = bytearray()
                    print("🛑 Speech ended")

        return (is_speaking, completed_audio)

    def reset(self):
        """Reset processor state"""
        self.vad.reset()
        self.audio_buffer = bytearray()
        self.recording = False
        self.recorded_audio = bytearray()


def convert_audio_to_wav(audio_data: bytes, sample_rate: int = 48000, channels: int = 1) -> bytes:
    """
    Convert raw PCM audio to WAV format

    Args:
        audio_data: Raw PCM audio data
        sample_rate: Sample rate in Hz
        channels: Number of audio channels

    Returns:
        WAV formatted audio data
    """
    import io
    import wave

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)

    return wav_buffer.getvalue()
