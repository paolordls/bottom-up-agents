from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Iterator
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class BaseAgent(ABC):
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history: List[Dict[str, str]] = []
    
    @abstractmethod
    def process(self, user_input: str) -> str:
        pass
    
    @abstractmethod
    def process_stream(self, user_input: str) -> Iterator[str]:
        pass
    
    def _create_messages(self, user_input: str) -> List[Dict[str, str]]:
        return [{"role": "user", "content": user_input}]
    
    def _call_llm(self, messages: List[Dict[str, str]], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            **kwargs
        )
        return response.choices[0].message.content
    
    def _call_llm_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            stream=True,
            **kwargs
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content