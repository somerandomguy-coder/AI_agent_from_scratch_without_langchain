import time
import json
from llm_abstraction import LLM

class JsonOutputParser:
    """A parser to extract JSON plans from the agent's raw text output."""
    def parse(self, text: str):
        """
        Parses the raw text output to find and load a JSON object.

        Args:
            text (str): The raw text output from the LLM.

        Returns:
            A Python object (dict or list) parsed from the JSON,
            or the original text if no JSON is found.
        """
        try:
            if '```json' in text:
                json_str = text.split('```json')[1].split('```')[0].strip()
                return json.loads(json_str)
            else:
                return text
        except (json.JSONDecodeError, IndexError) as e:
            print(f"Error parsing JSON: {e}")
            return text

class BaseAgent:
    """
    The core agent that interacts with the LLM.
    It now uses an LLM abstraction layer and a parser to return structured output.
    """
    def __init__(self, llm: LLM):
        """
        Initializes the BaseAgent.

        Args:
            llm (LLM): The LLM abstraction instance.
        """
        self.llm = llm
        self.parser = JsonOutputParser()

    def run(self, prompt: str):
        print("Agent is running, vroom vroom!")

        # The LLM call is now handled by the LLM abstraction class.
        response, responding_time= self.llm.generate_content(contents=prompt)

        # Now, we use the parser before returning the output.
        print(f"Total token usage: {response.usage_metadata.total_token_count}")
        response_text = self.parser.parse(response.text)
        response_obj = {"content":response_text,
                        "duration": responding_time,
                        "token_usage": response.usage_metadata.total_token_count}
        return response_obj

