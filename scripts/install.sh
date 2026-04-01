#!/bin/bash

# ZeroSpecter Installation Script
# Version 2.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root (for system-wide installation)
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. Installing system-wide."
    INSTALL_PREFIX="/usr/local"
else
    print_info "Running as user. Installing locally."
    INSTALL_PREFIX="$HOME/.local"
fi

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

print_info "ZeroSpecter Installation Script"
print_info "Project directory: $PROJECT_DIR"
print_info "Install prefix: $INSTALL_PREFIX"

# Check Python version
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $PYTHON_VERSION is not supported. Please upgrade to Python $REQUIRED_VERSION or higher."
    exit 1
fi

print_success "Python $PYTHON_VERSION detected."

# Check if pip is available
print_info "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

print_success "pip3 detected."

# Create virtual environment if it doesn't exist
VENV_DIR="$PROJECT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
else
    print_info "Virtual environment already exists at $VENV_DIR"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_info "Installing dependencies..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install -r "$PROJECT_DIR/requirements.txt"
    print_success "Dependencies installed."
else
    print_error "requirements.txt not found in $PROJECT_DIR"
    exit 1
fi

# Install the package in development mode
print_info "Installing ZeroSpecter in development mode..."
pip install -e "$PROJECT_DIR"

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/captures"
mkdir -p "$PROJECT_DIR/temp"

# Check if installation was successful
print_info "Verifying installation..."
if command -v zer0specter &> /dev/null; then
    print_success "ZeroSpecter CLI installed successfully!"
    zer0specter --help | head -10
else
    print_error "Installation failed. Please check the error messages above."
    exit 1
fi

# Deactivate virtual environment
deactivate

print_success "Installation completed successfully!"
print_info "To use ZeroSpecter:"
print_info "  1. Activate the virtual environment: source $VENV_DIR/bin/activate"
print_info "  2. Run: zer0specter"
print_info "  3. Or run directly: $VENV_DIR/bin/zer0specter"
print_info ""
print_info "For development:"
print_info "  Install dev dependencies: pip install -r requirements-dev.txt"
print_info "  Run tests: pytest"
print_info "  Run linter: flake8 zer0specter/"
print_info ""
print_warning "Remember: Use this tool only for authorized security assessments!"
