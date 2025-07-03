# ==============================================================================
# EchoSOS WebApp - Main Application (FINAL Version with Debug Mode)
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

# --- Initialize session state ---
if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = 0

# --- Main App UI ---
st.title("🚨 EchoSOS: Acoustic Rescue Beacon Dashboard")
st.write("""
This interactive prototype demonstrates the core EchoSOS technology. 
Use one device (like your phone) to **Transmit** a signal, and another (like your laptop) to **Receive** and analyze it.
""")

col1, col2 = st.columns([0.8, 1])

# ======================================================
#                        TRANSMIT PANEL
# ======================================================
with col1:
    st.header("TRANSMIT PANEL")
    st.markdown("Select an emergency to broadcast its unique acoustic signal.")
    for emergency_name in EMERGENCIES.keys():
        if st.button(f"Broadcast: {emergency_name}", use_container_width=True):
            chirp_signal = generate_chirp(emergency_name)
            virtual_file = io.BytesIO()
            scaled_audio = np.int16(chirp_signal / np.max(np.abs(chirp_signal)) * 32767)
            write(virtual_file, SAMPLE_RATE, scaled_audio)
            st.audio(virtual_file)
            st.success(f"Transmitting '{emergency_name}' signal...")

# ======================================================
#                        RECEIVE PANEL (with Debug Mode)
# ======================================================
with col2:
    st.header("RECEIVE PANEL")
    st.markdown("Activate the microphone to listen for signals in real-time.")

    # --- DEBUG MODE CONTROLS ---
    st.markdown("---")
    debug_mode = st.checkbox("Show Debug Information")
    
    # Allow user to set threshold live in the app.
    power_threshold = st.number_input(
        label="Detection Power Threshold (Lower to make it more sensitive)",
        min_value=50,
        max_value=5000,
        value=500, # A reasonable starting guess
        step=50
    )
    st.markdown("---")


    RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    class AudioProcessor(AudioProcessorBase):
        def __init__(self): self.audio_buffer = []
        def recv(self, frame: av.AudioFrame) -> av.AudioFrame: self.audio_buffer.append(frame.to_ndarray().flatten()); return frame

    webrtc_ctx = webrtc_streamer(
        key=f"receiver_{st.session_state.refresh_key}",
        mode=WebRtcMode.RECVONLY,
        rtc_configuration=RTC_CONFIGURATION,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"video": False, "audio": True},
    )

    if st.button("🔄 Force Refresh Receiver"):
        st.session_state.refresh_key += 1
        st.rerun()

    # UI Placeholders
    status_indicator = st.empty()
    strength_indicator = st.empty()
    debug_indicator = st.empty() # Placeholder for debug info
    graph_indicator = st.empty()

    if webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
        if webrtc_ctx.audio_processor.audio_buffer:
            
            audio_chunk = np.concatenate(webrtc_ctx.audio_processor.audio_buffer)
            webrtc_ctx.audio_processor.audio_buffer.clear()
            
            # --- Perform Core Analysis ---
            # We pass the user-defined threshold to our analysis function
            detected_name, peak_freq, peak_power = analyze_and_detect_chirp(audio_chunk, SAMPLE_RATE, custom_threshold=power_threshold)
            
            # --- Display Debug Info if toggled ---
            if debug_mode:
                debug_indicator.info(f"Live Peak Power: {peak_power:.0f} | Live Peak Freq: {peak_freq:.0f} Hz | Threshold: {power_threshold}")
            else:
                debug_indicator.empty()

            # --- Update UI based on Analysis ---
            if detected_name:
                status_indicator.success(f"✅ STATUS: DETECTED - **{detected_name}**")
                strength_normalized = min(peak_power / (power_threshold * 20), 1.0) # Normalize relative to threshold
                strength_indicator.progress(strength_normalized, text=f"Signal Strength: {int(strength_normalized * 100)}%")
            else:
                status_indicator.info("ℹ️ STATUS: Listening... No known signal detected.")
                strength_indicator.progress(0, text="Signal Strength: 0%")

            # --- Update Frequency Spectrum Graph ---
            fig, ax = plt.subplots(figsize=(10, 3))
            N = len(audio_chunk)
            if N > 0:
                yf = np.abs(fft(audio_chunk))
                xf = fftfreq(N, 1 / SAMPLE_RATE)
                ax.plot(xf[:N // 2], yf[:N // 2], color="#d13639")
            ax.set_title("Live Audio Frequency Spectrum", color="white")
            ax.set_xlabel("Frequency (Hz)", color="white")
            ax.set_ylabel("Power", color="white")
            ax.tick_params(colors='white')
            ax.set_ylim(0, 15000)
            ax.set_xlim(14000, 21000)
            fig.patch.set_alpha(0.0)
            ax.set_facecolor((0, 0, 0, 0.5))
            graph_indicator.pyplot(fig)
            plt.close(fig)
        else:
            status_indicator.info("ℹ️ STATUS: Receiver is active. Listening...")
            strength_indicator.progress(0, text="Signal Strength: 0%")
    else:
        status_indicator.warning("⚠️ STATUS: Receiver is OFF. Click 'START' above to activate microphone.")
