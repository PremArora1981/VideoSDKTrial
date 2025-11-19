from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class AgentConfig(Base):
    """Stores agent configuration presets"""
    __tablename__ = "agent_configs"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    system_prompt = Column(Text, default="")
    
    # Pipeline Settings
    pipeline_type = Column(String, default="cascading") # "realtime" or "cascading"
    
    # Model Selection (Cascading)
    llm_provider = Column(String, default="openai")
    llm_model = Column(String, default="gpt-4o")
    stt_provider = Column(String, default="deepgram")
    tts_provider = Column(String, default="elevenlabs")
    
    # Model Selection (Realtime)
    realtime_provider = Column(String, nullable=True)
    realtime_model = Column(String, nullable=True)

    # Voice Settings
    voice_id = Column(String, nullable=True)
    voice_settings = Column(JSON, default={}) # speed, pitch, stability, etc.
    language = Column(String, default="en")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ApiKey(Base):
    """Stores API keys locally"""
    __tablename__ = "api_keys"

    provider = Column(String, primary_key=True) # openai, elevenlabs, deepgram, etc.
    key = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


