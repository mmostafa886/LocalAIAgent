"""
Prompt Builder Module

This module is responsible for constructing prompts that will be sent to the AI model.
By isolating prompt construction, we can easily modify and experiment with different
prompt strategies without affecting other parts of the system.

Design principle: Single Responsibility - this module only knows how to build prompts.
It doesn't know about models, parsing, or validation.
"""

from typing import List


class PromptBuilder:
    """
    Constructs prompts for test case generation.

    This class encapsulates all the logic for creating effective prompts.
    As you refine your prompting strategy through experimentation, all changes
    happen in this one place without rippling through the rest of your codebase.
    """

    def __init__(self, include_edge_cases: bool = True, include_negative_tests: bool = True):
        """
        Initialize the prompt builder with configuration options.

        Args:
            include_edge_cases: Whether to request edge case test cases
            include_negative_tests: Whether to request negative test cases
        """
        self.include_edge_cases = include_edge_cases
        self.include_negative_tests = include_negative_tests

    def build_test_case_prompt(
            self,
            user_story: str,
            acceptance_criteria: List[str]
    ) -> str:
        """
        Build a comprehensive prompt for test case generation.

        This method constructs a prompt that instructs the AI to generate test cases
        in a specific JSON format. The prompt includes the user story, acceptance
        criteria, and detailed instructions about the desired output format.

        Args:
            user_story: The user story describing the feature to test
            acceptance_criteria: List of acceptance criteria that must be met

        Returns:
            A formatted prompt string ready to send to the AI model
        """
        # Format acceptance criteria with clear labels
        # This makes it easy for the AI to reference specific criteria
        ac_formatted = self._format_acceptance_criteria(acceptance_criteria)

        # Build the test coverage instructions based on configuration
        coverage_instructions = self._build_coverage_instructions()

        # Construct the complete prompt with all sections
        prompt = f"""You are an expert SDET (Software Development Engineer in Test). Generate comprehensive test cases for the following user story.

USER STORY:
{user_story}

ACCEPTANCE CRITERIA:
{ac_formatted}

INSTRUCTIONS:
1. Generate test cases that cover ALL acceptance criteria
{coverage_instructions}
3. Make steps clear, specific, and actionable
4. Each test case must link to at least one acceptance criterion using the AC labels (AC1, AC2, etc.)
5. Return ONLY a valid JSON array with NO additional text, explanations, or markdown formatting before or after

REQUIRED JSON FORMAT:
[
  {{
    "Test Case ID": "TC001",
    "Test Case Title": "Brief description of what is being tested",
    "Steps": "1. First step\\n2. Second step\\n3. Third step",
    "Expected Result": "Clear description of expected outcome",
    "Linked Acceptance Criterion": "AC1"
  }}
]

CRITICAL: Output must be valid JSON only. Do not include any text before the opening bracket [ or after the closing bracket ].

Generate the test cases now:"""

        return prompt

    def _format_acceptance_criteria(self, criteria: List[str]) -> str:
        """
        Format acceptance criteria with numbered labels.

        This helper method takes a list of criteria and formats them with
        AC1, AC2, etc. labels. These labels make it easy for the AI to reference
        specific criteria in the generated test cases.

        Args:
            criteria: List of acceptance criteria strings

        Returns:
            Formatted string with labeled criteria
        """
        return "\n".join([
            f"AC{i+1}: {criterion.strip()}"
            for i, criterion in enumerate(criteria)
        ])

    def _build_coverage_instructions(self) -> str:
        """
        Build test coverage instructions based on configuration.

        This method constructs the instruction text that tells the AI what types
        of test cases to generate. The instructions vary based on the builder's
        configuration settings.

        Returns:
            Formatted instruction text for test coverage
        """
        instructions = []

        instructions.append("2. Include positive test cases (happy path scenarios)")

        if self.include_negative_tests:
            instructions.append("   Include negative test cases (error scenarios)")

        if self.include_edge_cases:
            instructions.append("   Include edge cases and boundary conditions")

        return "\n".join(instructions)