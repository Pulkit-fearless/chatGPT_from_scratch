import json
from typing import List, Dict, Any, Optional
import anthropic

class ContextManager:
    """
    Manages the context window, token counting, and compaction strategies.
    """
    def __init__(self, client: anthropic.Anthropic, model: str = "claude-3-7-sonnet-20250219", max_tokens: int = 20000):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        # Reserve some tokens for the response and system prompt overhead
        self.token_buffer = 4000 

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count. 
        Note: Precise counting requires the model-specific tokenizer.
        This uses a heuristic or the API if available (though API usually counts tokens on response).
        For now, we'll use a heuristic (char count / 4) as a lightweight approximation 
        if we don't have a local tokenizer.
        """
        # TODO: Implement precise token counting using anthropic-tokenizer-python if available
        return len(text) // 4

    def count_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count tokens for a list of messages.
        """
        total = 0
        for msg in messages:
            total += self.count_tokens(msg.get("content", ""))
        return total

    def should_compact(self, messages: List[Dict[str, str]]) -> bool:
        """
        Determine if compaction is needed based on current token usage.
        """
        current_tokens = self.count_message_tokens(messages)
        return current_tokens > (self.max_tokens - self.token_buffer)

    def compact_history(self, history: List[Dict[str, str]], keep_last_n: int = 4) -> List[Dict[str, str]]:
        """
        Compacts the conversation history by summarizing older messages.
        Keeps the last `keep_last_n` messages intact.
        """
        if len(history) <= keep_last_n:
            return history

        # Split into to-be-summarized and recent messages
        to_summarize = history[:-keep_last_n]
        recent_messages = history[-keep_last_n:]

        # Create a prompt for summarization
        conversation_text = ""
        for msg in to_summarize:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            conversation_text += f"{role.upper()}: {content}\n\n"

        # Ask the model to summarize
        try:
            summary_message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user", 
                        "content": f"Please provide a concise summary of the following conversation history. Capture key facts, user preferences, and important context that should be preserved for the ongoing conversation.\n\nCONVERSATION:\n{conversation_text}"
                    }
                ]
            )
            summary_text = summary_message.content[0].text
            
            # Create a new history structure: 
            # [Summary System Message/User Note] + [Recent Messages]
            # We'll inject the summary as a 'user' message with context note, 
            # or better, as a separate context block if the system prompt allowed it.
            # For simplicity, we append it as a context note.
            
            compacted_message = {
                "role": "user", 
                "content": f"[System Note: The following is a summary of the earlier conversation: {summary_text}]"
            }
            
            # Depending on how strict we are, we might want to merge this with the next user message,
            # but adding it as a standalone user message is a common pattern.
            
            new_history = [compacted_message] + recent_messages
            return new_history

        except Exception as e:
            print(f"Error during compaction: {e}")
            return history
