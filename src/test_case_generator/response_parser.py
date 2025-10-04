"""
Response Parser Module

This module handles parsing AI model responses into structured data.
AI models sometimes produce output with extra text or formatting, so this
parser robustly extracts the JSON data we need.

Design principle: Single Responsibility - this module only knows how to parse
responses. It doesn't make assumptions about what's valid or what to do with
the data once parsed.
"""

import json
import re
from typing import List, Dict, Any


class ResponseParser:
    """
    Parses AI model responses into structured test case data.

    This class handles the complexity of extracting valid JSON from AI-generated
    text that might include extra commentary, markdown formatting, or other
    unexpected elements. It implements robust parsing strategies to handle
    real-world AI output.
    """

    def parse_test_cases(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse test cases from AI-generated response text.

        This method attempts multiple parsing strategies to extract valid JSON
        from the response. It handles common issues like:
        - Extra explanatory text before or after the JSON
        - Markdown code blocks wrapping the JSON
        - Escaped characters that need unescaping

        Args:
            response_text: Raw text response from the AI model

        Returns:
            List of test case dictionaries

        Raises:
            ValueError: If no valid JSON can be extracted from the response
        """
        # Try different parsing strategies in order of likelihood
        strategies = [
            self._parse_direct_json,
            self._parse_json_from_markdown,
            self._parse_json_with_boundaries,
        ]

        for strategy in strategies:
            try:
                test_cases = strategy(response_text)
                if test_cases:
                    return test_cases
            except (json.JSONDecodeError, ValueError):
                # This strategy didn't work, try the next one
                continue

        # If all strategies failed, raise an informative error
        raise ValueError(
            "Unable to parse valid JSON from response. "
            "The AI may not have followed the required format."
        )

    def _parse_direct_json(self, text: str) -> List[Dict[str, Any]]:
        """
        Attempt to parse the text directly as JSON.

        This is the simplest strategy - just try to parse the entire response
        as JSON. This works when the AI perfectly follows instructions and
        outputs only JSON with no extra text.

        Args:
            text: Response text to parse

        Returns:
            Parsed test cases

        Raises:
            json.JSONDecodeError: If text is not valid JSON
        """
        return json.loads(text.strip())

    def _parse_json_from_markdown(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract and parse JSON from markdown code blocks.

        Sometimes AI models wrap JSON in markdown code blocks like:
        ```json
        [...]
        ```
        This strategy extracts the content between code fences.

        Args:
            text: Response text potentially containing markdown

        Returns:
            Parsed test cases

        Raises:
            ValueError: If no code block found or invalid JSON
        """
        # Look for JSON within markdown code blocks
        pattern = r'```(?:json)?\s*(\[.*?\])\s*```'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            json_str = match.group(1)
            return json.loads(json_str)

        raise ValueError("No markdown code block found")

    def _parse_json_with_boundaries(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract JSON by finding array boundaries.

        This strategy looks for the first '[' and last ']' in the text,
        assuming these mark the boundaries of the JSON array. This handles
        cases where the AI adds explanatory text before or after the JSON.

        Args:
            text: Response text containing JSON

        Returns:
            Parsed test cases

        Raises:
            ValueError: If boundaries not found or invalid JSON
        """
        # Find the first '[' and last ']' to identify JSON boundaries
        start_idx = text.find('[')
        end_idx = text.rfind(']')

        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            raise ValueError("No JSON array boundaries found")

        # Extract the JSON substring
        json_str = text[start_idx:end_idx + 1]

        # Parse and return
        return json.loads(json_str)

    def extract_summary_stats(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract summary statistics from parsed test cases.

        This utility method provides quick insights into the generated test cases,
        such as how many test cases were generated and which acceptance criteria
        are covered.

        Args:
            test_cases: List of parsed test case dictionaries

        Returns:
            Dictionary containing summary statistics
        """
        # Count total test cases
        total_cases = len(test_cases)

        # Extract unique acceptance criteria covered
        criteria_covered = set()
        for tc in test_cases:
            criterion = tc.get("Linked Acceptance Criterion", "")
            if criterion:
                criteria_covered.add(criterion)

        return {
            "total_test_cases": total_cases,
            "criteria_covered": sorted(list(criteria_covered)),
            "coverage_count": len(criteria_covered)
        }