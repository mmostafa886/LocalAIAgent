"""
Validator Module

This module validates test case data to ensure it meets all requirements.
By separating validation logic, we create a single source of truth for what
constitutes a valid test case. This makes it easy to add new validation rules
or modify existing ones without affecting other parts of the system.

Design principle: Single Responsibility - this module only validates data.
It doesn't parse, generate, or modify data.
"""

from typing import List, Dict, Any, Set


class TestCaseValidator:
    """
    Validates test case data structures.

    This class encapsulates all the logic for determining whether test case data
    is valid. It checks for required fields, proper formatting, and logical
    consistency. By centralizing validation, we ensure consistent quality checks
    across the entire application.
    """

    # Define required fields as a class constant
    # This makes it easy to see and modify the requirements in one place
    REQUIRED_FIELDS = [
        "Test Case ID",
        "Test Case Title",
        "Steps",
        "Expected Result",
        "Linked Acceptance Criterion"
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, enforce all validation rules strictly.
                        If False, allow some flexibility (useful for testing)
        """
        self.strict_mode = strict_mode

    def validate_test_cases(
            self,
            test_cases: List[Dict[str, Any]],
            expected_criteria: List[str] = None
    ) -> None:
        """
        Validate a list of test cases.

        This is the main validation method. It performs comprehensive checks
        on the test cases to ensure they meet all requirements. If any validation
        fails, it raises a descriptive error.

        Args:
            test_cases: List of test case dictionaries to validate
            expected_criteria: Optional list of acceptance criteria that should
                             be covered (e.g., ["AC1", "AC2", "AC3"])

        Raises:
            ValueError: If validation fails, with a detailed error message
        """
        # Check that we have at least one test case
        if not test_cases:
            raise ValueError("No test cases to validate")

        # Validate each test case individually
        for i, test_case in enumerate(test_cases, start=1):
            self._validate_single_test_case(test_case, index=i)

        # Validate test case IDs are unique
        self._validate_unique_ids(test_cases)

        # If expected criteria provided, check coverage
        if expected_criteria and self.strict_mode:
            self._validate_criteria_coverage(test_cases, expected_criteria)

    def _validate_single_test_case(self, test_case: Dict[str, Any], index: int) -> None:
        """
        Validate a single test case.

        This method checks that a test case has all required fields and that
        each field contains valid data.

        Args:
            test_case: Test case dictionary to validate
            index: Position of this test case in the list (for error messages)

        Raises:
            ValueError: If validation fails
        """
        # Check for required fields
        missing_fields = [
            field for field in self.REQUIRED_FIELDS
            if field not in test_case
        ]

        if missing_fields:
            raise ValueError(
                f"Test case {index} is missing required fields: {', '.join(missing_fields)}"
            )

        # Validate Test Case ID format
        self._validate_test_case_id(test_case["Test Case ID"], index)

        # Validate that fields are not empty
        self._validate_non_empty_fields(test_case, index)

        # Validate acceptance criterion format
        self._validate_criterion_format(
            test_case["Linked Acceptance Criterion"],
            index
        )

    def _validate_test_case_id(self, test_case_id: str, index: int) -> None:
        """
        Validate the format of a Test Case ID.

        Test Case IDs should follow the format TC001, TC002, etc.
        This method ensures consistency in naming.

        Args:
            test_case_id: The test case ID to validate
            index: Position of this test case (for error messages)

        Raises:
            ValueError: If the ID format is invalid
        """
        if not isinstance(test_case_id, str):
            raise ValueError(f"Test case {index}: ID must be a string")

        # In strict mode, enforce TC### format
        if self.strict_mode:
            if not test_case_id.startswith("TC"):
                raise ValueError(
                    f"Test case {index}: ID '{test_case_id}' should start with 'TC'"
                )

            # Check that it has a number after TC
            number_part = test_case_id[2:]
            if not number_part.isdigit():
                raise ValueError(
                    f"Test case {index}: ID '{test_case_id}' should have a number after 'TC'"
                )

    def _validate_non_empty_fields(self, test_case: Dict[str, Any], index: int) -> None:
        """
        Ensure all required fields have non-empty values.

        Args:
            test_case: Test case to check
            index: Position of this test case (for error messages)

        Raises:
            ValueError: If any required field is empty
        """
        for field in self.REQUIRED_FIELDS:
            value = test_case.get(field)

            # Check for None or empty string
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(
                    f"Test case {index}: Field '{field}' cannot be empty"
                )

    def _validate_criterion_format(self, criterion: str, index: int) -> None:
        """
        Validate acceptance criterion format.

        Criteria should be in the format AC1, AC2, etc.

        Args:
            criterion: The criterion string to validate
            index: Position of this test case (for error messages)

        Raises:
            ValueError: If criterion format is invalid
        """
        if not isinstance(criterion, str):
            raise ValueError(
                f"Test case {index}: Linked Acceptance Criterion must be a string"
            )

        # In strict mode, enforce AC# format
        if self.strict_mode:
            if not criterion.startswith("AC"):
                raise ValueError(
                    f"Test case {index}: Criterion '{criterion}' should start with 'AC'"
                )

    def _validate_unique_ids(self, test_cases: List[Dict[str, Any]]) -> None:
        """
        Ensure all test case IDs are unique.

        Duplicate IDs would cause confusion in test management systems,
        so we enforce uniqueness.

        Args:
            test_cases: List of test cases to check

        Raises:
            ValueError: If duplicate IDs are found
        """
        ids = [tc["Test Case ID"] for tc in test_cases]
        unique_ids = set(ids)

        if len(ids) != len(unique_ids):
            # Find which IDs are duplicated
            duplicates = [id for id in unique_ids if ids.count(id) > 1]
            raise ValueError(
                f"Duplicate test case IDs found: {', '.join(duplicates)}"
            )

    def _validate_criteria_coverage(
            self,
            test_cases: List[Dict[str, Any]],
            expected_criteria: List[str]
    ) -> None:
        """
        Check that all expected acceptance criteria are covered by test cases.

        This validation ensures that test cases exist for every acceptance
        criterion in the user story. This helps catch gaps in test coverage.

        Args:
            test_cases: Generated test cases
            expected_criteria: List of criteria that should be covered (e.g., ["AC1", "AC2"])

        Raises:
            ValueError: If some criteria are not covered by any test case
        """
        # Extract all criteria covered by test cases
        covered_criteria: Set[str] = set()
        for tc in test_cases:
            criterion = tc["Linked Acceptance Criterion"]
            covered_criteria.add(criterion)

        # Check for missing coverage
        expected_set = set(expected_criteria)
        missing_criteria = expected_set - covered_criteria

        if missing_criteria:
            raise ValueError(
                f"Some acceptance criteria are not covered by any test case: "
                f"{', '.join(sorted(missing_criteria))}"
            )

    def get_validation_report(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a validation report for test cases.

        This method performs all validations and returns a report instead of
        raising exceptions. Useful for getting a complete picture of validation
        status rather than failing on the first error.

        Args:
            test_cases: Test cases to validate

        Returns:
            Dictionary containing validation results and any issues found
        """
        report = {
            "is_valid": True,
            "total_test_cases": len(test_cases),
            "issues": []
        }

        try:
            self.validate_test_cases(test_cases)
        except ValueError as e:
            report["is_valid"] = False
            report["issues"].append(str(e))

        return report