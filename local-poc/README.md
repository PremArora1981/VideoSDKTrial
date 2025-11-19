# Local POC Agent Builder

A simplified, local-only version of the agent builder that runs directly on your machine using "Console Mode". No VideoSDK rooms, no cloud infrastructure required.

## Features
- **Config Dashboard**: Select STT, LLM, TTS providers.
- **Prompt Editor**: Edit system prompts and instructions.
- **Voice Tuning**: Adjust TTS parameters (speed, pitch, voice ID).
- **API Key Manager**: Securely input keys for OpenAI, Deepgram, etc.
- **Local Runtime**: Uses your computer's microphone and speakers.

## Tech Stack
- **Frontend**: Streamlit (Python-based UI, perfect for local data apps).
- **Backend**: VideoSDK Agents Framework (Console Mode).
- **Storage**: Local JSON file for configs.

## Setup
1. Install dependencies:
   ```bash
   pip install streamlit videosdk-agents python-dotenv
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

