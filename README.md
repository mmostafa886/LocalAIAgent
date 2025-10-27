# 🤖 LocalAIAgent for Test Case Generation

A Python-based tool for generating comprehensive test cases from user stories and acceptance criteria using AI models. Includes both a command-line interface (CLI) and a web server with real-time log streaming and CSV export.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)

## Runtime / LLM / Scripting
- Runtime: Ollama
- LLM: llama3.2-vision:11b
- Scripting: Python

## Features
- 📝 Generate test cases from user stories and acceptance criteria
- 🧩 Supports edge cases and negative tests
- 📺 Real-time log panel in web interface
- 🔎 Auto-parsing of various input formats (bullets, numbers, labels, plain text)
- 📄 Output as CSV files
- ⚙️ Configurable AI model backend

## Directory Structure
```
├── .gitignore                # Git configuration to ignore files/folders
├── LocalAIAgent.iml          # IntelliJ/JetBrains project file
├── Quick_Start.txt           # Quick start instructions
├── cli.py                    # Command-line interface for test case generation
├── config.py                 # Configuration settings (model, options)
├── convert_to_csv.py         # Utility for converting data to CSV
├── my_test_cases.json        # Example test cases in JSON format
├── my_user_story.json        # Example user story in JSON format
├── requirements.txt          # Python dependencies
├── setup.py                  # Python package setup script
├── setup_project.sh          # Shell script for project setup
├── src                       # Source code directory
    ├── test_case_generator.egg-info   # Python package metadata
    │   ├── PKG-INFO                  # Package info
    │   ├── SOURCES.txt               # Source files list
    │   ├── dependency_links.txt      # Dependency links
    │   ├── entry_points.txt          # Entry points for package
    │   ├── requires.txt              # Required packages
    │   └── top_level.txt             # Top-level modules
    └── test_case_generator           # Main test case generator module
    │   ├── __init__.py               # Package initializer
    │   ├── csv_converter.py          # CSV conversion logic
    │   ├── file_operations.py        # File read/write utilities
    │   ├── model_client.py           # AI model client interface
    │   ├── prompt_builder.py         # Prompt construction logic
    │   ├── response_parser.py        # AI response parsing
    │   ├── test_case_generator.py    # Core test case generation logic
    │   └── validator.py              # Test case validation logic
├── static                    # Static files for web server
    ├── css
    │   └── style.css          # Web UI styles
    └── js
    │   └── app.js             # Web UI JavaScript
├── templates                 # HTML templates for web server
    └── index.html             # Main web page template
└── web_server.py              # Flask web server for UI
```

## Setup
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd LocalAIAgent
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   pip install -e .
   ```
3. **(Optional) Configure model settings:**
   Edit `config.py` to set your preferred AI model and options.

## Usage
### Command-Line Interface
Generate test cases from a user story and acceptance criteria:
```sh
python cli.py --model <model_name> --input <input_file> --output <output_file> [--max_retries 5]
```

### Web Server
Start the web server:
```sh
python web_server.py
```
Then open [http://localhost:8000](http://localhost:8000) in your browser.

## 🛠️ Usage
### Web Interface
- Paste your user story and acceptance criteria
- Click "Generate Test Cases" (spinner shows progress)
- Download the generated CSV file

## Example Input
```
User Story:
As a user, I want to log in so that I can access my account

Acceptance Criteria:
- User can log in with valid credentials
- User sees error with invalid password
- User account locks after 5 failed attempts
- User can reset password via email
```

## Contact
[mmostafa886@gmail.com](mailto:mostafa886@gmail.com)
