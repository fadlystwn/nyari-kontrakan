#!/bin/bash
# Install Docker Engine in WSL 2
# Run this script in WSL terminal: bash setup-docker-wsl.sh

echo "Installing Docker Engine in WSL 2..."

# Update packages
sudo apt update
sudo apt upgrade -y

# Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start

echo ""
echo "Docker installed successfully!"
echo "Please run: newgrp docker"
echo "Then test with: docker ps"
echo ""
echo "To start Docker on WSL startup, add this to ~/.bashrc:"
echo "sudo service docker start"
