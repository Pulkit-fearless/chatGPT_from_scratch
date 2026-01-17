import json
import os
import time
from typing import List, Dict, Optional
import anthropic
from context_editing import ContextManager

class ChatSession:
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-7-sonnet-20250219"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.system_prompt = "You are a helpful and knowledgeable AI assistant acting as a tutor. Use the context provided to answer questions effectively."
        self.messages: List[Dict[str, str]] = []
        self.session_id = f"session_{int(time.time())}"
        self.context_manager = ContextManager(self.client, model=self.model)
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def get_response(self, stream: bool = True):
        # Check for compaction before sending
        if self.context_manager.should_compact(self.messages):
            print("\n[System: Compacting conversation history...]")
            self.messages = self.context_manager.compact_history(self.messages)

        try:
            if stream:
                return self._stream_response()
            else:
                return self._simple_response()
        except Exception as e:
            return f"Error: {str(e)}"

    def _simple_response(self):
        response = self.client.messages.create(
            model=self.model,
            system=self.system_prompt,
            messages=self.messages,
            max_tokens=2000
        )
        assistant_reply = response.content[0].text
        self.messages.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply

    def _stream_response(self):
        """
        Yields text chunks for streaming.
        Also aggregates the full response to save to history.
        """
        full_response = ""
        
        with self.client.messages.stream(
            model=self.model,
            system=self.system_prompt,
            messages=self.messages,
            max_tokens=2000
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                yield text
        
        self.messages.append({"role": "assistant", "content": full_response})

    def save_session(self, filepath: Optional[str] = None):
        if not filepath:
            filepath = os.path.join("data", f"{self.session_id}.json")
        
        data = {
            "session_id": self.session_id,
            "model": self.model,
            "messages": self.messages,
            "timestamp": time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return filepath

    def load_session(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Session file not found: {filepath}")
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.session_id = data.get("session_id", self.session_id)
        self.model = data.get("model", self.model)
        self.messages = data.get("messages", [])
