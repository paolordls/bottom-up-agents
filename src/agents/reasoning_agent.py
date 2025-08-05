import json
from typing import List, Dict, Any, Optional, Iterator
from src.agents.tool_agent import ToolAgent
from src.core.tools import Tool


class ReasoningAgent(ToolAgent):
    def __init__(self, max_iterations: int = 20, **kwargs):
        super().__init__(**kwargs)
        self.max_iterations = max_iterations
        self.enable_memory = True
        self.show_reasoning = True  # Always show reasoning for agent loop
    
    def process(self, user_input: str) -> str:
        # Initial system prompt with planning capability
        system_prompt = """You are a helpful travel planning assistant with access to real-time information tools.

        When helping users plan trips, you should:
        1. Always check the weather forecast for their destination and travel dates first
        2. Search for flight options and provide specific recommendations with prices
        3. Look for hotel accommodations that match their preferences
        4. Consider weather conditions when suggesting activities
        5. If a tool fails (returns an error message starting with ❌), retry it or try alternative approaches
        6. Provide comprehensive travel plans with specific flight and hotel recommendations
        
        Your goal is to create personalized, weather-aware travel plans with actionable booking information.
        You can call multiple tools to gather all necessary information. Tools may occasionally fail due to service issues - simply retry them or use alternative approaches if needed."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add few-shot examples from parent classes
        from src.core.prompts import TRAVEL_AGENT_TOOL_FEW_SHOT_EXAMPLES
        for example in TRAVEL_AGENT_TOOL_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add conversation history if memory is enabled
        if self.enable_memory:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        
        iterations = 0
        final_response = None
        reasoning_trace = []
        
        reasoning_trace.append(f"🤖 **Agent Loop Starting** (max {self.max_iterations} iterations)\n")
        
        while iterations < self.max_iterations:
            reasoning_trace.append(f"\n🔄 **Iteration {iterations + 1}**")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                tools=[{"type": "function", "function": tool.to_openai_function()} for tool in self.tools],
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            # Log the agent's reasoning
            if response_message.content:
                reasoning_trace.append(f"💭 **Thinking**: {response_message.content}")
            
            # If no tool calls, we have our final answer
            if not response_message.tool_calls:
                reasoning_trace.append("✨ **Final response ready!**\n\n---\n")
                final_response = response_message.content
                break
            
            # Execute all tool calls with immediate retry on failure
            reasoning_trace.append(f"🔧 **Executing {len(response_message.tool_calls)} tool(s)**:")
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                reasoning_trace.append(f"  • {tool_name}({tool_args})")
                
                if tool_name in self.tool_map:
                    # Try the tool, retry once if it fails
                    result = self.tool_map[tool_name].execute(**tool_args)
                    
                    if result.startswith("❌"):
                        reasoning_trace.append(f"    → ⚠️ Failed: {result}")
                        reasoning_trace.append(f"    → 🔄 Retrying immediately...")
                        
                        # Immediate retry
                        result = self.tool_map[tool_name].execute(**tool_args)
                        
                        if result.startswith("❌"):
                            reasoning_trace.append(f"    → ❌ Retry failed: {result}")
                            reasoning_trace.append(f"    → Will continue with partial information")
                        else:
                            reasoning_trace.append(f"    → ✅ Retry successful: {result}")
                    else:
                        reasoning_trace.append(f"    → ✅ Success: {result}")
                    
                    messages.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call.id
                    })
            
            iterations += 1
        
        # Update conversation history if memory is enabled
        if self.enable_memory and final_response:
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": final_response})
        
        full_response = final_response or "I couldn't complete the travel planning. Please try again."
        
        if self.show_reasoning:
            return "\n".join(reasoning_trace) + "\n" + full_response
        return full_response
    
    def clear_memory(self):
        self.conversation_history = []
    
    def process_stream(self, user_input: str) -> Iterator[str]:
        # Initial system prompt with planning capability
        system_prompt = """You are a helpful travel planning assistant with access to real-time information tools.

        When helping users plan trips, you should:
        1. Always check the weather forecast for their destination and travel dates first
        2. Search for flight options and provide specific recommendations with prices
        3. Look for hotel accommodations that match their preferences
        4. Consider weather conditions when suggesting activities
        5. If a tool fails (returns an error message starting with ❌), retry it or try alternative approaches
        6. Provide comprehensive travel plans with specific flight and hotel recommendations
        
        Your goal is to create personalized, weather-aware travel plans with actionable booking information.
        You can call multiple tools to gather all necessary information. Tools may occasionally fail due to service issues - simply retry them or use alternative approaches if needed."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add few-shot examples from parent classes
        from src.core.prompts import TRAVEL_AGENT_TOOL_FEW_SHOT_EXAMPLES
        for example in TRAVEL_AGENT_TOOL_FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add conversation history if memory is enabled
        if self.enable_memory:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        
        iterations = 0
        final_response = None
        
        yield f"🤖 **Agent Loop Starting** (max {self.max_iterations} iterations)\n\n"
        
        while iterations < self.max_iterations:
            yield f"🔄 **Iteration {iterations + 1}**\n"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                tools=[{"type": "function", "function": tool.to_openai_function()} for tool in self.tools],
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            # Stream the agent's reasoning
            if response_message.content:
                yield f"💭 **Thinking**: {response_message.content}\n"
            
            # If no tool calls, we have the final answer
            if not response_message.tool_calls:
                yield "\n✨ **Final response ready!**\n\n---\n\n"
                
                # The response_message.content IS the final travel plan
                final_response = response_message.content
                
                # Stream the final response word by word to simulate streaming
                words = final_response.split()
                for i, word in enumerate(words):
                    if i > 0:
                        yield " "
                    yield word
                
                break
            
            # Execute all tool calls with immediate retry
            yield f"\n🔧 **Executing {len(response_message.tool_calls)} tool(s)**:\n"
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                yield f"  • {tool_name}({tool_args})\n"
                
                if tool_name in self.tool_map:
                    # Try the tool, retry once if it fails
                    result = self.tool_map[tool_name].execute(**tool_args)
                    
                    if result.startswith("❌"):
                        yield f"    → ⚠️ Failed: {result}\n"
                        yield f"    → 🔄 Retrying immediately...\n"
                        
                        # Immediate retry
                        result = self.tool_map[tool_name].execute(**tool_args)
                        
                        if result.startswith("❌"):
                            yield f"    → ❌ Retry failed: {result}\n"
                            yield f"    → Will continue with partial information\n"
                        else:
                            yield f"    → ✅ Retry successful: {result}\n"
                    else:
                        yield f"    → ✅ Success: {result}\n"
                    
                    messages.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call.id
                    })
            
            yield "\n"
            iterations += 1
        
        # Update conversation history if memory is enabled
        if self.enable_memory and final_response:
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": final_response})
        
        if not final_response:
            yield "\n⚠️ I couldn't complete the travel planning. Please try again."