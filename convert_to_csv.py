"""
Test Case Format Converter

A standalone utility to convert test case files between JSON and CSV formats.
This is useful when you have existing test case files and need them in a
different format.

Usage:
    # Convert JSON to CSV
    python convert_to_csv.py test_cases.json

    # Convert CSV to JSON
    python convert_to_csv.py test_cases.csv

    # Specify output path
    python convert_to_csv.py test_cases.json --output my_tests.csv

    # Use single-line format for steps
    python convert_to_csv.py test_cases.json --single-line
"""

import argparse
import sys
from pathlib import Path

from src.test_case_generator.csv_converter import CSVConverter


def main():
    """
    Main entry point for the conversion utility.
    """
    parser = argparse.ArgumentParser(
        description='Convert test case files between JSON and CSV formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert JSON to CSV (auto-detects format from extension)
  python convert_to_csv.py test_cases.json
  
  # Convert CSV back to JSON
  python convert_to_csv.py test_cases.csv
  
  # Specify output file explicitly
  python convert_to_csv.py input.json --output custom_name.csv
  
  # Use single-line format for steps (semicolon-separated)
  python convert_to_csv.py test_cases.json --single-line
  
  # Add summary statistics to CSV
  python convert_to_csv.py test_cases.json --summary
        """
    )

    # Input file
    parser.add_argument(
        'input_file',
        help='Input file (JSON or CSV) to convert'
    )

    # Output file
    parser.add_argument(
        '--output', '-o',
        help='Output file path (auto-generated if not specified)'
    )

    # CSV formatting options
    parser.add_argument(
        '--single-line',
        action='store_true',
        help='For CSV output: use single-line format for Steps (semicolon-separated)'
    )

    parser.add_argument(
        '--summary',
        action='store_true',
        help='For CSV output: include summary statistics at the top'
    )

    # Parse arguments
    args = parser.parse_args()

    # Check input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        return 1

    # Determine conversion direction from file extension
    input_ext = input_path.suffix.lower()

    if input_ext == '.json':
        direction = 'json_to_csv'
        output_ext = '.csv'
    elif input_ext == '.csv':
        direction = 'csv_to_json'
        output_ext = '.json'
    else:
        print(f"Error: Unsupported file format: {input_ext}", file=sys.stderr)
        print("Supported formats: .json, .csv", file=sys.stderr)
        return 1

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Auto-generate output path
        output_path = str(input_path.with_suffix(output_ext))

    # Perform conversion
    try:
        print(f"Converting {input_path.name} to {Path(output_path).suffix[1:].upper()} format...")

        if direction == 'json_to_csv':
            # JSON to CSV conversion with options
            converter = CSVConverter(preserve_line_breaks=not args.single_line)

            # Read JSON
            import json
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle both formats
            if isinstance(data, dict) and "test_cases" in data:
                test_cases = data["test_cases"]
            elif isinstance(data, list):
                test_cases = data
            else:
                print("Error: Invalid JSON format", file=sys.stderr)
                return 1

            # Convert
            converter.json_to_csv(
                test_cases=test_cases,
                output_path=output_path,
                include_summary=args.summary
            )

        else:
            # CSV to JSON conversion
            converter = CSVConverter(preserve_line_breaks=not args.single_line)
            converter.convert_file(
                input_path=str(input_path),
                output_path=output_path,
                direction=direction
            )

        print(f"✓ Conversion complete!")
        print(f"  Output saved to: {output_path}")

        # Show format info
        if direction == 'json_to_csv':
            if args.single_line:
                print(f"  Format: Single-line steps (semicolon-separated)")
            else:
                print(f"  Format: Multi-line steps (preserved line breaks)")

        return 0

    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())