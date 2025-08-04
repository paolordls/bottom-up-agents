# Bottom-Up AI Agents Tutorial

A progressive tutorial workshop for building AI agents, from simple prompts to complex multi-agent systems.

## Overview

This repository demonstrates how to build AI agents incrementally, with each stage building upon the previous one through reusable components.

## Architecture

```
src/
   core/               # Reusable foundation
      base_agent.py   # Abstract base class for all agents
      prompts.py      # Centralized prompt management
      tools.py        # Tool definitions and implementations
   agents/             # Progressive agent implementations
      simple_agent.py # Stage 0: Basic prompt-response
      few_shot_agent.py # Stage 1: With examples
      memory_agent.py # Stage 2: Conversation memory
      tool_agent.py   # Stage 3: Tool calling
      reasoning_agent.py   # Stage 4: Full agent loop
```

## Tutorial Stages

### Stage 0: Simple Prompt
- Basic LLM call with system prompt
- Single request, single response

### Stage 1: Few-Shot Prompting
- Includes examples to guide response format
- Improves consistency and quality

### Stage 2: Conversation Memory
- Maintains conversation history
- Context-aware responses

### Stage 3: Tool Calling
- Can search flights, hotels, weather
- Structured function calling

### Stage 4: Reasoning Agent
- Advanced planning capabilities
- Multiple tool calls per request
- Immediate retry on tool failures
- Iterative refinement
- Memory + tools combined
- Resilient error handling

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and add your OpenAI API key
3. Install dependencies:
   ```bash
   uv sync
   ```

## Running the Tutorials

### Interactive Streamlit App (Recommended)

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the Streamlit app
streamlit run app.py
```

The app will automatically open in your browser. You can:
- Select different agent stages from the sidebar
- Adjust model and temperature settings
- Have conversations with each agent type
- See how capabilities build from stage to stage

### Command Line Scripts

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run each stage
python tutorials/00_simple_prompt.py
python tutorials/01_few_shot.py
python tutorials/02_memory.py
python tutorials/03_tools.py
python tutorials/04_agent_loop.py
```

## Key Design Principles

1. **Inheritance**: Each agent builds on `BaseAgent`
2. **Composition**: Tools and prompts are separate, reusable components
3. **Progressive Enhancement**: Each stage adds one new capability
4. **Clear Separation**: Core logic vs. agent-specific behavior

## Extending the Framework

To add new capabilities:
1. Extend `BaseAgent` or an existing agent class
2. Add new tools to `src/core/tools.py`
3. Create new prompt templates in `src/core/prompts.py`
4. Combine components in new agent classes