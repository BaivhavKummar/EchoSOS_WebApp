# ==============================================================================
# EchoSOS WebApp - Audio Utilities
#
# This module contains the core functions for generating and analyzing the
# acoustic signals used by the EchoSOS application.
# ==============================================================================

import numpy as np
import scipy.signal
from scipy.fft import fft, fftfreq

# --- 1. Global Configuration ---

# This dictionary defines the unique frequency sweep for each emergency type.
# It is the "source of truth" for our acoustic protocol.
EMERGENCIES = {
    "Medical Alert": (15000, 16000),  # Sweeps from 15kHz to 16kHz
    "Public Harassment": (17000, 18000),  # Sweeps from 17kHz to 18kHz
    "Fire / Smoke": (19000, 20000)   # Sweeps from 19kHz to 20kHz
}

# Standard audio parameters used throughout the application.
SAMPLE_RATE = 44100
DURATION = 30  # seconds

# The power threshold for detecting a signal. Can be tuned.
POWER_THRESHOLD = 500


# --- 2. Signal Generation Function ---

def generate_chirp(emergency_name: str) -> np.ndarray:
    """
    Generates a unique frequency sweep (chirp) signal for a given emergency.

    Args:
        emergency_name (str): The name of the emergency. Must be a key in the EMERGENCIES dict.

    Returns:
        np.ndarray: A NumPy array containing the generated audio signal, normalized to [-1, 1].
                    Returns an empty array if the emergency name is not found.
    """
    if emergency_name not in EMERGENCIES:
        print(f"Error: Unknown emergency name '{emergency_name}'")
        return np.array([])

    start_freq, end_freq = EMERGENCIES[emergency_name]

    # Create the time array for the signal's duration
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)

    # Generate the chirp signal using scipy's chirp function
    chirp_signal = scipy.signal.chirp(t, f0=start_freq, f1=end_freq, t1=DURATION, method='linear')

    return chirp_signal


# --- 3. Signal Detection Function ---

# --- 3. Signal Detection Function (Updated) ---

def analyze_and_detect_chirp(audio_data: np.ndarray, sample_rate: int, custom_threshold: int = 500) -> tuple:
    """
    Analyzes a chunk of audio and identifies which, if any, emergency chirp is present.
    Now accepts a custom power threshold.
    """
    N = len(audio_data)
    if N == 0:
        return None, 0, 0

    yf = fft(audio_data)
    xf = fftfreq(N, 1 / sample_rate)

    positive_mask = xf > 0
    xf_positive = xf[positive_mask]
    yf_positive = np.abs(yf[positive_mask])

    peak_index = np.argmax(yf_positive)
    peak_freq = xf_positive[peak_index]
    peak_power = yf_positive[peak_index]

    # Use the custom_threshold passed from the app instead of the hardcoded one
    if peak_power < custom_threshold:
        return None, peak_freq, peak_power

    for name, (start_freq, end_freq) in EMERGENCIES.items():
        if start_freq <= peak_freq <= end_freq:
            return name, peak_freq, peak_power

    return "Unknown Signal", peak_freq, peak_power
