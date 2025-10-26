#!/bin/bash

# Exit on any error
set -e

echo "Starting setup..."

# 1. Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install Python3 and pip if not installed
echo "Installing Python3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# 3. Install Docker if not installed
if ! command -v docker &> /dev/null
then
    echo "Installing Docker..."
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
    echo "Docker installed. You may need to log out and log back in."
fi

# 4. Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null
then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 5. Set up Python virtual environment for local dev (optional)
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 6. Install Python dependencies
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "No requirements.txt found, skipping Python dependency installation."
fi

echo "Setup complete!"
echo "To activate the Python virtual environment, run: source venv/bin/activate"
echo "To start the project containers, run: docker-compose up -d"
