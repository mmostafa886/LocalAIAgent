#!/bin/bash
# Setup Script for Test Case Generator
# This script automates the setup process and fixes common issues

set -e  # Exit on error

echo "=========================================="
echo "Test Case Generator - Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Check if src directory structure exists
echo ""
echo "Checking project structure..."
if [ ! -d "src/test_case_generator" ]; then
    echo "Creating directory structure..."
    mkdir -p src/test_case_generator
    mkdir -p input
    mkdir -p output
    mkdir -p examples
    mkdir -p docs
    mkdir -p tests
    touch input/.gitkeep
    touch output/.gitkeep
    print_success "Directory structure created"
else
    print_info "Directory structure already exists"
fi

# Check if __init__.py exists and has content
echo ""
echo "Checking __init__.py..."
INIT_FILE="src/test_case_generator/__init__.py"
if [ ! -f "$INIT_FILE" ] || [ ! -s "$INIT_FILE" ]; then
    print_error "__init__.py is missing or empty"
    print_info "Please create $INIT_FILE with the content from the __init__.py artifact"
else
    print_success "__init__.py exists"
fi

# Check if setup.py exists
echo ""
echo "Checking setup.py..."
if [ ! -f "setup.py" ]; then
    print_error "setup.py not found"
    print_info "Please create setup.py with the content from the setup.py artifact"
else
    print_success "setup.py exists"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed from requirements.txt"
else
    print_info "requirements.txt not found, installing core dependencies..."
    pip install ollama flask
    print_success "Core dependencies installed"
fi

# Install package in development mode
echo ""
echo "Installing package in development mode..."
if [ -f "setup.py" ]; then
    pip install -e .
    print_success "Package installed in development mode"
else
    print_error "Cannot install: setup.py not found"
fi

# Check if Ollama is installed
echo ""
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    print_success "Ollama is installed"
    
    # Check if Ollama is running
    echo ""
    echo "Checking if Ollama is running..."
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama is running"
        
        # Check for models
        echo ""
        echo "Checking installed models..."
        MODELS=$(ollama list 2>&1)
        
        if echo "$MODELS" | grep -q "llama3.2-vision:11b"; then
            print_success "llama3.2-vision:11b is installed"
        else
            print_info "llama3.2-vision:11b not found"
            echo "To install: ollama pull llama3.2-vision:11b"
        fi
        
        if echo "$MODELS" | grep -q "llama3.1:8b"; then
            print_success "llama3.1:8b is installed"
        else
            print_info "llama3.1:8b not found"
            echo "To install: ollama pull llama3.1:8b"
        fi
    else
        print_error "Ollama is not running"
        echo "Start Ollama with: ollama serve"
    fi
else
    print_error "Ollama is not installed"
    echo "Install from: https://ollama.com/download"
fi

# Test imports
echo ""
echo "Testing imports..."
if python3 -c "from test_case_generator import TestCaseGenerator" 2>/dev/null; then
    print_success "Import test passed"
else
    print_error "Import test failed"
    print_info "Troubleshooting tips:"
    echo "  1. Verify all files are in src/test_case_generator/"
    echo "  2. Check __init__.py has proper imports"
    echo "  3. Run: pip install -e ."
    echo "  4. See FIXING_IMPORT_ERRORS.md for details"
fi

# Check if config.py exists
echo ""
echo "Checking configuration..."
if [ -f "config.py" ]; then
    print_success "config.py exists"
    MODEL=$(python3 -c "import config; print(config.MODEL_NAME)" 2>/dev/null || echo "unknown")
    echo "  Configured model: $MODEL"
else
    print_info "config.py not found - using defaults"
fi

# Create .gitignore if it doesn't exist
echo ""
echo "Checking .gitignore..."
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# IDE
.vscode/
.idea/
*.swp

# Project specific
output/*.csv
output/*.json
!output/.gitkeep

# OS
.DS_Store
Thumbs.db
EOF
    print_success ".gitignore created"
else
    print_info ".gitignore already exists"
fi

# Final summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start Ollama (if not running):"
echo "   ollama serve"
echo ""
echo "2. Pull your model (if needed):"
echo "   ollama pull llama3.2-vision:11b"
echo ""
echo "3. Test the CLI:"
echo "   python cli.py --show-config"
echo ""
echo "4. Start the web server:"
echo "   python web_server.py"
echo ""
echo "5. Open in browser:"
echo "   http://localhost:8000"
echo ""
echo "For troubleshooting, see: FIXING_IMPORT_ERRORS.md"
echo ""