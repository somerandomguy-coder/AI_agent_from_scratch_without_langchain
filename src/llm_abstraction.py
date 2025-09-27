from google import genai
import time

class LLM:
    """
    An abstraction class for a Large Language Model.

    This class encapsulates the specific API calls, making it easy to
    switch between different models or providers in the future.
    """
    def __init__(self, model_name: str, client: genai.Client):
        """
        Initializes the LLM.

        Args:
            model_name (str): The name of the model to use (e.g., "gemini-2.0-flash-lite").
            client (genai.Client): The Gemini API client instance.
        """
        self.model_name = model_name
        self.client = client

    def generate_content(self, contents: str):
        """
        Generates content from the LLM.

        Args:
            contents (str): The text prompt to send to the model.

        Returns:
            The raw response object from the API.
        """
        print(f"Calling LLM: {self.model_name}")
        start_time = time.time()
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents
        )
        end_time = time.time()
        print(f"LLM finished responding in {end_time-start_time:.2f} seconds.")
        return response
