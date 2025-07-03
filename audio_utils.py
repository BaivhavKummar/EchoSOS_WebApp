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

def analyze_and_detect_chirp(audio_data: np.ndarray, sample_rate: int) -> tuple:
    """
    Analyzes a chunk of audio and identifies which, if any, emergency chirp is present.

    This function performs a Fast Fourier Transform (FFT) to find the dominant frequency
    and compares it against the known emergency signal ranges.

    Args:
        audio_data (np.ndarray): The audio signal to analyze.
        sample_rate (int): The sample rate of the audio data.

    Returns:
        tuple: A tuple containing (detected_name, peak_frequency, peak_power).
               - `detected_name` (str or None): The name of the detected emergency or None.
               - `peak_frequency` (float): The frequency with the most power.
               - `peak_power` (float): The power of the peak frequency.
    """
    N = len(audio_data)
    if N == 0:
        return None, 0, 0

    # Perform FFT
    yf = fft(audio_data)
    xf = fftfreq(N, 1 / sample_rate)

    # Isolate positive frequencies and their magnitudes
    positive_mask = xf > 0
    xf_positive = xf[positive_mask]
    yf_positive = np.abs(yf[positive_mask])

    # Find the peak frequency and its power
    peak_index = np.argmax(yf_positive)
    peak_freq = xf_positive[peak_index]
    peak_power = yf_positive[peak_index]

    # Check if the signal is strong enough to be considered
    if peak_power < POWER_THRESHOLD:
        return None, peak_freq, peak_power

    # Check if the peak frequency falls into any of our defined emergency ranges
    for name, (start_freq, end_freq) in EMERGENCIES.items():
        if start_freq <= peak_freq <= end_freq:
            return name, peak_freq, peak_power

    # If the signal is strong but unrecognized, label it as "Unknown"
    return "Unknown Signal", peak_freq, peak_power
