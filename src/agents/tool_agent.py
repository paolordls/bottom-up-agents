import json
from typing import List, Dict, Any, Iterator
from src.core.base_agent import BaseAgent
from src.core.prompts import TRAVEL_AGENT_TOOL_SYSTEM_PROMPT, TRAVEL_AGENT_TOOL_FEW_SHOT_EXAMPLES
from src.core.tools import Tool, TRAVEL_TOOLS


class ToolAgent(BaseAgent):
    def __init__(self, tools: List[Tool] = None, **kwargs):
        super().__init__(**kwargs)
        self.tools = tools or TRAVEL_TOOLS
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.show_reasoning = True  # Show tool calling process
        self.enable_memory = True  # Enable conversation memory
    
    def process(self, user_input: str) -> str:
        reasoning_trace = []
        messages = [{"role": "system", "content": TRAVEL_AGENT_TOOL_SYSTEM_PROMPT}]
        
        # Add few-shot examples
        for example in TRAVEL_AGENT_TOOL_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add conversation history if memory is enabled
        if self.enable_memory:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        
        # Call LLM with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            tools=[{"type": "function", "function": tool.to_openai_function()} for tool in self.tools],
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Check if the model wants to use tools
        if response_message.tool_calls:
            reasoning_trace.append("🤔 **Planning to use tools...**\n")
            
            # Execute tool calls
            tool_results = []
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                reasoning_trace.append(f"🔧 **Calling {tool_name}** with args: {tool_args}")
                
                if tool_name in self.tool_map:
                    result = self.tool_map[tool_name].execute(**tool_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "output": result
                    })
                    reasoning_trace.append(f"✅ **{tool_name} result**: {result}\n")
            
            # Add tool results to messages and get final response
            messages.append(response_message)
            for result in tool_results:
                messages.append({
                    "role": "tool",
                    "content": result["output"],
                    "tool_call_id": result["tool_call_id"]
                })
            
            reasoning_trace.append("💭 **Synthesizing results into final response...**\n\n---\n")
            
            # Get final response with tool results
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            final_content = final_response.choices[0].message.content
        else:
            final_content = response_message.content
        
        # Update conversation history if memory is enabled
        if self.enable_memory:
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": final_content})
        
        if self.show_reasoning and reasoning_trace:
            return "\n".join(reasoning_trace) + "\n" + final_content
        return final_content
    
    def process_stream(self, user_input: str) -> Iterator[str]:
        messages = [{"role": "system", "content": TRAVEL_AGENT_TOOL_SYSTEM_PROMPT}]
        
        # Add few-shot examples
        for example in TRAVEL_AGENT_TOOL_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add conversation history if memory is enabled
        if self.enable_memory:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        
        # First, check if tools will be used
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            tools=[{"type": "function", "function": tool.to_openai_function()} for tool in self.tools],
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        final_content = ""
        
        if response_message.tool_calls:
            # Stream the reasoning process
            if self.show_reasoning:
                yield "🤔 **Planning to use tools...**\n\n"
            
            # Execute tool calls
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                if self.show_reasoning:
                    yield f"🔧 **Calling {tool_name}** with args: {tool_args}\n"
                
                if tool_name in self.tool_map:
                    result = self.tool_map[tool_name].execute(**tool_args)
                    if self.show_reasoning:
                        yield f"✅ **{tool_name} result**: {result}\n\n"
            
            # Prepare for final response
            messages.append(response_message)
            for tool_call in response_message.tool_calls:
                if tool_call.function.name in self.tool_map:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    result = self.tool_map[tool_name].execute(**tool_args)
                    messages.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call.id
                    })
            
            if self.show_reasoning:
                yield "💭 **Synthesizing results into final response...**\n\n---\n\n"
            
            # Stream final response
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    final_content += chunk.choices[0].delta.content
                    yield chunk.choices[0].delta.content
        else:
            # No tools needed, stream the response directly
            for chunk in self._call_llm_stream(messages):
                final_content += chunk
                yield chunk
        
        # Update conversation history if memory is enabled
        if self.enable_memory:
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": final_content})
    
    def clear_memory(self):
        """Clear conversation history"""
        self.conversation_history = []