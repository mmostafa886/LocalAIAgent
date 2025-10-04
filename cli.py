"""
Command Line Interface for Test Case Generator

This module provides a command-line interface to the test case generation system.
It handles argument parsing, user interaction, and high-level error handling.

Updated to use centralized configuration and support multiple import methods.
"""

import argparse
import sys
from pathlib import Path

# Import configuration
import config

# Try different import methods to handle various project structures
try:
    # Method 1: Installed package (after pip install -e .)
    from test_case_generator import TestCaseGenerator, FileOperations
    print("✓ Imported as installed package")
except ImportError:
    try:
        # Method 2: Direct import from src
        from src.test_case_generator import TestCaseGenerator, FileOperations
        print("✓ Imported from src directory")
    except ImportError:
        # Method 3: Add src to path and import
        import os
        src_path = Path(__file__).parent / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
            from test_case_generator import TestCaseGenerator, FileOperations
            print("✓ Imported with path modification")
        else:
            print("ERROR: Cannot import test_case_generator module.", file=sys.stderr)
            print("\nTroubleshooting steps:", file=sys.stderr)
            print("1. Install the package: pip install -e .", file=sys.stderr)
            print("2. Verify file structure: src/test_case_generator/__init__.py exists", file=sys.stderr)
            print("3. Check all module files are in src/test_case_generator/", file=sys.stderr)
            sys.exit(1)


