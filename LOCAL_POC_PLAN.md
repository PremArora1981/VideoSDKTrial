# Local Agent Tester - POC Plan

## Overview
A local-first desktop/web application to design, configure, and test AI voice agents using your PC's microphone and speakers. This tool bypasses VideoSDK rooms for cost-free local prototyping.

## Architecture
- **Frontend**: Next.js (React) running locally.
- **Backend**: FastAPI (Python) wrapping the `videosdk-agents` framework in "Console Mode".
- **Storage**: Local SQLite database for configs and API keys.

## Features Scope

### 1. Configuration Tab
- **Pipeline Selection**: Choose between "Realtime" (Unified) or "Cascading" (Modular).
- **Model Selection**:
  - **LLM**: OpenAI GPT-4o, Anthropic Claude, Gemini, etc.
  - **STT (ASR)**: Deepgram, OpenAI Whisper, Google, AssemblyAI.
  - **TTS**: ElevenLabs, Cartesia, OpenAI, Deepgram.
- **System Prompt**: Rich text editor for defining agent persona.
- **Voice Tuning**:
  - Dynamic voice list based on selected TTS provider.
  - Sliders for speed, pitch, stability (if supported).
  - Language selection.

### 2. Admin / Settings Tab
- **API Key Management**: Securely store keys for OpenAI, ElevenLabs, Deepgram, etc.
- **Audio Device Selection**: Choose specific Mic/Speaker inputs if multiple exist.

### 3. Test Console (The "Playground")
- **Start/Stop**: Button to launch the agent process.
- **Visualizer**: Audio waveform or simple "Listening/Speaking" state indicator.
- **Transcript Log**: Real-time scrolling text of the conversation.
- **Interrupt**: Button to manually interrupt (simulating barge-in).

## Technical Approach

### Backend (FastAPI)
- **`/config`**: CRUD for agent presets.
- **`/keys`**: CRUD for API keys (stored locally).
- **`/start`**: Spawns a Python subprocess running the `Agent` in `console_mode`.
  - *Why subprocess?* To isolate the audio loop and allow clean restarts without killing the web server.
- **`/stop`**: Terminates the subprocess.
- **WebSockets**: Streams logs and transcription from the subprocess back to the UI.

### Frontend (Next.js)
- **State Management**: React Context for current configuration.
- **UI Components**:
  - Provider dropdowns (dynamic based on plugins).
  - Voice selector (fetches list from provider API via backend).
  - Log viewer (WebSocket consumer).

## Step-by-Step Implementation Plan

1.  **Setup**: Refine existing `poc-platform` structure.
2.  **Backend - Config & Keys**: Implement endpoints to save/load configs.
3.  **Backend - Runner**: Create a script `runner.py` that accepts a JSON config and runs `Agent(...).start()`.
4.  **Frontend - Config UI**: Build the form for selecting models and prompts.
5.  **Frontend - Admin UI**: Build the API key input form.
6.  **Integration**: Wire up the "Start" button to launch `runner.py` and stream stdout/stderr via WebSocket.

---
*This plan focuses entirely on the "Console Mode" functionality of the framework, avoiding any VideoSDK room costs/logic.*
