# ==============================================================================
# EchoSOS WebApp - Main Application
#
# This Streamlit application serves as an interactive demonstration of the
# EchoSOS acoustic signaling and detection technology.
# ==============================================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
from scipy.fft import fft, fftfreq
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import io
import av # Important for handling audio frames

# --- Import our custom audio processing functions ---
# This is where we use the logic we built and tested!
from audio_utils import generate_chirp, analyze_and_detect_chirp, EMERGENCIES, SAMPLE_RATE

# --- Function to set the background image ---
def set_background(image_url):
    """
    Sets a background image for the Streamlit app.
    """
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-attachment: fixed;
            background-size: cover;
        }}
        h1, h2, h3, p, label {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    """

# --- Page Configuration ---
st.set_page_config(
    page_title="EchoSOS Dashboard",
    page_icon="🚨",
    layout="wide"
)

# --- Call the function to set our custom background ---
set_background("https://images.pexels.com/photos/998641/pexels-photo-998641.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")

# --- Main App UI ---
st.title("🚨 EchoSOS: Acoustic Rescue Beacon Dashboard")
st.write("""
<p style="color:white;">This interactive prototype demonstrates the core EchoSOS technology. 
Use one device (like your phone) to <strong>Transmit</strong> a signal, and another (like your laptop) to <strong>Receive</strong> and analyze it.</p>
""", unsafe_allow_html=True)

# Create two columns for our dashboard layout
col1, col2 = st.columns([0.8, 1]) # Make the right column slightly wider

# ======================================================
#                        TRANSMIT PANEL
# ======================================================
with col1:
    st.header("TRANSMIT PANEL")
    st.markdown("Select an emergency to broadcast its unique acoustic signal.")

    # Create a button for each defined emergency signal
    for emergency_name in EMERGENCIES.keys():
        
        # When a button is clicked, this block executes
        if st.button(f"Broadcast: {emergency_name}", use_container_width=True):
            
            # 1. Generate the audio signal using our utility function
            chirp_signal = generate_chirp(emergency_name)
            
            # 2. Convert the NumPy array to a WAV file in memory
            # st.audio needs a file-like object, not a raw array
            virtual_file = io.BytesIO()
            # We scale the signal to 16-bit integer format for the WAV file
            scaled_audio = np.int16(chirp_signal / np.max(np.abs(chirp_signal)) * 32767)
            write(virtual_file, SAMPLE_RATE, scaled_audio)
            
            # 3. Play the audio using Streamlit's built-in audio player
            st.audio(virtual_file)
            st.success(f"Transmitting '{emergency_name}' signal...")

# ======================================================
#                        RECEIVE PANEL
# ======================================================
with col2:
    st.header("RECEIVE PANEL")
    st.markdown("Activate the microphone to listen for signals in real-time.")

    # We need a class to process audio frames from the browser's microphone
    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            # This list will accumulate audio chunks for analysis
            self.audio_buffer = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            # The WebRTC component sends audio frames here.
            # We convert the frame to a NumPy array and add it to our buffer.
            self.audio_buffer.append(frame.to_ndarray().flatten())
            # We must return the frame back, though we don't modify it
            return frame

    # The main WebRTC streamer component
    webrtc_ctx = webrtc_streamer(
        key="receiver",
        mode=WebRtcMode.RECVONLY, # We only want to receive audio, not send it
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"video": False, "audio": True},
    )

    # --- UI Placeholders ---
    # We create empty elements that we can fill with live data later
    status_indicator = st.empty()
    strength_indicator = st.empty()
    graph_indicator = st.empty()

    # This is the main logic loop for the receiver
    if webrtc_ctx.state.playing:
        # Check if the audio processor has been successfully created
        if webrtc_ctx.audio_processor:
            # Check if we have audio in the buffer to process
            if webrtc_ctx.audio_processor.audio_buffer:
                
                # Concatenate all recent audio chunks into one for analysis
                audio_chunk = np.concatenate(webrtc_ctx.audio_processor.audio_buffer)
                webrtc_ctx.audio_processor.audio_buffer.clear() # Clear buffer for next round
                
                # --- Perform the analysis using our utility function ---
                detected_name, peak_freq, peak_power = analyze_and_detect_chirp(audio_chunk, SAMPLE_RATE)
                
                # --- Update the UI based on the results ---
                if detected_name:
                    status_indicator.success(f"✅ STATUS: DETECTED - **{detected_name}**")
                    # Normalize strength for the progress bar (max value is tuned by testing)
                    strength_normalized = min(peak_power / 10000.0, 1.0)
                    strength_indicator.progress(strength_normalized, text=f"Signal Strength: {int(strength_normalized * 100)}%")
                else:
                    status_indicator.info("ℹ️ STATUS: Listening... No known signal detected.")
                    strength_indicator.progress(0, text="Signal Strength: 0%")

                # --- Update the Frequency Spectrum Graph ---
                fig, ax = plt.subplots(figsize=(10,3))
                N = len(audio_chunk)
                if N > 0:
                    yf = np.abs(fft(audio_chunk))
                    xf = fftfreq(N, 1/SAMPLE_RATE)
                    ax.plot(xf[:N//2], yf[:N//2]) # Plot only positive frequencies
                ax.set_title("Live Audio Frequency Spectrum")
                ax.set_xlabel("Frequency (Hz)")
                ax.set_ylabel("Power")
                ax.set_ylim(0, 15000) # Set a fixed y-axis limit for stable visualization
                ax.set_xlim(14000, 21000) # Zoom in on our emergency frequency range
                graph_indicator.pyplot(fig)
                plt.close(fig) # Important to close the figure to free up memory
        else:
            # This message shows if the mic is not properly activated
            status_indicator.warning("⚠️ Audio receiver is not ready. Please try restarting or check browser/OS microphone permissions.")
    else:
        # This is the default message before the user clicks "START"
        status_indicator.info("ℹ️ STATUS: Receiver is idle. Click 'START' to activate microphone.")
