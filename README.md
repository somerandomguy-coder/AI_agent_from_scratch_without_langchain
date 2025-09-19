# AI_agent_from_scratch_without_langchain
Using gemini API, and create feature similar to tool-calling, graph,... to have more control over agent, as well as acquiring deeper understanding to the framework

Project Phases (written by gemini 2.5 flash)

## Phase 1: Foundational Architecture
### Core Classes:
- Define a BaseAgent class with methods for plan, execute, and run.
- Create a BaseTool class and a ToolManager to register and retrieve tools.
- Implement an AgentExecutor to handle the main loop of reasoning and action.

### LLM Abstraction:
- Create an LLM class that abstracts away the specific API calls, making it easy to switch between models.
- Add a PromptTemplate system to manage and format prompts consistently.

### Core Tooling:
- Implement two essential tools: a SearchTool (e.g., using a mock API) and a CalculatorTool.

## Phase 2: Advanced Functionality & Integrations
### Memory & State:
- Design a BaseMemory class.
- Implement different types of memory, such as ConversationBufferMemory to store chat history and VectorStoreMemory to handle a knowledge base.
- Add state management to the AgentExecutor to track the agent's progress.

### Agentic Reasoning:
- Implement the "ReAct" (Reasoning and Acting) pattern within the agent's run loop. This involves prompting the LLM for a Thought, an Action, and an Observation.

### User Interface & Interaction:
- Build a simple command-line interface (CLI) to interact with the agent.
- Add a print method to the agent to display the "Thought" and "Action" for debugging and transparency.

## Phase 3: Testing and Deployment
### Testing:
- Write unit tests for the core classes (BaseAgent, BaseTool, AgentExecutor).
- Create integration tests to ensure the agent and tools work together correctly on simple tasks.

### Package & Distribute:
- Structure the project with setup.py or pyproject.toml.
- Add comprehensive documentation explaining how to use the framework.
- Containerize the application using Dockerfile to ensure it can be run in any environment.
