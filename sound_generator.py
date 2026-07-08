import numpy as np
import math
import random
from typing import Optional
import io
import wave

class SoundGenerator:
    def __init__(self):
        self.rng = random.Random()
    
    def save_wav(self, samples: np.ndarray, sample_rate: int = 44100) -> bytes:
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            samples_int = (samples * 32767).astype(np.int16)
            wav_file.writeframes(samples_int.tobytes())
        
        return buffer.getvalue()
    
    def generate_vulcan_sound(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.1
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 20.0)
            base_freq = 440.0
            mod_freq = 880.0
            mod_depth = 100.0
            freq = base_freq + math.sin(t * mod_freq * 2 * math.pi) * mod_depth
            wave_val = math.sin(t * freq * 2 * math.pi)
            harmonic = math.sin(t * freq * 2.0 * 2 * math.pi) * 0.3
            samples[i] = (wave_val + harmonic) * env * 0.25
        
        return self.save_wav(samples, sample_rate)
    
    def generate_laser_sound(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.12
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 18.0)
            freq = 3000.0 + (1200.0 - 3000.0) * (t / duration)
            wave_val = math.sin(t * freq * 2 * math.pi)
            bright = math.sin(t * freq * 3.0 * 2 * math.pi) * 0.2
            samples[i] = (wave_val + bright) * env * 0.2
        
        return self.save_wav(samples, sample_rate)
    
    def generate_spread_sound(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.15
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 12.0)
            pulse_phase = (t * 20.0) % 1.0
            pulse_env = math.exp(-pulse_phase * 8.0)
            freq = 600.0
            wave_val = math.sin(t * freq * 2 * math.pi) * pulse_env
            texture = math.sin(t * freq * 1.5 * 2 * math.pi) * 0.3 * pulse_env
            samples[i] = (wave_val + texture) * env * 0.2
        
        return self.save_wav(samples, sample_rate)
    
    def generate_missile_sound(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.25
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 6.0)
            base_freq = 150.0
            wave_val = math.sin(t * base_freq * 2 * math.pi) * 0.4
            noise = self.rng.uniform(-0.3, 0.3) * (1.0 - t / duration)
            sweep_freq = 200.0 + (400.0 - 200.0) * (t / duration)
            sweep = math.sin(t * sweep_freq * 2 * math.pi) * 0.2
            samples[i] = (wave_val + noise + sweep) * env * 0.25
        
        return self.save_wav(samples, sample_rate)
    
    def generate_explosion_small(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.25
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 10.0)
            noise = self.rng.uniform(-1.0, 1.0)
            low = math.sin(t * 100.0 * 2 * math.pi) * 0.5
            samples[i] = (noise * 0.6 + low) * env
        
        return self.save_wav(samples, sample_rate)
    
    def generate_explosion_medium(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.4
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 6.0)
            noise = self.rng.uniform(-1.0, 1.0)
            low = math.sin(t * 60.0 * 2 * math.pi) * 0.7
            mid = math.sin(t * 200.0 * 2 * math.pi) * 0.3 * math.exp(-t * 15.0)
            samples[i] = (noise * 0.5 + low + mid) * env
        
        return self.save_wav(samples, sample_rate)
    
    def generate_explosion_large(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.6
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 4.0)
            noise = self.rng.uniform(-1.0, 1.0)
            low = math.sin(t * 40.0 * 2 * math.pi) * 0.8
            mid = math.sin(t * 120.0 * 2 * math.pi) * 0.4 * math.exp(-t * 8.0)
            samples[i] = (noise * 0.4 + low + mid) * env
        
        return self.save_wav(samples, sample_rate)
    
    def generate_player_death(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.8
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 3.0)
            noise = self.rng.uniform(-1.0, 1.0)
            low = math.sin(t * 30.0 * 2 * math.pi) * 0.9
            mid = math.sin(t * 80.0 * 2 * math.pi) * 0.5 * math.exp(-t * 6.0)
            high = math.sin(t * 300.0 * 2 * math.pi) * 0.3 * math.exp(-t * 12.0)
            samples[i] = (noise * 0.5 + low + mid + high) * env
        
        return self.save_wav(samples, sample_rate)
    
    def generate_ui_click(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.05
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 40.0)
            freq = 800.0
            wave = math.sin(t * freq * 2 * math.pi)
            samples[i] = wave * env * 0.3
        
        return self.save_wav(samples, sample_rate)
    
    def generate_ui_hover(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.08
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 25.0)
            freq = 1200.0
            wave = math.sin(t * freq * 2 * math.pi)
            samples[i] = wave * env * 0.2
        
        return self.save_wav(samples, sample_rate)
    
    def generate_ui_confirm(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.15
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 15.0)
            # Two-tone ascending
            if t < 0.075:
                freq = 600.0
            else:
                freq = 900.0
            wave = math.sin(t * freq * 2 * math.pi)
            samples[i] = wave * env * 0.25
        
        return self.save_wav(samples, sample_rate)
    
    def generate_ui_cancel(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.15
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 15.0)
            # Two-tone descending
            if t < 0.075:
                freq = 900.0
            else:
                freq = 600.0
            wave = math.sin(t * freq * 2 * math.pi)
            samples[i] = wave * env * 0.25
        
        return self.save_wav(samples, sample_rate)
    
    def generate_powerup_sound(self, seed: Optional[int] = None) -> bytes:
        if seed is not None:
            self.rng.seed(seed)
        
        duration = 0.3
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 8.0)
            # Ascending arpeggio
            freq = 400.0 + (t / duration) * 800.0
            wave = math.sin(t * freq * 2 * math.pi)
            harmonic = math.sin(t * freq * 2.0 * 2 * math.pi) * 0.3
            samples[i] = (wave + harmonic) * env * 0.3
        
        return self.save_wav(samples, sample_rate)
