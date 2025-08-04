from typing import Iterator
from src.core.base_agent import BaseAgent
from src.core.prompts import TRAVEL_AGENT_SYSTEM_PROMPT, TRAVEL_AGENT_FEW_SHOT_EXAMPLES


class FewShotAgent(BaseAgent):
    def process(self, user_input: str) -> str:
        messages = [{"role": "system", "content": TRAVEL_AGENT_SYSTEM_PROMPT}]
        
        # Add few-shot examples
        for example in TRAVEL_AGENT_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return self._call_llm(messages)
    
    def process_stream(self, user_input: str) -> Iterator[str]:
        messages = [{"role": "system", "content": TRAVEL_AGENT_SYSTEM_PROMPT}]
        
        # Add few-shot examples
        for example in TRAVEL_AGENT_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        yield from self._call_llm_stream(messages)