"""
Test Case Generator - Main Orchestrator

This module coordinates all the components to generate test cases.
It represents the high-level workflow and business logic while delegating
specific responsibilities to specialized modules.

Design principle: Dependency Inversion - this orchestrator depends on
abstractions (the other modules) rather than concrete implementations.
This makes the system flexible and testable.
"""

import time
from typing import List, Dict, Any

from src.test_case_generator.prompt_builder import PromptBuilder
from src.test_case_generator.model_client import OllamaClient
from src.test_case_generator.response_parser import ResponseParser
from src.test_case_generator.validator import TestCaseValidator


class TestCaseGenerator:
    """
    Orchestrates the test case generation process.

    This class coordinates the entire workflow of generating test cases:
    1. Build an effective prompt
    2. Send it to the AI model
    3. Parse the response
    4. Validate the results
    5. Retry if necessary

    By delegating specific tasks to specialized components, this class remains
    focused on the high-level workflow and is easy to understand and maintain.
    """

    def __init__(
            self,
            model_name: str = "llama3.1:8b",
            include_edge_cases: bool = True,
            include_negative_tests: bool = True,
            strict_validation: bool = True
    ):
        """
        Initialize the test case generator with all necessary components.

        Args:
            model_name: Name of the Ollama model to use
            include_edge_cases: Whether to generate edge case test cases
            include_negative_tests: Whether to generate negative test cases
            strict_validation: Whether to enforce strict validation rules
        """
        # Initialize all components
        self.model_client = OllamaClient(model_name=model_name)
        self.prompt_builder = PromptBuilder(
            include_edge_cases=include_edge_cases,
            include_negative_tests=include_negative_tests
        )
        self.parser = ResponseParser()
        self.validator = TestCaseValidator(strict_mode=strict_validation)

        # Store configuration
        self.model_name = model_name

    def generate_test_cases(
            self,
            user_story: str,
            acceptance_criteria: List[str],
            temperature: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases for a user story (single attempt).

        This method performs one complete generation cycle without retry logic.
        It's useful when you want direct control over retry behavior or when
        you're confident the generation will succeed.

        Args:
            user_story: The user story to generate test cases for
            acceptance_criteria: List of acceptance criteria
            temperature: Model temperature (lower = more focused, higher = more creative)

        Returns:
            List of validated test case dictionaries

        Raises:
            ValueError: If generation or validation fails
        """
        # Step 1: Build the prompt
        prompt = self.prompt_builder.build_test_case_prompt(
            user_story=user_story,
            acceptance_criteria=acceptance_criteria
        )

        # Step 2: Generate response from model
        response_text = self.model_client.generate(
            prompt=prompt,
            temperature=temperature
        )

        # Step 3: Parse the response
        test_cases = self.parser.parse_test_cases(response_text)

        # Step 4: Validate the results
        # Generate expected criterion labels for validation
        expected_criteria = [f"AC{i+1}" for i in range(len(acceptance_criteria))]
        self.validator.validate_test_cases(test_cases, expected_criteria)

        return test_cases

    def generate_test_cases_with_retry(
            self,
            user_story: str,
            acceptance_criteria: List[str],
            max_retries: int = 5,
            temperature: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases with automatic retry on failure.

        This is the recommended method for production use. It implements robust
        retry logic that handles transient failures and AI output inconsistencies.

        The retry strategy:
        - Gradually increases temperature to encourage different approaches
        - Waits between retries to allow for transient issues to resolve
        - Provides clear progress feedback
        - Preserves error information for debugging

        Args:
            user_story: The user story to generate test cases for
            acceptance_criteria: List of acceptance criteria
            max_retries: Maximum number of attempts (default: 5)
            temperature: Base temperature (increases with each retry)

        Returns:
            List of validated test case dictionaries

        Raises:
            ValueError: If all retry attempts fail
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                # Calculate temperature for this attempt
                # Gradually increase to encourage variation on retries
                current_temperature = temperature + (attempt * 0.1)

                # Provide progress feedback
                if attempt == 0:
                    print("Generating test cases...")
                else:
                    print(f"Retry attempt {attempt + 1} of {max_retries}...")

                # Attempt to generate test cases
                test_cases = self.generate_test_cases(
                    user_story=user_story,
                    acceptance_criteria=acceptance_criteria,
                    temperature=current_temperature
                )

                # Success! Report if this took multiple attempts
                if attempt > 0:
                    print(f"✓ Success on attempt {attempt + 1}")

                return test_cases

            except (ValueError, RuntimeError) as e:
                # Save error for potential final failure message
                last_error = e

                # If this was the last attempt, don't wait or print retry message
                if attempt == max_retries - 1:
                    break

                # Inform user of the issue and that we're retrying
                print(f"✗ Attempt {attempt + 1} failed: {str(e)}")
                print(f"Waiting 2 seconds before retry...")

                # Brief pause before retry
                time.sleep(2)

        # All attempts failed - raise comprehensive error
        raise ValueError(
            f"Failed to generate valid test cases after {max_retries} attempts.\n"
            f"Last error: {str(last_error)}\n"
            f"Suggestions:\n"
            f"  - Check that Ollama is running properly\n"
            f"  - Verify the model '{self.model_name}' is available\n"
            f"  - Try simplifying the user story or reducing acceptance criteria\n"
            f"  - Increase max_retries for more complex scenarios"
        )

    def generate_and_analyze(
            self,
            user_story: str,
            acceptance_criteria: List[str],
            max_retries: int = 5
    ) -> Dict[str, Any]:
        """
        Generate test cases and return them with analysis.

        This convenience method combines generation with summary statistics,
        giving you both the test cases and insights about what was generated.

        Args:
            user_story: The user story to generate test cases for
            acceptance_criteria: List of acceptance criteria
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary containing:
                - test_cases: List of test case dictionaries
                - summary: Summary statistics about the test cases
                - model_info: Information about the model used
        """
        # Generate test cases with retry
        test_cases = self.generate_test_cases_with_retry(
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            max_retries=max_retries
        )

        # Generate summary statistics
        summary = self.parser.extract_summary_stats(test_cases)

        # Get model information
        model_info = self.model_client.get_model_info()

        return {
            "test_cases": test_cases,
            "summary": summary,
            "model_info": model_info
        }

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the generator configuration.

        Returns:
            Dictionary with configuration details
        """
        return {
            "model": self.model_name,
            "prompt_config": {
                "include_edge_cases": self.prompt_builder.include_edge_cases,
                "include_negative_tests": self.prompt_builder.include_negative_tests
            },
            "validation": {
                "strict_mode": self.validator.strict_mode
            }
        }