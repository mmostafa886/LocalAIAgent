"""
Configuration file for Test Case Generator

Centralized configuration makes it easy to adjust settings without
modifying multiple files. Change these values to customize the generator
for your environment and preferences.
"""

from pathlib import Path

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Ollama model to use for generation
# Options:
#   - "llama3.2-vision:11b" - Llama 3.2 Vision (11B parameters)
#   - "llama3.1:8b"         - Llama 3.1 (8B parameters) - faster
#   - "llama3.1:70b"        - Llama 3.1 (70B parameters) - higher quality
#   - "mistral"             - Mistral model
#   - "qwen2.5"             - Qwen 2.5 model
MODEL_NAME = "llama3.2-vision:11b"

# Model generation parameters
TEMPERATURE = 0.3        # Lower = more focused, Higher = more creative (0.0-1.0)
TOP_P = 0.9             # Nucleus sampling parameter (0.0-1.0)
MAX_TOKENS = 4096       # Maximum tokens to generate

# Retry configuration
MAX_RETRIES = 3         # Number of retry attempts if generation fails


# ============================================================================
# TEST CASE GENERATION OPTIONS
# ============================================================================

# Include edge case test cases in generation
INCLUDE_EDGE_CASES = True

# Include negative test cases (error scenarios)
INCLUDE_NEGATIVE_TESTS = True

# Enable strict validation (enforce all validation rules)
STRICT_VALIDATION = True


# ============================================================================
# FILE AND DIRECTORY PATHS
# ============================================================================

# Base directory for the project
BASE_DIR = Path(__file__).parent

# Directory for input files (user stories)
INPUT_DIR = BASE_DIR / "input"

# Directory for output files (generated test cases)
OUTPUT_DIR = BASE_DIR / "output"

# Directory for example files
EXAMPLES_DIR = BASE_DIR / "examples"


# ============================================================================
# WEB SERVER CONFIGURATION
# ============================================================================

# Web server host (0.0.0.0 allows access from other devices on network)
WEB_HOST = "0.0.0.0"

# Web server port
WEB_PORT = 5000

# Enable Flask debug mode (auto-reload on code changes)
DEBUG_MODE = True


# ============================================================================
# CSV OUTPUT OPTIONS
# ============================================================================

# Preserve line breaks in CSV Steps field (True = multi-line, False = single-line)
CSV_PRESERVE_LINE_BREAKS = True

# Include summary statistics in CSV output by default
CSV_INCLUDE_SUMMARY = True

# Append datetime to filenames by default
APPEND_DATETIME = True

# Datetime format for filenames
DATETIME_FORMAT = "%Y%m%d_%H%M%S"


# ============================================================================
# LOGGING AND DEBUGGING
# ============================================================================

# Enable verbose output
VERBOSE = False

# Log file path (None = no log file, just console)
LOG_FILE = None  # Example: BASE_DIR / "generator.log"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model_display_name(model_name: str = None) -> str:
    """Get a user-friendly display name for the model."""
    if model_name is None:
        model_name = MODEL_NAME

    model_names = {
        "llama3.2-vision:11b": "Llama 3.2 Vision (11B)",
        "llama3.1:8b": "Llama 3.1 (8B)",
        "llama3.1:70b": "Llama 3.1 (70B)",
        "mistral": "Mistral",
        "qwen2.5": "Qwen 2.5"
    }

    return model_names.get(model_name, model_name)


def ensure_directories():
    """Create necessary directories if they don't exist."""
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    EXAMPLES_DIR.mkdir(exist_ok=True)


# Create directories on import
ensure_directories()


# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration values."""
    errors = []

    # Validate temperature
    if not 0.0 <= TEMPERATURE <= 1.0:
        errors.append(f"TEMPERATURE must be between 0.0 and 1.0, got {TEMPERATURE}")

    # Validate top_p
    if not 0.0 <= TOP_P <= 1.0:
        errors.append(f"TOP_P must be between 0.0 and 1.0, got {TOP_P}")

    # Validate max_tokens
    if MAX_TOKENS < 100:
        errors.append(f"MAX_TOKENS should be at least 100, got {MAX_TOKENS}")

    # Validate max_retries
    if MAX_RETRIES < 1:
        errors.append(f"MAX_RETRIES must be at least 1, got {MAX_RETRIES}")

    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(errors))


# Validate configuration on import
validate_config()