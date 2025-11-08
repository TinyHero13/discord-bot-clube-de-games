#!/bin/bash

# Usage: export PROJECT_ID="your-gcp-project-id" && ./deploy-gcp.sh

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-your-gcp-project-id}"
INSTANCE_NAME="discord-bot"
ZONE="us-central1-a"
MACHINE_TYPE="e2-micro"

if [[ "$PROJECT_ID" == "your-gcp-project-id" ]]; then
    echo "set PROJECT_ID: export PROJECT_ID=your-project-id"
    exit 1
fi

echo "Deploying Discord Bot to GCP VM"

# Create VM if it doesn't exist
if ! gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID &>/dev/null; then
    echo "Creating VM $INSTANCE_NAME..."
    gcloud compute instances create $INSTANCE_NAME \
        --project=$PROJECT_ID \
        --zone=$ZONE \
        --machine-type=$MACHINE_TYPE \
        --image-family=ubuntu-2204-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=10GB \
        --boot-disk-type=pd-standard \
        --tags=discord-bot
    
    echo "Waiting for VM to initialize (30s)"
    sleep 30
else
    echo "VM $INSTANCE_NAME already exists"
fi

# Check for env file
if [[ -f bot.env ]]; then
    ENV_FILE=bot.env
elif [[ -f .env ]]; then
    ENV_FILE=.env
else
    echo "No .env found. Create one from bot.env.example"
    exit 1
fi

echo "Copying files to VM"
gcloud compute scp --zone=$ZONE --project=$PROJECT_ID \
    bot.py requirements.txt $ENV_FILE \
    $INSTANCE_NAME:~/

gcloud compute scp --recurse --zone=$ZONE --project=$PROJECT_ID \
    src/ \
    $INSTANCE_NAME:~/

echo "Setting up Python environment and systemd service..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID --command="
set -e

# Install Python and dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv ffmpeg

# Create virtual environment
python3 -m venv ~/discord-bot-venv
source ~/discord-bot-venv/bin/activate
pip install -r ~/requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/discord-bot.service > /dev/null <<'EOF'
[Unit]
Description=Discord Bot - Clube de Games
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
EnvironmentFile=$HOME/$ENV_FILE
ExecStart=$HOME/discord-bot-venv/bin/python $HOME/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl restart discord-bot

echo 'Bot deployed and running!'
echo 'Check status: sudo systemctl status discord-bot'
echo 'View logs: sudo journalctl -u discord-bot -f'
"

echo ""
echo "Deploy complete!"
echo ""