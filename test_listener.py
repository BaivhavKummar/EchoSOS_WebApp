# ==============================================================================
# Minimal WebRTC Listener Test
#
# The only purpose of this app is to verify that the webrtc_streamer component
# can successfully initialize and access the microphone in this environment.
# ==============================================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase, RTCConfiguration
import av

# --- Page Configuration ---
st.set_page_config(page_title="Microphone Listener Test")
st.title("🎤 Minimal Microphone Listener Test")
st.write("""
This app tests the most basic function: accessing the microphone. 
Click 'START' below. If it works, you should be asked for microphone permission and then see a live graph of the audio your microphone is hearing.
""")

# --- The Core WebRTC Component ---

# Define a class to process audio frames
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_buffer = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Simply buffer the audio frames
        self.audio_buffer.append(frame.to_ndarray().flatten())
        return frame

# The WebRTC streamer component, with the reliable STUN server configuration
webrtc_ctx = webrtc_streamer(
    key="listener_test",
    mode=WebRtcMode.RECVONLY,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
)

# --- Live Display ---
graph_placeholder = st.empty()

if webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
    st.success("✅ Microphone is active. Try talking or snapping your fingers.")
    if webrtc_ctx.audio_processor.audio_buffer:
        
        # Combine and clear the buffer
        audio_chunk = np.concatenate(webrtc_ctx.audio_processor.audio_buffer)
        webrtc_ctx.audio_processor.audio_buffer.clear()
        
        # Create a simple plot of the audio waveform
        fig, ax = plt.subplots()
        ax.plot(audio_chunk)
        ax.set_title("Live Audio Waveform")
        ax.set_ylim(-1, 1) # Audio data is typically in the range [-1, 1]
        graph_placeholder.pyplot(fig)
        plt.close(fig)
else:
    st.warning("⚠️ Receiver is OFF. Click 'START' above.")
