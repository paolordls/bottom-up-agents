from typing import Iterator
from src.core.base_agent import BaseAgent
from src.core.prompts import TRAVEL_AGENT_SYSTEM_PROMPT


class SimpleAgent(BaseAgent):
    def process(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": TRAVEL_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
        return self._call_llm(messages)
    
    def process_stream(self, user_input: str) -> Iterator[str]:
        messages = [
            {"role": "system", "content": TRAVEL_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
        yield from self._call_llm_stream(messages)