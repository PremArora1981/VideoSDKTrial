from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sys
import json
import asyncio
import logging
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Local Agent Console API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for POC
agent_config: Dict[str, Any] = {
    "system_prompt": "You are a helpful AI assistant.",
    "pipeline_type": "realtime",
    "llm_model": "gpt-4o-realtime-preview",
    "voice": "alloy",
    "api_keys": {}
}

running_process: Optional[subprocess.Popen] = None

class ConfigUpdate(BaseModel):
    system_prompt: Optional[str] = None
    pipeline_type: Optional[str] = None
    llm_model: Optional[str] = None
    voice: Optional[str] = None
    api_keys: Optional[Dict[str, str]] = None

@app.get("/config")
async def get_config():
    return agent_config

@app.post("/config")
async def update_config(config: ConfigUpdate):
    global agent_config
    update_data = config.dict(exclude_unset=True)
    
    # Deep merge api_keys if present
    if "api_keys" in update_data:
        agent_config["api_keys"].update(update_data["api_keys"])
        del update_data["api_keys"]
        
    agent_config.update(update_data)
    return agent_config

@app.post("/start")
async def start_agent():
    global running_process
    if running_process and running_process.poll() is None:
        return {"status": "already_running"}
    
    # Path to runner.py
    runner_path = os.path.join(os.path.dirname(__file__), "runner.py")
    config_json = json.dumps(agent_config)
    
    # Start subprocess
    try:
        running_process = subprocess.Popen(
            [sys.executable, runner_path, config_json],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        return {"status": "started"}
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop")
async def stop_agent():
    global running_process
    if running_process:
        running_process.terminate()
        try:
            running_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            running_process.kill()
        running_process = None
    return {"status": "stopped"}

@app.websocket("/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if running_process and running_process.poll() is None:
                # Read line from subprocess stdout
                line = running_process.stdout.readline()
                if line:
                    await websocket.send_text(line)
                else:
                    await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.5)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if running_process and running_process.poll() is None:
             # Optional: kill process on disconnect if desired, but maybe keep running?
             pass


