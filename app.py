# ==============================================================================
# EchoSOS WebApp - Main Application (Hardened & Complete Version)
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

# --- Initialize session state for the refresh trick ---
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
#                        RECEIVE PANEL (REVISED)
# ======================================================
with col2:
    st.header("RECEIVE PANEL")
    st.markdown("Activate the microphone to listen for signals in real-time.")

    # Define RTC Configuration with a reliable STUN server to aid connection
    RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

    class AudioProcessor(AudioProcessorBase):
        def __init__(self): self.audio_buffer = []
        def recv(self, frame: av.AudioFrame) -> av.AudioFrame: self.audio_buffer.append(frame.to_ndarray().flatten()); return frame

    # The main WebRTC streamer component with our stability changes
    webrtc_ctx = webrtc_streamer(
        key=f"receiver_{st.session_state.refresh_key}",  # Key now depends on refresh state
        mode=WebRtcMode.RECVONLY,
        rtc_configuration=RTC_CONFIGURATION, # Applying the STUN server config
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"video": False, "audio": True},
    )

    # The Force Refresh button to re-initialize the component if it gets stuck
    if st.button("🔄 Force Refresh Receiver"):
        st.session_state.refresh_key += 1
        st.rerun()

    # UI Placeholders
    status_indicator = st.empty()
    strength_indicator = st.empty()
    graph_indicator = st.empty()

    # Revised Logic Loop with Clearer Feedback
    if webrtc_ctx.state.playing:
        if webrtc_ctx.audio_processor:
            # Check if there's any audio data in the buffer
            if webrtc_ctx.audio_processor.audio_buffer:
                
                # Combine all audio chunks from the buffer for analysis
                audio_chunk = np.concatenate(webrtc_ctx.audio_processor.audio_buffer)
                webrtc_ctx.audio_processor.audio_buffer.clear()
                
                # --- Perform the Core Analysis ---
                detected_name, peak_freq, peak_power = analyze_and_detect_chirp(audio_chunk, SAMPLE_RATE)
                
                # --- Update the UI based on the analysis results ---
                if detected_name:
                    status_indicator.success(f"✅ STATUS: DETECTED - **{detected_name}**")
                    strength_normalized = min(peak_power / 10000.0, 1.0)
                    strength_indicator.progress(strength_normalized, text=f"Signal Strength: {int(strength_normalized * 100)}%")
                else:
                    status_indicator.info("ℹ️ STATUS: Listening... No known signal detected.")
                    strength_indicator.progress(0, text="Signal Strength: 0%")

                # --- Update the Frequency Spectrum Graph ---
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
                # This state is normal between audio frames, just show listening status
                status_indicator.info("ℹ️ STATUS: Receiver is active. Listening...")
                strength_indicator.progress(0, text="Signal Strength: 0%")
                graph_indicator.empty()
        else:
            status_indicator.error("❌ ERROR: Could not start audio processor. Try the 'Force Refresh' button.")
    else:
        status_indicator.warning("⚠️ STATUS: Receiver is OFF. Click 'START' above to activate microphone.")
