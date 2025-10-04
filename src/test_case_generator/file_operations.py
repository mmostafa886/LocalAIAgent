"""
File Operations Module

This module handles all file input and output operations.
By centralizing file handling, we create a single place to manage file formats,
error handling, and any file-related features like backups or logging.

Design principle: Single Responsibility - this module only knows about files.
"""

import json
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from src.test_case_generator.csv_converter import CSVConverter


class FileOperations:
    """
    Handles file input and output for test case generation.

    This class encapsulates all file operations, making it easy to change
    file formats, add validation, or implement features like automatic backups
    without affecting the rest of the application.
    """

    @staticmethod
    def load_user_story(filepath: str) -> Tuple[str, List[str]]:
        """
        Load user story and acceptance criteria from a JSON file.

        Expected JSON format:
        {
            "user_story": "As a user...",
            "acceptance_criteria": ["criterion 1", "criterion 2", ...]
        }

        Args:
            filepath: Path to the input JSON file

        Returns:
            Tuple of (user_story, acceptance_criteria)

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
            ValueError: If required keys are missing
        """
        # Convert to Path object for better path handling
        file_path = Path(filepath)

        # Check file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Read and parse JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate required keys
        if "user_story" not in data:
            raise ValueError("JSON file missing required key: 'user_story'")

        if "acceptance_criteria" not in data:
            raise ValueError("JSON file missing required key: 'acceptance_criteria'")

        # Validate acceptance criteria is a list
        if not isinstance(data["acceptance_criteria"], list):
            raise ValueError("'acceptance_criteria' must be a list")

        return data["user_story"], data["acceptance_criteria"]

    @staticmethod
    def save_test_cases(
            test_cases: List[Dict[str, Any]],
            filepath: str,
            pretty: bool = True
    ) -> None:
        """
        Save test cases to a JSON file.

        Args:
            test_cases: List of test case dictionaries to save
            filepath: Path where the file should be saved
            pretty: If True, format JSON with indentation for readability

        Raises:
            IOError: If the file cannot be written
        """
        # Convert to Path object
        file_path = Path(filepath)

        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine JSON formatting
        indent = 2 if pretty else None

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, indent=indent, ensure_ascii=False)

    @staticmethod
    def save_with_metadata(
            test_cases: List[Dict[str, Any]],
            filepath: str,
            metadata: Dict[str, Any] = None
    ) -> None:
        """
        Save test cases with additional metadata.

        This creates a JSON file with both test cases and contextual information
        like generation time, model used, etc.

        Args:
            test_cases: List of test case dictionaries
            filepath: Output file path
            metadata: Optional dictionary of metadata to include
        """
        from datetime import datetime

        # Build output structure
        output = {
            "generated_at": datetime.now().isoformat(),
            "test_cases": test_cases,
            "count": len(test_cases)
        }

        # Add any additional metadata
        if metadata:
            output["metadata"] = metadata

        # Save to file
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    @staticmethod
    def save_test_cases_csv(
            test_cases: List[Dict[str, Any]],
            filepath: str,
            preserve_line_breaks: bool = True,
            include_summary: bool = False
    ) -> None:
        """
        Save test cases to a CSV file.

        Args:
            test_cases: List of test case dictionaries to save
            filepath: Path where the CSV file should be saved
            preserve_line_breaks: If True, preserve line breaks in Steps field
            include_summary: If True, add summary statistics at the top

        Raises:
            IOError: If the file cannot be written
        """
        converter = CSVConverter(preserve_line_breaks=preserve_line_breaks)
        converter.json_to_csv(
            test_cases=test_cases,
            output_path=filepath,
            include_summary=include_summary
        )

    @staticmethod
    def save_test_cases_both_formats(
            test_cases: List[Dict[str, Any]],
            base_path: str,
            preserve_line_breaks: bool = True
    ) -> Tuple[str, str]:
        """
        Save test cases in both JSON and CSV formats.

        This convenience method creates both file types with matching names
        but different extensions.

        Args:
            test_cases: List of test case dictionaries
            base_path: Base path for output (extension will be added/replaced)
            preserve_line_breaks: If True, preserve line breaks in CSV Steps field

        Returns:
            Tuple of (json_path, csv_path)
        """
        base = Path(base_path).with_suffix('')
        json_path = str(base.with_suffix('.json'))
        csv_path = str(base.with_suffix('.csv'))

        # Save JSON
        FileOperations.save_test_cases(test_cases, json_path)

        # Save CSV
        FileOperations.save_test_cases_csv(
            test_cases,
            csv_path,
            preserve_line_breaks=preserve_line_breaks
        )

        return json_path, csv_path

    @staticmethod
    def convert_json_to_csv(
            json_path: str,
            csv_path: Optional[str] = None,
            preserve_line_breaks: bool = True,
            include_summary: bool = False
    ) -> str:
        """
        Convert an existing JSON test cases file to CSV format.

        Args:
            json_path: Path to the JSON file to convert
            csv_path: Output CSV path. If None, replaces .json with .csv
            preserve_line_breaks: If True, preserve line breaks in Steps field
            include_summary: If True, add summary statistics at the top

        Returns:
            Path to the created CSV file
        """
        converter = CSVConverter(preserve_line_breaks=preserve_line_breaks)
        return converter.convert_file(
            input_path=json_path,
            output_path=csv_path,
            direction="json_to_csv"
        )

    @staticmethod
    def create_input_template(filepath: str) -> None:
        """
        Create a template input file for user stories.

        This is helpful for users who are starting fresh and need to know
        the expected file format.

        Args:
            filepath: Where to save the template file
        """
        template = {
            "user_story": "As a [user type], I want to [action] so that [benefit]",
            "acceptance_criteria": [
                "Criterion 1: Description of what should happen",
                "Criterion 2: Description of another requirement",
                "Criterion 3: Description of additional constraint"
            ]
        }

        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        print(f"Template created at: {filepath}")
        print("Edit this file with your user story and acceptance criteria.")