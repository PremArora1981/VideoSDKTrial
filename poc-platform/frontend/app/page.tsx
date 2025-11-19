'use client';

import { useState, useEffect } from 'react';

export default function ConfigPage() {
  const [config, setConfig] = useState({
    system_prompt: '',
    pipeline_type: 'realtime',
    llm_model: 'gpt-4o-realtime-preview',
    voice: 'alloy',
    api_keys: { openai: '' }
  });
  
  const [status, setStatus] = useState('stopped');
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    // Fetch initial config
    fetch('http://localhost:8000/config')
      .then(res => res.json())
      .then(data => setConfig(prev => ({ ...prev, ...data })));
      
    // WebSocket for logs
    const ws = new WebSocket('ws://localhost:8000/logs');
    ws.onmessage = (event) => {
      setLogs(prev => [...prev, event.data]);
    };
    return () => ws.close();
  }, []);

  const handleSave = async () => {
    await fetch('http://localhost:8000/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    alert('Configuration saved!');
  };

  const toggleAgent = async () => {
    if (status === 'stopped') {
      await fetch('http://localhost:8000/start', { method: 'POST' });
      setStatus('running');
    } else {
      await fetch('http://localhost:8000/stop', { method: 'POST' });
      setStatus('stopped');
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Local Agent Console</h1>
      
      <div className="grid grid-cols-2 gap-8">
        <div className="space-y-4">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Configuration</h2>
            
            <label className="block text-sm font-medium mb-1">Pipeline Type</label>
            <select 
              className="input-field mb-4"
              value={config.pipeline_type}
              onChange={e => setConfig({...config, pipeline_type: e.target.value})}
            >
              <option value="realtime">Realtime (OpenAI)</option>
              <option value="cascading">Cascading (STT+LLM+TTS)</option>
            </select>

            <label className="block text-sm font-medium mb-1">System Prompt</label>
            <textarea
              className="input-field h-32 mb-4"
              value={config.system_prompt}
              onChange={e => setConfig({...config, system_prompt: e.target.value})}
            />

            <label className="block text-sm font-medium mb-1">OpenAI API Key</label>
            <input 
              type="password" 
              className="input-field mb-4"
              value={config.api_keys.openai || ''}
              onChange={e => setConfig({...config, api_keys: {...config.api_keys, openai: e.target.value}})}
            />
            
            <button onClick={handleSave} className="btn-secondary w-full">Save Config</button>
          </div>
        </div>

        <div className="space-y-4">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Control</h2>
            <button 
              onClick={toggleAgent}
              className={`w-full py-3 rounded-lg text-white font-bold ${status === 'running' ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}`}
            >
              {status === 'running' ? 'Stop Agent' : 'Start Agent'}
            </button>
            
            <div className="mt-4 bg-black text-green-400 font-mono p-4 rounded h-64 overflow-y-auto text-sm">
              {logs.map((log, i) => <div key={i}>{log}</div>)}
              {logs.length === 0 && <span className="text-gray-500">Ready to start...</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

