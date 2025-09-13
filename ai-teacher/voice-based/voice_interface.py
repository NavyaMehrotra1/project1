"""
Voice Interface for AI Teacher
Handles speech-to-text and text-to-speech conversion
"""

import whisper
import pyaudio
import wave
import numpy as np
import threading
import queue
import time
from typing import Optional, Callable
import webrtcvad
import collections
import contextlib
import sys
import os

class VoiceInterface:
    """Handles voice input/output for the AI teacher"""
    
    def __init__(self, 
                 model_size: str = "base",
                 sample_rate: int = 16000,
                 chunk_duration_ms: int = 30,
                 padding_duration_ms: int = 300,
                 vad_aggressiveness: int = 3):
        
        # Whisper setup
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model(model_size)
        
        # Audio settings
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.padding_duration_ms = padding_duration_ms
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        self.padding_size = int(sample_rate * padding_duration_ms / 1000)
        
        # VAD (Voice Activity Detection)
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        
        # Audio recording
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.audio_queue = queue.Queue()
        
        # Callbacks
        self.on_speech_detected: Optional[Callable[[str], None]] = None
        self.on_silence_detected: Optional[Callable[[], None]] = None
        
    def start_listening(self):
        """Start continuous voice listening"""
        if self.is_recording:
            return
            
        self.is_recording = True
        
        # Start audio recording thread
        recording_thread = threading.Thread(target=self._record_audio)
        recording_thread.daemon = True
        recording_thread.start()
        
        # Start speech processing thread
        processing_thread = threading.Thread(target=self._process_audio)
        processing_thread.daemon = True
        processing_thread.start()
        
        print("🎤 Voice interface started. Listening for speech...")
    
    def stop_listening(self):
        """Stop voice listening"""
        self.is_recording = False
        print("🔇 Voice interface stopped.")
    
    def _record_audio(self):
        """Record audio in chunks"""
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while self.is_recording:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    self.audio_queue.put(data)
                except Exception as e:
                    print(f"Error recording audio: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Error setting up audio stream: {e}")
    
    def _process_audio(self):
        """Process audio chunks for voice activity detection"""
        ring_buffer = collections.deque(maxlen=self.padding_size // self.chunk_size)
        triggered = False
        voiced_frames = []
        
        while self.is_recording:
            try:
                if self.audio_queue.empty():
                    time.sleep(0.01)
                    continue
                    
                chunk = self.audio_queue.get_nowait()
                
                # Convert to numpy array for VAD
                audio_data = np.frombuffer(chunk, dtype=np.int16)
                
                # Check if chunk contains speech
                is_speech = self.vad.is_speech(chunk, self.sample_rate)
                
                if not triggered:
                    ring_buffer.append((chunk, is_speech))
                    num_voiced = len([f for f, speech in ring_buffer if speech])
                    
                    # Start recording if we detect speech
                    if num_voiced > 0.9 * ring_buffer.maxlen:
                        triggered = True
                        voiced_frames.extend([f for f, s in ring_buffer])
                        ring_buffer.clear()
                        print("🗣️  Speech detected, recording...")
                else:
                    voiced_frames.append(chunk)
                    ring_buffer.append((chunk, is_speech))
                    num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                    
                    # Stop recording if silence detected
                    if num_unvoiced > 0.9 * ring_buffer.maxlen:
                        triggered = False
                        
                        # Process the recorded speech
                        if voiced_frames:
                            self._transcribe_audio(voiced_frames)
                        
                        voiced_frames = []
                        ring_buffer.clear()
                        
                        if self.on_silence_detected:
                            self.on_silence_detected()
                            
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
    
    def _transcribe_audio(self, audio_frames):
        """Transcribe audio frames to text"""
        try:
            # Combine audio frames
            audio_data = b''.join(audio_frames)
            
            # Convert to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(audio_np, language='en')
            text = result['text'].strip()
            
            if text and len(text) > 1:
                print(f"📝 Transcribed: {text}")
                
                if self.on_speech_detected:
                    self.on_speech_detected(text)
                    
        except Exception as e:
            print(f"Error transcribing audio: {e}")
    
    def record_single_utterance(self, timeout: float = 10.0) -> Optional[str]:
        """Record a single utterance and return transcription"""
        print("🎤 Speak now...")
        
        # Record audio for specified duration or until silence
        frames = []
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        start_time = time.time()
        silence_count = 0
        max_silence = int(2.0 * self.sample_rate / self.chunk_size)  # 2 seconds of silence
        
        try:
            while time.time() - start_time < timeout:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Check for silence
                audio_data = np.frombuffer(data, dtype=np.int16)
                if np.max(np.abs(audio_data)) < 500:  # Silence threshold
                    silence_count += 1
                    if silence_count > max_silence and len(frames) > 10:
                        break
                else:
                    silence_count = 0
            
            stream.stop_stream()
            stream.close()
            
            # Transcribe
            if frames:
                audio_data = b''.join(frames)
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                result = self.whisper_model.transcribe(audio_np, language='en')
                text = result['text'].strip()
                
                if text:
                    print(f"📝 You said: {text}")
                    return text
                    
        except Exception as e:
            print(f"Error recording: {e}")
            
        return None
    
    def speak_text(self, text: str):
        """Convert text to speech (placeholder - requires TTS implementation)"""
        print(f"🔊 AI Teacher: {text}")
        
        # For now, just print. In a full implementation, you would use:
        # - macOS: `say` command
        # - Windows: SAPI
        # - Cross-platform: pyttsx3, gTTS, or cloud TTS services
        
        # Simple macOS implementation:
        if sys.platform == "darwin":
            os.system(f'say "{text}"')
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
        if hasattr(self, 'audio'):
            self.audio.terminate()
