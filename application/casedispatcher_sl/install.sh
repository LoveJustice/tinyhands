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
git sparse-checkout set tinyhands/application/casedispatcher_sl/
git checkout main  # Or another branch if necessary

# --- Proceed with Installing Your Project ---
# (Uncomment and update the following commands as needed.)

# Example: Clone the repository that contains your project
# Replace <repository-url> with the actual URL of your Git repository.
# git clone <repository-url> casedispatcher
# cd casedispatcher

# Make the project script executable and run it.
# chmod +x casedispatcher.sh
# ./casedispatcher.sh

echo "Installation steps completed."
