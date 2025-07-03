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
import av  # Important for handling audio frames

# --- Import our custom audio processing functions ---
# This is where we use the logic we built and tested!
from audio_utils import generate_chirp, analyze_and_detect_chirp, EMERGENCIES, SAMPLE_RATE


# --- Function to set the background image ---
def set_background(image_url):
    """
    Sets a background image for the Streamlit app using a more robust method.
    """
    # Define the CSS style as a multi-line f-string
    page_bg_img_style = f"""
    <style>
    .stApp {{
        background-image: url("{image_url}");
        background-attachment: fixed;
        background-size: cover;
    }}
    /* Target main text and headers for better visibility on dark background */
    h1, h2, h3, h4, h5, h6, p, label {{
        color: white !important;
    }}
    /* Ensure markdown text is also white */
    .stMarkdown {{
        color: white !important;
    }}
    </style>
    """  """
    
    # Inject the CSS into the Streamlit app
    st.markdown(page_bg_img_style, unsafe_allow_html=True)


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
st.write(f"""
This interactive prototype demonstrates the core EchoSOS technology. 
Use one device (like your phone) to **Transmit** a signal, and another (like your laptop) to **Receive** and analyze it.
""")

# Create two columns for our dashboard layout
col1, col2 = st.columns([0.8, 1])


# ======================================================
#                        TRANSMIT PANEL
# ======================================================
with col1:
    st.header("TRANSMIT PANEL")
    st.markdown("Select an emergency to broadcast its unique acoustic signal.")

    # Create a button for each defined emergency signal
    for emergency_name in EMERGENCIES.keys():
        if st.button(f"Broadcast: {emergency_name}", use_container_width=True):
            chirp_signal = generate_chirp(emergency_name)
            virtual_file = io.BytesIO()
            scaled_audio = np.int16(chirp_signal / np.max(np.abs(chirp_signal)) * 32767)
            write(virtual_file, SAMPLE_RATE, scaled_audio)
            st.audio(virtual_file)
            st.success(f"Transmitting '{emergency_name}' signal...")


# ======================================================
#                        RECEIVE PANEL
# ======================================================
with col2:
    st.header("RECEIVE PANEL")
    st.markdown("Activate the microphone to listen for signals in real-time.")

    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.audio_buffer = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            self.audio_buffer.append(frame.to_ndarray().flatten())
            return frame

    webrtc_ctx = webrtc_streamer(
        key="receiver",
        mode=WebRtcMode.RECVONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"video": False, "audio": True},
    )

    status_indicator = st.empty()
    strength_indicator = st.empty()
    graph_indicator = st.empty()

    if webrtc_ctx.state.playing:
        if webrtc_ctx.audio_processor:
            if webrtc_ctx.audio_processor.audio_buffer:
                audio_chunk = np.concatenate(webrtc_ctx.audio_processor.audio_buffer)
                webrtc_ctx.audio_processor.audio_buffer.clear()
                
                detected_name, peak_freq, peak_power = analyze_and_detect_chirp(audio_chunk, SAMPLE_RATE)
                
                if detected_name:
                    status_indicator.success(f"✅ STATUS: DETECTED - **{detected_name}**")
                    strength_normalized = min(peak_power / 10000.0, 1.0)
                    strength_indicator.progress(strength_normalized, text=f"Signal Strength: {int(strength_normalized * 100)}%")
                else:
                    status_indicator.info("ℹ️ STATUS: Listening... No known signal detected.")
                    strength_indicator.progress(0, text="Signal Strength: 0%")

                fig, ax = plt.subplots(figsize=(10, 3))
                N = len(audio_chunk)
                if N > 0:
                    yf = np.abs(fft(audio_chunk))
                    xf = fftfreq(N, 1 / SAMPLE_RATE)
                    ax.plot(xf[:N // 2], yf[:N // 2])
                ax.set_title("Live Audio Frequency Spectrum")
                ax.set_xlabel("Frequency (Hz)")
                ax.set_ylabel("Power")
                ax.set_ylim(0, 15000)
                ax.set_xlim(14000, 21000)
                graph_indicator.pyplot(fig)
                plt.close(fig)
        else:
            status_indicator.warning("⚠️ Audio receiver is not ready. Please try restarting or check browser/OS microphone permissions.")
    else:
        status_indicator.info("ℹ️ STATUS: Receiver is idle. Click 'START' to activate microphone.")