def main():
    """
    Main entry point for the CLI.
    """
    # Set up argument parser with detailed help text
    parser = argparse.ArgumentParser(
        description=f'Generate test cases from user stories using {config.get_model_display_name()}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate test cases from a user story file
  python cli.py user_story.json
  
  # Specify custom output file and format
  python cli.py user_story.json --output my_tests.csv --format csv
  
  # Use a different model
  python cli.py user_story.json --model llama3.2-vision:11b
  
  # Create a template to get started
  python cli.py --create-template my_story.json
        """
    )

    # Input file argument
    parser.add_argument(
        'input_file',
        nargs='?',  # Make it optional when using --create-template
        help='JSON file containing user story and acceptance criteria'
    )

    # Output format options
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'both'],
        default='json',
        help=f'Output format: json, csv, or both (default: json)'
    )

    parser.add_argument(
        '--csv-single-line',
        action='store_true',
        help='For CSV output, use single-line format for Steps (semicolon-separated)'
    )

    parser.add_argument(
        '--csv-summary',
        action='store_true',
        default=config.CSV_INCLUDE_SUMMARY,
        help=f'Include summary statistics at the top of CSV file (default: {config.CSV_INCLUDE_SUMMARY})'
    )

    # Output file option
    parser.add_argument(
        '--output',
        default='test_cases.json',
        help='Output file for generated test cases (default: test_cases.json)'
    )

    # Model selection option
    parser.add_argument(
        '--model',
        default=config.MODEL_NAME,
        help=f'Ollama model to use (default: {config.MODEL_NAME})'
    )

    # Retry configuration
    parser.add_argument(
        '--max-retries',
        type=int,
        default=config.MAX_RETRIES,
        help=f'Maximum number of retry attempts (default: {config.MAX_RETRIES})'
    )

    # Temperature control
    parser.add_argument(
        '--temperature',
        type=float,
        default=config.TEMPERATURE,
        help=f'Model temperature 0.0-1.0, lower is more focused (default: {config.TEMPERATURE})'
    )

    # Template creation option
    parser.add_argument(
        '--create-template',
        metavar='FILEPATH',
        help='Create a template input file and exit'
    )

    # Metadata output option
    parser.add_argument(
        '--with-metadata',
        action='store_true',
        help='Include generation metadata in output file'
    )

    # Verbose output
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=config.VERBOSE,
        help=f'Show detailed progress information (default: {config.VERBOSE})'
    )

    # Show configuration
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Display current configuration and exit'
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle show-config mode
    if args.show_config:
        print("=" * 60)
        print("Current Configuration")
        print("=" * 60)
        print(f"Model: {config.MODEL_NAME} ({config.get_model_display_name()})")
        print(f"Temperature: {config.TEMPERATURE}")
        print(f"Max Retries: {config.MAX_RETRIES}")
        print(f"Include Edge Cases: {config.INCLUDE_EDGE_CASES}")
        print(f"Include Negative Tests: {config.INCLUDE_NEGATIVE_TESTS}")
        print(f"Output Directory: {config.OUTPUT_DIR}")
        print(f"CSV Preserve Line Breaks: {config.CSV_PRESERVE_LINE_BREAKS}")
        print("=" * 60)
        print("\nTo change these settings, edit config.py")
        return 0

    # Handle template creation mode
    if args.create_template:
        try:
            FileOperations.create_input_template(args.create_template)
            return 0
        except Exception as e:
            print(f"Error creating template: {e}", file=sys.stderr)
            return 1

    # Validate that input file was provided
    if not args.input_file:
        parser.print_help()
        print("\nError: input_file is required (or use --create-template)", file=sys.stderr)
        return 1

    # Display banner if verbose
    if args.verbose:
        print("=" * 60)
        print("Test Case Generator - Local AI Agent")
        print("=" * 60)
        print(f"Model: {config.get_model_display_name(args.model)}")

    # Step 1: Load user story from file
    try:
        if args.verbose:
            print(f"\n[1/3] Loading user story from: {args.input_file}")

        user_story, acceptance_criteria = FileOperations.load_user_story(args.input_file)

        if args.verbose:
            print(f"  ✓ Loaded user story with {len(acceptance_criteria)} acceptance criteria")

    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        print("Use --create-template to create a template file.", file=sys.stderr)
        return 1

    except ValueError as e:
        print(f"Error: Invalid input file format: {e}", file=sys.stderr)
        print("Make sure your JSON has 'user_story' and 'acceptance_criteria' fields.", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        return 1

    # Step 2: Initialize generator and generate test cases
    try:
        if args.verbose:
            print(f"\n[2/3] Generating test cases using model: {args.model}")
            print(f"  Configuration:")
            print(f"    - Max retries: {args.max_retries}")
            print(f"    - Temperature: {args.temperature}")
        else:
            print(f"Generating test cases using {config.get_model_display_name(args.model)}...")

        # Create generator with configuration
        generator = TestCaseGenerator(
            model_name=args.model,
            include_edge_cases=config.INCLUDE_EDGE_CASES,
            include_negative_tests=config.INCLUDE_NEGATIVE_TESTS,
            strict_validation=config.STRICT_VALIDATION
        )

        # Generate test cases with retry
        test_cases = generator.generate_test_cases_with_retry(
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            max_retries=args.max_retries,
            temperature=args.temperature
        )

        if args.verbose:
            print(f"  ✓ Generated {len(test_cases)} test cases")

    except ConnectionError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"\nMake sure Ollama is running with the {args.model} model:", file=sys.stderr)
        print("  - Check: ollama list", file=sys.stderr)
        print(f"  - Install: ollama pull {args.model}", file=sys.stderr)
        print("  - Start: ollama serve", file=sys.stderr)
        return 1

    except ValueError as e:
        print(f"Error generating test cases: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Step 3: Save results
    try:
        if args.verbose:
            print(f"\n[3/3] Saving test cases (format: {args.format})")

        if args.format == 'both':
            # Save in both formats
            if args.with_metadata:
                metadata = generator.get_info()
                metadata['input_file'] = args.input_file
                json_path = args.output if args.output.endswith('.json') else args.output + '.json'
                FileOperations.save_with_metadata(
                    test_cases=test_cases,
                    filepath=json_path,
                    metadata=metadata
                )
                csv_path = Path(args.output).with_suffix('.csv')
                FileOperations.save_test_cases_csv(
                    test_cases=test_cases,
                    filepath=str(csv_path),
                    preserve_line_breaks=not args.csv_single_line,
                    include_summary=args.csv_summary
                )
                print(f"\n✓ Success! Generated {len(test_cases)} test cases")
                print(f"  JSON saved to: {json_path}")
                print(f"  CSV saved to: {csv_path}")
            else:
                json_path, csv_path = FileOperations.save_test_cases_both_formats(
                    test_cases=test_cases,
                    base_path=args.output,
                    preserve_line_breaks=not args.csv_single_line
                )
                print(f"\n✓ Success! Generated {len(test_cases)} test cases")
                print(f"  JSON saved to: {json_path}")
                print(f"  CSV saved to: {csv_path}")

        elif args.format == 'csv':
            csv_path = args.output if args.output.endswith('.csv') else args.output + '.csv'
            FileOperations.save_test_cases_csv(
                test_cases=test_cases,
                filepath=csv_path,
                preserve_line_breaks=not args.csv_single_line,
                include_summary=args.csv_summary
            )
            print(f"\n✓ Success! Generated {len(test_cases)} test cases")
            print(f"  CSV saved to: {csv_path}")

        else:  # json format
            if args.with_metadata:
                metadata = generator.get_info()
                metadata['input_file'] = args.input_file
                FileOperations.save_with_metadata(
                    test_cases=test_cases,
                    filepath=args.output,
                    metadata=metadata
                )
            else:
                FileOperations.save_test_cases(
                    test_cases=test_cases,
                    filepath=args.output
                )

            print(f"\n✓ Success! Generated {len(test_cases)} test cases")
            print(f"  JSON saved to: {args.output}")

        # Show brief summary (common to all formats)
        criteria_covered = set(tc["Linked Acceptance Criterion"] for tc in test_cases)
        print(f"  Coverage: {len(criteria_covered)} acceptance criteria covered")

        return 0

    except Exception as e:
        print(f"Error saving output: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())