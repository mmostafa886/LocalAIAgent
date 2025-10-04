"""
Model Client Module

This module handles all communication with the Ollama AI service.
By isolating model interaction, we create a clean abstraction layer that makes
it easy to switch models, adjust parameters, or even replace Ollama entirely
without affecting the rest of the application.

Design principle: Dependency Inversion - higher-level modules depend on this
abstraction rather than on Ollama directly.
"""

import ollama
from typing import Dict, Any


class OllamaClient:
    """
    Client for interacting with Ollama models.

    This class wraps the Ollama API and provides a clean interface for generating
    responses. It handles all the technical details of model communication,
    including parameter configuration and error handling.
    """

    def __init__(self, model_name: str = "llama3.1:8b"):
        """
        Initialize the Ollama client.

        Args:
            model_name: Name of the Ollama model to use

        Raises:
            ConnectionError: If Ollama service is not running or accessible
        """
        self.model_name = model_name
        self._verify_connection()

    def _verify_connection(self) -> None:
        """
        Verify that Ollama is running and accessible.

        This check happens at initialization so we fail fast if there's a problem
        with the Ollama service. It's better to catch configuration issues
        immediately rather than waiting until the first generation attempt.

        Raises:
            ConnectionError: If unable to connect to Ollama
        """
        try:
            # Try to list available models as a connectivity check
            ollama.list()
        except Exception as e:
            raise ConnectionError(
                f"Cannot connect to Ollama service. "
                f"Make sure Ollama is running. Error: {e}"
            )

    def generate(
            self,
            prompt: str,
            temperature: float = 0.3,
            top_p: float = 0.9,
            max_tokens: int = 4096
    ) -> str:
        """
        Generate a response from the model using the provided prompt.

        This method sends a prompt to the Ollama model and returns the generated
        text. It handles all the configuration of generation parameters like
        temperature and token limits.

        Args:
            prompt: The prompt to send to the model
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
                        Lower values are better for structured output like JSON
            top_p: Nucleus sampling parameter (0.0-1.0)
                   Controls diversity of word choice
            max_tokens: Maximum number of tokens to generate

        Returns:
            The generated text response from the model

        Raises:
            RuntimeError: If the model fails to generate a response
        """
        try:
            # Configure generation parameters
            # These parameters control how the model generates text
            options = {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            }

            # Call the Ollama API
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options=options
            )

            # Extract and return the generated text
            return response['response'].strip()

        except Exception as e:
            raise RuntimeError(f"Model generation failed: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the currently configured model.

        Returns:
            Dictionary containing model information
        """
        return {
            "model_name": self.model_name,
            "provider": "Ollama"
        }