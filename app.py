# ==============================================================================
# EchoSOS WebApp - Main Application (Hardened Version)
#
# This Streamlit application serves as an interactive demonstration of the
# EchoSOS acoustic signaling and detection technology.
# ==============================================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
from scipy.fft import fft, fftfreq
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase, RTCConfiguration
import io
import av

# --- Import our custom audio processing functions ---
from audio_utils import generate_chirp, analyze_and_detect_chirp, EMERGENCIES, SAMPLE_RATE

# --- Function to set the background image and styles ---
def set_page_styling():
    # ... (This function remains exactly the same as the last version) ...
    image_url = "https://images.pexels.com/photos/998641/pexels-photo-998641.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
    page_styling = f"""
    <style>
    .stApp {{ background-image: url("{image_url}"); background-attachment: fixed; background-size: cover; }}
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{ color: white !important; }}
    .stButton > button {{ color: #FFFFFF !important; background-color: #d13639 !important; border: 2px solid #FFFFFF !important; font-weight: bold !important; border-radius: 10px !important; }}
    .stButton > button:hover {{ background-color: #a82a2d !important; border-color: #CCCCCC !important; }}
    .st-emotion-cache-1wivap2, .st-emotion-cache-zt5igj, .st-emotion-cache-j7qwjs {{ background-color: rgba(0, 0, 0, 0.6) !important; border: 1px solid #d13639 !important; border-radius: 10px !important; }}
    </style>
    """
    st.markdown(page_styling, unsafe_allow_html=True)

# --- Page Configuration ---
st.set_page_config(page_title="EchoSOS Dashboard", page_icon="🚨", layout="wide")
set_page_styling()

# --- Main App UI ---
st.title("🚨 EchoSOS: Acoustic Rescue Beacon Dashboard")
# ... (Title and Intro text remain the same) ...

# Initialize session state for our refresh trick
if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = 0

col1, col2 = st.columns([0.8, 1])

# ======================================================
#                        TRANSMIT PANEL
# ======================================================
with col1:
    # ... (This entire panel remains exactly the same as the last version) ...
    st.header("TRANSMIT PANEL")
    st.markdown("...")
    for emergency_name in EMERGENCIES.keys():
        if st.button(f"Broadcast: {emergency_name}", use_container_width=True):
            # ... (button logic is unchanged) ...
            pass # Placeholder for your existing code

# ======================================================
#                        RECEIVE PANEL (REVISED)
# ======================================================
with col2:
    st.header("RECEIVE PANEL")
    st.markdown("Activate the microphone to listen for signals in real-time.")

    # --- CHANGE 1: Define RTC Configuration with a reliable STUN server ---
    RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

    class AudioProcessor(AudioProcessorBase):
        # ... (This class remains exactly the same) ...
        def __init__(self): self.audio_buffer = []
        def recv(self, frame: av.AudioFrame) -> av.AudioFrame: self.audio_buffer.append(frame.to_ndarray().flatten()); return frame

    # --- The main WebRTC streamer component with our changes ---
    webrtc_ctx = webrtc_streamer(
        key=f"receiver_{st.session_state.refresh_key}",  # <-- CHANGE 2a: Key now depends on refresh state
        mode=WebRtcMode.RECVONLY,
        rtc_configuration=RTC_CONFIGURATION, # <-- CHANGE 1: Applying the STUN server config
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"video": False, "audio": True},
    )

    # --- CHANGE 2b: The Force Refresh button ---
    if st.button("🔄 Force Refresh Receiver"):
        st.session_state.refresh_key += 1
        st.rerun() # Immediately rerun the script with the new key

    # --- UI Placeholders ---
    status_indicator = st.empty()
    strength_indicator = st.empty()
    graph_indicator = st.empty()

    # --- Revised Logic Loop with Clearer Feedback ---
    if webrtc_ctx.state.playing:
        status_indicator.info("ℹ️ STATUS: Receiver is active. Listening for signal...")
        if webrtc_ctx.audio_processor:
            if webrtc_ctx.audio_processor.audio_buffer:
                # ... (The entire analysis block remains the same as before) ...
                # ...
                pass # Placeholder for your existing analysis code
            else:
                strength_indicator.progress(0, text="Signal Strength: 0%")
                graph_indicator.empty() # Clear graph if no audio
        else:
            status_indicator.error("❌ ERROR: Could not start audio processor. The component may be stuck.")
    else:
        status_indicator.warning("⚠️ STATUS: Receiver is OFF. Click 'START' above to activate microphone.")
