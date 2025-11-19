import logging
import sys
import json
import asyncio
import os
from typing import Dict, Any

# Add the project root to sys.path to import videosdk-agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from videosdk.agents import Agent, AgentSession, RealTimePipeline, CascadingPipeline, JobContext, WorkerJob
from videosdk.agents.console_mode import ConsoleMode

# Configure logging to print to stdout so the parent process can capture it
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ConfigurableAgent(Agent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            instructions=config.get("system_prompt", "You are a helpful assistant."),
        )
        self.config = config

    async def on_enter(self) -> None:
        logger.info("Agent entered local session.")
        await self.session.say("Hello! I am ready to chat.")

async def run_agent(config: Dict[str, Any]):
    logger.info("Initializing agent with config...")
    
    pipeline_type = config.get("pipeline_type", "realtime")
    
    # --- Pipeline Construction ---
    if pipeline_type == "realtime":
        from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
        
        model_name = config.get("llm_model", "gpt-4o-realtime-preview")
        voice = config.get("voice", "alloy")
        api_key = config.get("api_keys", {}).get("openai")
        
        if not api_key:
            logger.error("Error: OpenAI API Key missing for Realtime pipeline.")
            return

        model = OpenAIRealtime(
            model=model_name,
            api_key=api_key,
            config=OpenAIRealtimeConfig(
                voice=voice,
                modalities=["text", "audio"]
            )
        )
        pipeline = RealTimePipeline(model=model)
        
    elif pipeline_type == "cascading":
        # Simple cascading example using OpenAI for everything for MVP
        # In full version, this would parse config['stt_provider'], config['tts_provider'] etc.
        from videosdk.plugins.openai import OpenAIStt, OpenAILlm, OpenAITts
        
        api_key = config.get("api_keys", {}).get("openai")
        if not api_key:
            logger.error("Error: OpenAI API Key missing.")
            return

        pipeline = CascadingPipeline(
            stt=OpenAIStt(api_key=api_key),
            llm=OpenAILlm(api_key=api_key, model=config.get("llm_model", "gpt-4o")),
            tts=OpenAITts(api_key=api_key, voice=config.get("voice", "alloy"))
        )
    else:
        logger.error(f"Unknown pipeline type: {pipeline_type}")
        return

    agent = ConfigurableAgent(config)
    
    # JobContext is usually for rooms, but we are hijacking it for console mode mostly? 
    # Actually, ConsoleMode usually wraps the session directly or via a helper.
    # Let's look at how videosdk-agents/examples/test_realtime_pipeline.py does it usually.
    # But wait, we want to use ConsoleMode specifically to use local mic/speaker.
    
    # Re-using the pattern from the library's own console mode entry point if possible,
    # or manually setting up the audio streams.
    
    # Creating a dummy JobContext for the AgentSession to attach to, 
    # though ConsoleMode handles the IO.
    
    session = AgentSession(agent=agent, pipeline=pipeline)
    
    # Use ConsoleMode to run this session locally
    console = ConsoleMode(session)
    
    logger.info("Starting console session...")
    try:
        await console.start()
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        await console.stop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python runner.py <config_json>")
        sys.exit(1)
        
    try:
        config_str = sys.argv[1]
        config = json.loads(config_str)
        asyncio.run(run_agent(config))
    except Exception as e:
        logger.error(f"Runner Error: {e}")
        sys.exit(1)


