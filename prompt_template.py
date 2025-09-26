class PromptTemplate:
    """
    A template system for formatting prompts consistently.
    """
    def __init__(self, system_prompt: str, user_input: str, history: str):
        self.system_prompt = system_prompt
        self.user_input = user_input
        self.history = history

    def format_prompt(self, user_input) -> str:
        """
        Formats the prompt with the user input and history.
        """
        return f"""
{self.system_prompt}

Chat History: {self.history}

User Input: {user_input}
"""

    def output_inst(self) -> str:
        """
        Returns the instruction for the output format.

        Args:
            tool_descriptions (str): A formatted string of all available tool descriptions.

        Returns:
            str: The complete system prompt.
        """
        return f"""
    # OUTPUT INSTRUCTION:
    Your job is to solve complex problems by creating a series of tool calls. You must not respond conversationally. All output must be a JSON array of tool calls.
    You should respond with a JSON array of tool calls. Each tool call must be an object with an 'action', 'action_input', and 'result_id'.
    If a subsequent tool call depends on the output of a previous one, use a '$' prefix followed by the 'result_id' of the previous step.
    Use the format:
    ```json
    [
    {{
        "action": "tool_name",
        "action_input": ["arg1", "arg2"],
        "result_id": "step1_id"
    }},
    {{
        "action": "another_tool",
        "action_input": ["$step1_id", "argB"],
        "result_id": "step2_id"
    }},
    {{
        "action": "Final_Answer",
        "action_input": ["The final result is: @0 and @1", "$step1", "$step2"],
        "result_id": "final_result"
    }}
    ]
    ```

    If the task is coming to the final answer, use the action 'Final_Answer' with the final result as the 'action_input'.

    Example of a query like "Who are you?"
    ```json
    [
    {{
        "action": "Final_Answer",
        "action_input": ["I am a helpful AI Agent designed to use tools to answer questions."],
        "result_id": "final_result"
    }}
    ]
    ```

    Example of a query like "What is the current time?"
    ```json
    [
    {{
        "action": "get_time",
        "action_input": [],
        "result_id": "step1"
    }},
    {{
        "action": "Final_Answer",
        "action_input": ["The final result is: @0", "$step1"],
        "result_id": "final_result"
    }}
    ]
    ```

    You must provide a plan that completely solves the user's request.
    # END OF OUTPUT INSTRUCTION
    """
