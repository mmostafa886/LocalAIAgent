"""
Test Case Generator Package

A local AI-powered tool for generating comprehensive test cases
from user stories and acceptance criteria using Ollama.
"""

# Import main classes for easy access
from .test_case_generator import TestCaseGenerator
from .validator import TestCaseValidator
from .file_operations import FileOperations
from .csv_converter import CSVConverter
from .prompt_builder import PromptBuilder
from .model_client import OllamaClient
from .response_parser import ResponseParser

# Package metadata
__version__ = "1.0.0"
__author__ = "SDET Team"
__all__ = [
    "TestCaseGenerator",
    "TestCaseValidator",
    "FileOperations",
    "CSVConverter",
    "PromptBuilder",
    "OllamaClient",
    "ResponseParser"
]