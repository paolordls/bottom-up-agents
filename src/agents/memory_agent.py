from typing import Iterator
from src.core.base_agent import BaseAgent
from src.core.prompts import TRAVEL_AGENT_SYSTEM_PROMPT, TRAVEL_AGENT_FEW_SHOT_EXAMPLES


class MemoryAgent(BaseAgent):
    def process(self, user_input: str) -> str:
        # Build messages with full conversation history
        messages = [{"role": "system", "content": TRAVEL_AGENT_SYSTEM_PROMPT}]
        
        # Add few-shot examples first (before conversation history)
        for example in TRAVEL_AGENT_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_input})
        
        # Get response
        response = self._call_llm(messages)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def process_stream(self, user_input: str) -> Iterator[str]:
        # Build messages with full conversation history
        messages = [{"role": "system", "content": TRAVEL_AGENT_SYSTEM_PROMPT}]
        
        # Add few-shot examples first (before conversation history)
        for example in TRAVEL_AGENT_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_input})
        
        # Stream response and collect it
        full_response = ""
        for chunk in self._call_llm_stream(messages):
            full_response += chunk
            yield chunk
        
        # Update conversation history with complete response
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": full_response})
    
    def clear_memory(self):
        self.conversation_history = []