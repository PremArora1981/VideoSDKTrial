import streamlit as st
import json
import os
import asyncio
import threading
from videosdk.agents import Agent, AgentSession, CascadingPipeline, JobContext, RoomOptions
# Import plugins explicitly to ensure they are registered if needed
# For this POC we will dynamically load them based on config

# Configuration file path
CONFIG_FILE = "agent_config.json"

# Default Configuration
DEFAULT_CONFIG = {
    "api_keys": {
        "openai": "",
        "deepgram": "",
        "elevenlabs": ""
    },
    "pipeline": {
        "stt": "openai",
        "llm": "openai",
        "tts": "openai"
    },
    "system_prompt": "You are a helpful AI assistant.",
    "voice_settings": {
        "speed": 1.0,
        "voice_id": "alloy" 
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Global variable to hold the running agent thread/loop
if 'agent_thread' not in st.session_state:
    st.session_state.agent_thread = None
if 'stop_event' not in st.session_state:
    st.session_state.stop_event = threading.Event()

def run_agent_process(config):
    """
    This function runs in a separate thread. 
    It sets up the agent and enters the asyncio loop.
    """
    # Set API Keys from config into environment variables for the SDK to pick up
    if config["api_keys"]["openai"]:
        os.environ["OPENAI_API_KEY"] = config["api_keys"]["openai"]
    if config["api_keys"]["deepgram"]:
        os.environ["DEEPGRAM_API_KEY"] = config["api_keys"]["deepgram"]
    if config["api_keys"]["elevenlabs"]:
        os.environ["ELEVENLABS_API_KEY"] = config["api_keys"]["elevenlabs"]

    # Define the Agent
    class LocalAgent(Agent):
        def __init__(self):
            super().__init__(
                instructions=config["system_prompt"]
            )
        
        async def on_enter(self):
            await self.session.say("Hello, I am ready.")

    # Pipeline Construction
    # Simplified for POC: We assume OpenAI for everything if selected, or specific plugins
    # Ideally, map config["pipeline"]["stt"] to actual classes
    
    # Dynamic import based on selection would go here. 
    # For this snippet, we'll use a basic OpenAI pipeline as placeholder
    # but structure it to use the CascadingPipeline if user wants separation.
    
    from videosdk.plugins.openai import OpenAIStt, OpenAILlm, OpenAITts
    
    stt = OpenAIStt()
    llm = OpenAILlm()
    tts = OpenAITts()
    
    pipeline = CascadingPipeline(stt=stt, llm=llm, tts=tts)

    # Context & Session
    # In Console Mode, we don't strictly need a room_id, but the SDK expects the object
    room_options = RoomOptions(
        room_id="local-console", 
        name="Local User", 
        playground=True
    )
    
    ctx = JobContext(room_options=room_options)
    # Enable Console Mode flag manually or via argument if SDK supports it directly
    ctx.want_console = True 

    session = AgentSession(agent=LocalAgent(), pipeline=pipeline)

    async def runner():
        print("--> Connecting to Local Console...")
        # connect() in console mode sets up local audio streams
        await ctx.connect() 
        print("--> Starting Session...")
        await session.start()
        
        # Wait until stop event is set
        while not st.session_state.stop_event.is_set():
            await asyncio.sleep(0.1)
            
        print("--> Stopping Session...")
        await session.close()
        await ctx.shutdown()

    # Run the async loop
    asyncio.run(runner())

def start_agent():
    if st.session_state.agent_thread is None or not st.session_state.agent_thread.is_alive():
        st.session_state.stop_event.clear()
        config = load_config()
        t = threading.Thread(target=run_agent_process, args=(config,))
        t.start()
        st.session_state.agent_thread = t
        st.success("Agent Started! Speak into your microphone.")
    else:
        st.warning("Agent is already running.")

def stop_agent():
    if st.session_state.agent_thread and st.session_state.agent_thread.is_alive():
        st.session_state.stop_event.set()
        st.session_state.agent_thread.join(timeout=5)
        st.success("Agent Stopped.")
    else:
        st.info("Agent is not running.")

# --- UI Layout ---
st.set_page_config(page_title="Local Agent Builder", layout="wide")
st.title("🎙️ Local POC Agent Builder")

tabs = st.tabs(["Configuration", "Run Agent", "Admin / API Keys"])

# Tab 1: Configuration
with tabs[0]:
    st.header("Model Selection")
    config = load_config()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        config["pipeline"]["stt"] = st.selectbox("STT Provider", ["openai", "deepgram", "google"], index=0)
    with col2:
        config["pipeline"]["llm"] = st.selectbox("LLM Provider", ["openai", "anthropic", "gemini"], index=0)
    with col3:
        config["pipeline"]["tts"] = st.selectbox("TTS Provider", ["openai", "elevenlabs", "cartesia"], index=0)

    st.header("Agent Personality")
    config["system_prompt"] = st.text_area("System Prompt", value=config["system_prompt"], height=150)

    st.header("Voice Tuning")
    config["voice_settings"]["speed"] = st.slider("Speed", 0.5, 2.0, config["voice_settings"].get("speed", 1.0))
    
    if st.button("Save Configuration"):
        save_config(config)
        st.toast("Configuration Saved!")

# Tab 2: Run Agent
with tabs[1]:
    st.header("Test Your Agent")
    st.markdown("This uses your **local microphone and speakers**. No cloud room required.")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Start Agent", type="primary"):
            start_agent()
    with c2:
        if st.button("⏹️ Stop Agent"):
            stop_agent()
            
    if st.session_state.agent_thread and st.session_state.agent_thread.is_alive():
        st.info("🔴 Agent is LISTENING... (Check your terminal for logs)")

# Tab 3: Admin
with tabs[2]:
    st.header("API Keys")
    st.markdown("Keys are stored locally in `agent_config.json`.")
    
    with st.form("api_keys_form"):
        openai_key = st.text_input("OpenAI API Key", value=config["api_keys"]["openai"], type="password")
        deepgram_key = st.text_input("Deepgram API Key", value=config["api_keys"]["deepgram"], type="password")
        elevenlabs_key = st.text_input("ElevenLabs API Key", value=config["api_keys"]["elevenlabs"], type="password")
        
        if st.form_submit_button("Update Keys"):
            config["api_keys"]["openai"] = openai_key
            config["api_keys"]["deepgram"] = deepgram_key
            config["api_keys"]["elevenlabs"] = elevenlabs_key
            save_config(config)
            st.success("API Keys Updated!")

