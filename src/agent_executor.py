from typing import Dict, Any, List
from base_agent import BaseAgent
from tools import ToolManager
from prompt_template import PromptTemplate
import json


class AgentExecutor:
    """
    The AgentExecutor is responsible for managing the execution of an agent's
    reasoning and tool-use loop.
    """
    def __init__(self, agent: BaseAgent, tool_manager: ToolManager, prompt_template: PromptTemplate, max_iterations: int = 5, history: str = None, dev_mode: bool = False, json_output = False):
        """
        Initializes the AgentExecutor.

        Args:
            agent (BaseAgent): The agent instance to execute.
            tool_manager (ToolManager): The manager for all available tools.
            prompt_template (PromptTemplate): The template for formatting prompts.
            max_iterations (int): The maximum number of iterations for the execution loop.
            history (str): The initial chat history.
            dev_mode (bool): If True, enables verbose logging for debugging.
            json_output (bool): If True, output will be in json format (agent will be able to work with tool)
        """
        self.agent = agent
        self.tool_manager = tool_manager
        self.prompt_template = prompt_template
        self.max_iterations = max_iterations
        self.history = history
        self.dev_mode = dev_mode
        self.json_output = json_output
        self.context = {}

    def run(self, user_input: str) -> str:
        """
        Executes the agent's reasoning loop based on the user's input.

        Args:
            user_input (str): The user's initial query.

        Returns:
            str: The final answer from the agent.
        """
        current_history = self.history if self.history else ""
        current_input = user_input

        for i in range(self.max_iterations):
            if self.dev_mode:
                print(f"\n--- Iteration {i + 1}/{self.max_iterations} ---")

            formatted_prompt = self.prompt_template.format_prompt(
                user_input=current_input
            )
            if self.json_output:
                formatted_prompt = formatted_prompt + self.prompt_template.output_inst()

            if self.dev_mode:
                print(f"Agent's Input Prompt: {formatted_prompt}")

            try:
                response_obj = self.agent.run(formatted_prompt)
                response_plan = response_obj["content"]
                if isinstance(response_plan, str):
                    return response_plan, response_obj

                if self.dev_mode:
                    print("Agent's Plan Received:")
                    if isinstance(response_plan, list):
                        print(json.dumps(response_plan, indent=2))

                if not isinstance(response_plan, list):
                    return f"The agent failed to provide a valid plan. Response was: '{response_plan}'"

                for action in response_plan:
                    tool_name = action.get("action")
                    action_input = action.get("action_input")
                    result_id = action.get("result_id")

                    if tool_name == "Terminate":
                        return "Task has finished within the iteration." + self.context.get("final_result"), response_obj

                    resolved_input = self._resolve_dependencies(action_input)

                    if self.dev_mode:
                        print(f"  -> Executing tool: '{tool_name}' with inputs: {resolved_input}")

                    tool = self.tool_manager.get_tool(tool_name)
                    tool_output = tool.run(*resolved_input)

                    self.context[result_id] = tool_output
                    if self.dev_mode:
                        print(f"    Tool output stored as '{result_id}': {tool_output} \n")

                    if tool_name == "Final_Answer":
                        return tool_output, response_obj

                current_input = f"User input: {user_input}, Response plan: {response_plan}, Iteration: {i}/{self.max_iterations}, Context board: {self.context}. Please continue with the plan. If the final answer has reached and have no problem, return a list of action with only one action name 'Terminate'"

            except (ValueError, TypeError, KeyError) as e:
                print(f"An error occurred during execution: {e}")
                return f"I encountered an error and could not complete the task: {e}"

        return "Max iterations reached without a final answer.", response_obj

    def _resolve_dependencies(self, action_input: Any) -> List:
        """
        Resolves input dependencies from the context.
        """
        if isinstance(action_input, list):
            return [self._resolve_dependencies_recursive(item) for item in action_input]

    def _resolve_dependencies_recursive(self, item: Any) -> Any:
        if isinstance(item, str) and item.startswith("$"):
            key = item[1:]
            if key in self.context:
                return self.context[key]
            else:
                raise ValueError(f"Dependency '{key}' not found in context.")
        elif isinstance(item, list) or isinstance(item, tuple):
            return [self._resolve_dependencies_recursive(i) for i in item]
        elif isinstance(item, dict):
            return {k: self._resolve_dependencies_recursive(v) for k, v in item.items()}
        return item


