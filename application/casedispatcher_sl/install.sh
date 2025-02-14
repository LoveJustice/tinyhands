#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# --- Check if Git is installed ---
if ! command -v git &>/dev/null; then
    echo "Git is not installed. Installing Git..."

    # Determine the package manager and install Git accordingly:
    if command -v apt-get &>/dev/null; then
        echo "Detected apt-get (Debian/Ubuntu)."
        sudo apt-get update
        sudo apt-get install -y git
    elif command -v yum &>/dev/null; then
        echo "Detected yum (RedHat/CentOS)."
        sudo yum install -y git
    elif command -v pacman &>/dev/null; then
        echo "Detected pacman (Arch Linux)."
        sudo pacman -Sy --noconfirm git
    else
        echo "Could not detect a supported package manager."
        echo "Please install Git manually and re-run this script."
        exit 1
    fi
else
    echo "Git is installed."
fi

git clone --no-checkout git@github.com:LoveJustice/tinyhands.git
cd tinyhands
git sparse-checkout init --cone
git sparse-checkout set application/casedispatcher_sl/
git checkout jira_de_53  # Or another branch if necessary
cd application/casedispatcher_sl/

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing now..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "uv has been installed successfully"
else
    echo "uv is already installed"
    uv --version
fi

uv venv
source .venv/bin/activate
uv pip install .

# Check for .streamlit directory and secrets.toml
if [ ! -d ".streamlit" ]; then
    echo ".streamlit directory is missing"
    exit 1
elif [ ! -f ".streamlit/secrets.toml" ]; then
    echo ".streamlit/secrets.toml is missing"
    exit 1
else
    echo "✓ .streamlit/secrets.toml found"
fi

# Check for .env in root
if [ ! -f ".env" ]; then
    echo ".env file is missing in root directory"
    exit 1
else
    echo "✓ .env found"
fi

echo "All required configuration files are present"



echo "Installation steps completed."
