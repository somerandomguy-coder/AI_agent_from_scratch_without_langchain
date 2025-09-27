import os
from dotenv import load_dotenv
from google import genai

from llm_abstraction import LLM
from base_agent import BaseAgent, JsonOutputParser
from tools import ToolManager, BaseTool, get_current_time, calculator, Final_Answer
from agent_executor import AgentExecutor
from prompt_template import PromptTemplate

load_dotenv()

try:
    client = genai.Client()
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    print("Please make sure you have the GEMINI_API_KEY environment variable set.")
    exit()

if __name__ == "__main__":
    print("--- Initializing AI Agent Framework ---")

    # 1. Initialize the LLM Abstraction Layer
    llm = LLM(model_name="gemini-2.0-flash", client=client)

    # 2. Register Tools with the ToolManager
    tool_manager = ToolManager()
    calculator_tool = BaseTool(name="calculator", func=calculator)
    get_time_tool = BaseTool(name="get_time", func=get_current_time)
    final_answer = BaseTool(name="Final_Answer", func=Final_Answer)
    tool_manager.add_tool(get_time_tool)
    tool_manager.add_tool(calculator_tool)
    tool_manager.add_tool(final_answer)

    # 3. Create the Prompt Template to inform the agent about its tools
    tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in tool_manager.get_all_tools()])
    prompt_template = PromptTemplate(
        system_prompt=f"""
You are a brilliant computational agent. Your job is to solve complex problems by creating a series of tool calls.
You have access to the following tools:
{tool_descriptions}
""",
        user_input="{user_input}",
        history="{history}"
    )

    # 4. Create the Agent with the LLM
    agent = BaseAgent(llm=llm)

    # 5. Initialize the AgentExecutor with the Agent and ToolManager
    executor = AgentExecutor(agent=agent, tool_manager=tool_manager, prompt_template=prompt_template,max_iterations=1, dev_mode=True, json_output=True)

    print("\n--- Framework Initialized. Running Demo Task ---")

    # This prompt requires the agent to use two tools in a specific sequence.
    # It must search for the current year and then add 20 to that year.
    user_prompt = "What is the year 20 years from now?"

    # 6. Run the AgentExecutor
    final_output = executor.run(user_prompt)

    print("\n--- Task Complete ---")
    print(f"Result: {final_output}")
