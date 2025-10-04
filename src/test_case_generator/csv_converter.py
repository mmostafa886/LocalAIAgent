"""
CSV Converter Module

This module handles conversion of test case JSON data to CSV format.
CSV is often preferred for importing into test management tools, spreadsheets,
and for sharing with non-technical stakeholders.

Design principle: Single Responsibility - this module only knows how to convert
data formats. It doesn't generate, validate, or understand test cases beyond
their structure.
"""

import csv
from typing import List, Dict, Any
from pathlib import Path


class CSVConverter:
    """
    Converts test case data between JSON and CSV formats.

    This class handles the complexities of converting structured test case data
    into flat CSV format while preserving readability and data integrity.
    """

    # Define the standard field order for CSV output
    # This ensures consistent column ordering across all exports
    FIELD_ORDER = [
        "Test Case ID",
        "Test Case Title",
        "Steps",
        "Expected Result",
        "Linked Acceptance Criterion"
    ]

    def __init__(self, preserve_line_breaks: bool = True):
        """
        Initialize the CSV converter.

        Args:
            preserve_line_breaks: If True, keep \n as actual line breaks in CSV.
                                 If False, replace with semicolons for single-line cells.
        """
        self.preserve_line_breaks = preserve_line_breaks

    def json_to_csv(
            self,
            test_cases: List[Dict[str, Any]],
            output_path: str,
            include_summary: bool = False
    ) -> None:
        """
        Convert test cases from JSON format to CSV file.

        This method creates a CSV file with proper escaping and formatting.
        Excel and Google Sheets will correctly handle multi-line cells when
        preserve_line_breaks is True.

        Args:
            test_cases: List of test case dictionaries from JSON
            output_path: Path where the CSV file should be saved
            include_summary: If True, add summary rows at the top of the CSV

        Raises:
            ValueError: If test_cases is empty or malformed
            IOError: If the file cannot be written
        """
        if not test_cases:
            raise ValueError("No test cases to convert")

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Open file with proper encoding
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=self.FIELD_ORDER,
                extrasaction='ignore'  # Ignore any extra fields not in FIELD_ORDER
            )

            # Add summary section if requested
            if include_summary:
                self._write_summary(writer, test_cases)

            # Write header row
            writer.writeheader()

            # Write test case rows
            for test_case in test_cases:
                # Process the test case for CSV format
                processed_case = self._process_test_case_for_csv(test_case)
                writer.writerow(processed_case)

        print(f"CSV file created: {output_path}")

    def _process_test_case_for_csv(self, test_case: Dict[str, Any]) -> Dict[str, str]:
        """
        Process a test case dictionary for CSV output.

        This method handles the conversion of fields, particularly the Steps field
        which may contain line breaks that need special handling.

        Args:
            test_case: Original test case dictionary

        Returns:
            Processed dictionary ready for CSV writing
        """
        processed = {}

        for field in self.FIELD_ORDER:
            value = test_case.get(field, "")

            # Special handling for Steps field
            if field == "Steps" and value:
                if self.preserve_line_breaks:
                    # Replace \n with actual line breaks
                    # CSV will quote the field automatically, and Excel handles this correctly
                    value = value.replace("\\n", "\n")
                else:
                    # Replace \n with semicolons for single-line format
                    value = value.replace("\\n", "; ")

            processed[field] = str(value)

        return processed

    def _write_summary(self, writer: csv.DictWriter, test_cases: List[Dict[str, Any]]) -> None:
        """
        Write a summary section at the top of the CSV.

        This adds metadata rows that provide context about the test cases.
        Most CSV readers will show these as regular rows, but they provide
        useful information when the file is shared.

        Args:
            writer: CSV DictWriter instance
            test_cases: List of test cases for calculating statistics
        """
        # Calculate summary statistics
        total_cases = len(test_cases)
        criteria_covered = set(tc.get("Linked Acceptance Criterion", "") for tc in test_cases)

        # Write summary rows
        # We use the first field for labels and second field for values
        summary_data = [
            {self.FIELD_ORDER[0]: "SUMMARY", self.FIELD_ORDER[1]: ""},
            {self.FIELD_ORDER[0]: "Total Test Cases", self.FIELD_ORDER[1]: str(total_cases)},
            {self.FIELD_ORDER[0]: "Acceptance Criteria Covered",
             self.FIELD_ORDER[1]: ", ".join(sorted(criteria_covered))},
            {self.FIELD_ORDER[0]: "", self.FIELD_ORDER[1]: ""},  # Empty row for separation
        ]

        for row in summary_data:
            writer.writerow(row)

    def csv_to_json(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        Convert a CSV file back to JSON format.

        This allows round-trip conversion if users edit test cases in CSV
        and want to convert back to JSON format.

        Args:
            csv_path: Path to the CSV file to convert

        Returns:
            List of test case dictionaries

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        csv_file = Path(csv_path)

        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        test_cases = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip summary rows or empty rows
                if not row.get("Test Case ID") or row["Test Case ID"].startswith("SUMMARY"):
                    continue

                # Process the row back to JSON format
                test_case = self._process_csv_row_to_json(row)
                test_cases.append(test_case)

        return test_cases

    def _process_csv_row_to_json(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a CSV row back to JSON format.

        This reverses the processing done in _process_test_case_for_csv,
        converting actual line breaks back to \n notation.

        Args:
            row: Dictionary representing one CSV row

        Returns:
            Test case dictionary in JSON format
        """
        test_case = {}

        for field in self.FIELD_ORDER:
            value = row.get(field, "").strip()

            # Special handling for Steps field
            if field == "Steps" and value:
                if self.preserve_line_breaks:
                    # Convert actual line breaks back to \n notation
                    value = value.replace("\n", "\\n")
                else:
                    # Convert semicolons back to \n notation
                    value = value.replace("; ", "\\n")

            test_case[field] = value

        return test_case

    def convert_file(
            self,
            input_path: str,
            output_path: str = None,
            direction: str = "json_to_csv"
    ) -> str:
        """
        Convenience method to convert files in either direction.

        This method handles file reading, conversion, and writing in one call,
        with automatic output path generation if needed.

        Args:
            input_path: Path to input file (JSON or CSV)
            output_path: Path for output file. If None, generates automatically.
            direction: Either "json_to_csv" or "csv_to_json"

        Returns:
            Path to the created output file

        Raises:
            ValueError: If direction is invalid or input file format is wrong
        """
        input_file = Path(input_path)

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Generate output path if not provided
        if output_path is None:
            if direction == "json_to_csv":
                output_path = str(input_file.with_suffix('.csv'))
            else:
                output_path = str(input_file.with_suffix('.json'))

        # Perform conversion based on direction
        if direction == "json_to_csv":
            # Read JSON file
            import json
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle both raw test case arrays and wrapped formats
            if isinstance(data, dict) and "test_cases" in data:
                test_cases = data["test_cases"]
            elif isinstance(data, list):
                test_cases = data
            else:
                raise ValueError("Invalid JSON format. Expected array or object with 'test_cases' key.")

            # Convert to CSV
            self.json_to_csv(test_cases, output_path)

        elif direction == "csv_to_json":
            # Read CSV and convert to JSON
            test_cases = self.csv_to_json(input_path)

            # Write JSON file
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(test_cases, f, indent=2, ensure_ascii=False)

            print(f"JSON file created: {output_path}")

        else:
            raise ValueError(f"Invalid direction: {direction}. Use 'json_to_csv' or 'csv_to_json'")

        return output_path