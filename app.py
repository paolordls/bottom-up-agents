#!/usr/bin/env python3
"""
Streamlit app for exploring different AI agent stages
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.agents.simple_agent import SimpleAgent
from src.agents.few_shot_agent import FewShotAgent
from src.agents.memory_agent import MemoryAgent
from src.agents.tool_agent import ToolAgent
from src.agents.reasoning_agent import ReasoningAgent

# Check if API key is set
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ Please set your OPENAI_API_KEY in the .env file")
    st.stop()


# Page config
st.set_page_config(
    page_title="Bottom-Up AI Agents Explorer",
    page_icon="🤖",
    layout="wide"
)

# Agent descriptions
AGENT_INFO = {
    "Stage 0: Simple Agent": {
        "key": "simple",
        "description": "Basic prompt-response interaction",
        "features": ["System prompt", "Single turn"],
        "class": SimpleAgent
    },
    "Stage 1: Few-Shot Agent": {
        "key": "few_shot",
        "description": "Uses examples to guide responses",
        "features": ["System prompt", "Example-based learning", "Better formatting"],
        "class": FewShotAgent
    },
    "Stage 2: Memory Agent": {
        "key": "memory",
        "description": "Maintains conversation history",
        "features": ["System prompt", "Multi-turn conversations", "Context awareness"],
        "class": MemoryAgent
    },
    "Stage 3: Tool Agent": {
        "key": "tool",
        "description": "Can use tools to search for information",
        "features": ["System prompt", "Flight search", "Hotel search", "Weather data"],
        "class": ToolAgent
    },
    "Stage 4: Reasoning Agent": {
        "key": "reasoning",
        "description": "Advanced agent with planning, reasoning, and retry logic",
        "features": ["All previous features", "Multi-step reasoning", "Tool chaining", "Failure handling", "Memory"],
        "class": ReasoningAgent
    }
}


def main():
    st.title("🤖 Bottom-Up AI Agents Explorer")
    st.markdown("---")
    
    # Sidebar for agent selection and settings
    with st.sidebar:
        st.header("Select Agent Type")
        
        # Agent selection
        selected_agent_name = st.radio(
            "Choose an agent stage:",
            options=list(AGENT_INFO.keys()),
            index=0
        )
        
        agent_info = AGENT_INFO[selected_agent_name]
        
        # Display agent details
        st.markdown(f"**Description:** {agent_info['description']}")
        st.markdown("**Features:**")
        for feature in agent_info['features']:
            st.markdown(f"• {feature}")
        
        st.markdown("---")
        
        # Settings
        st.header("Settings")
        model = st.selectbox(
            "Model:",
            options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0
        )
        
        temperature = st.slider(
            "Temperature:",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
        
        st.markdown("---")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Memory", type="secondary"):
                if hasattr(st.session_state.agent, 'clear_memory'):
                    st.session_state.agent.clear_memory()
                    st.success("Memory cleared!")
        
        with col2:
            if st.button("Reset All", type="secondary"):
                st.session_state.messages = []
                if hasattr(st.session_state.agent, 'clear_memory'):
                    st.session_state.agent.clear_memory()
                st.rerun()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "current_agent_type" not in st.session_state:
        st.session_state.current_agent_type = selected_agent_name
    
    # Check if agent type changed
    if st.session_state.current_agent_type != selected_agent_name:
        st.session_state.current_agent_type = selected_agent_name
        st.session_state.messages = []
        # Force recreation of agent
        if "agent" in st.session_state:
            del st.session_state.agent
    
    # Initialize or update agent
    if "agent" not in st.session_state or \
       st.session_state.get("model") != model or \
       st.session_state.get("temperature") != temperature:
        
        agent_class = agent_info["class"]
        st.session_state.agent = agent_class(
            model=model,
            temperature=temperature
        )
        st.session_state.model = model
        st.session_state.temperature = temperature
        
        # Clear conversation history for memory-enabled agents
        # The app will manage history, not the agents
        if hasattr(st.session_state.agent, 'conversation_history'):
            st.session_state.agent.conversation_history = []
    
    # Main chat interface
    st.header("Conversation")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            
            # Check if this message has reasoning traces (contains tool agent patterns)
            if message["role"] == "assistant" and any(emoji in content for emoji in ["🤔", "🔧", "🔄", "🤖", "💭"]):
                # Split reasoning from final content
                if "---" in content:
                    parts = content.split("---")
                    reasoning = "---".join(parts[:-1])
                    final_content = parts[-1].strip()
                    
                    if reasoning.strip():
                        with st.expander("🔍 View Tool Calls", expanded=False):
                            st.markdown(reasoning, unsafe_allow_html=True)
                    
                    if final_content:
                        st.markdown(final_content, unsafe_allow_html=True)
                    else:
                        st.markdown(content, unsafe_allow_html=True)
                else:
                    st.markdown(content, unsafe_allow_html=True)
            else:
                st.markdown(content, unsafe_allow_html=True)
    
    # Handle pending prompt from example buttons
    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pending_prompt
        del st.session_state.pending_prompt
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response with proper formatting
        with st.chat_message("assistant"):
            try:
                agent_type = st.session_state.current_agent_type
                is_tool_agent = "Tool" in agent_type or "Reasoning" in agent_type
                
                if is_tool_agent:
                    # For tool agents, get complete response then format with expandables
                    with st.spinner("Agent is working..."):
                        # Sync conversation history before processing
                        if hasattr(st.session_state.agent, 'conversation_history'):
                            st.session_state.agent.conversation_history = []
                            for msg in st.session_state.messages:
                                st.session_state.agent.conversation_history.append({
                                    "role": msg["role"],
                                    "content": msg["content"]
                                })
                        full_response = st.session_state.agent.process(prompt)
                    
                    # Split reasoning from final content
                    if "---" in full_response:
                        parts = full_response.split("---")
                        reasoning = "---".join(parts[:-1])
                        final_content = parts[-1].strip()
                        
                        if reasoning.strip():
                            with st.expander("🔍 View Tool Calls", expanded=False):
                                st.markdown(reasoning, unsafe_allow_html=True)
                        
                        if final_content:
                            st.markdown(final_content, unsafe_allow_html=True)
                        else:
                            st.markdown(full_response, unsafe_allow_html=True)
                    else:
                        st.markdown(full_response, unsafe_allow_html=True)
                else:
                    # Non-tool agents: normal streaming
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Sync conversation history before processing
                    if hasattr(st.session_state.agent, 'conversation_history'):
                        st.session_state.agent.conversation_history = []
                        for msg in st.session_state.messages:
                            st.session_state.agent.conversation_history.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                    
                    for chunk in st.session_state.agent.process_stream(prompt):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                    
                    message_placeholder.markdown(full_response, unsafe_allow_html=True)
                
                # Save to messages
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Clear agent's conversation history to prevent duplication
                if hasattr(st.session_state.agent, 'conversation_history'):
                    st.session_state.agent.conversation_history = []
            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Chat input
    if prompt := st.chat_input("Ask about travel plans..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response with streaming and expandable reasoning
        with st.chat_message("assistant"):
            try:
                agent_type = st.session_state.current_agent_type
                is_tool_agent = "Tool" in agent_type or "Reasoning" in agent_type
                
                if is_tool_agent:
                    # For tool agents, get complete response then format with expandables
                    with st.spinner("Agent is working..."):
                        # Sync conversation history before processing
                        if hasattr(st.session_state.agent, 'conversation_history'):
                            st.session_state.agent.conversation_history = []
                            for msg in st.session_state.messages:
                                st.session_state.agent.conversation_history.append({
                                    "role": msg["role"],
                                    "content": msg["content"]
                                })
                        full_response = st.session_state.agent.process(prompt)
                    
                    # Split reasoning from final content
                    if "---" in full_response:
                        parts = full_response.split("---")
                        reasoning = "---".join(parts[:-1])
                        final_content = parts[-1].strip()
                        
                        if reasoning.strip():
                            with st.expander("🔍 View Tool Calls", expanded=False):
                                st.markdown(reasoning, unsafe_allow_html=True)
                        
                        if final_content:
                            st.markdown(final_content, unsafe_allow_html=True)
                        else:
                            st.markdown(full_response, unsafe_allow_html=True)
                    else:
                        st.markdown(full_response, unsafe_allow_html=True)
                else:
                    # Non-tool agents: normal streaming
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Sync conversation history before processing
                    if hasattr(st.session_state.agent, 'conversation_history'):
                        st.session_state.agent.conversation_history = []
                        for msg in st.session_state.messages:
                            st.session_state.agent.conversation_history.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                    
                    for chunk in st.session_state.agent.process_stream(prompt):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                    
                    message_placeholder.markdown(full_response, unsafe_allow_html=True)
                
                # Save to messages
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Clear agent's conversation history to prevent duplication
                if hasattr(st.session_state.agent, 'conversation_history'):
                    st.session_state.agent.conversation_history = []
            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Example prompts
    if len(st.session_state.messages) == 0:
        st.markdown("### Try these example prompts:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗾 Plan a trip to Japan"):
                st.session_state.pending_prompt = "I want to plan a 3-day trip to Japan. What should I do?"
                st.rerun()
        
        with col2:
            if st.button("🌊 Beach vacation ideas"):
                st.session_state.pending_prompt = "I'm looking for a relaxing beach vacation in December. Any suggestions?"
                st.rerun()
        
        with col3:
            if st.button("🏔️ Adventure travel"):
                st.session_state.pending_prompt = "I want an adventure-filled trip with hiking and outdoor activities. Where should I go?"
                st.rerun()


if __name__ == "__main__":
    main()