#!/bin/bash

# Docker-based deploy script for GCP VM
# Usage
# export PROJECT_ID="your-gcp-project-id"
# ./deploy-gcp.sh

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-your-gcp-project-id}"
IMAGE_NAME="discord-bot"
TAG="latest"
INSTANCE_NAME="discord-bot"
ZONE="us-central1-a"
CONTAINER_NAME="discord-bot"
PORT="8081"

if [[ "$PROJECT_ID" == "your-gcp-project-id" ]]; then
    echo "Please set PROJECT_ID in the script or export it in your environment."
    exit 1
fi

echo "Checking if VM exists, creating if necessary"

if ! gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID &>/dev/null; then
    echo "Creating VM $INSTANCE_NAME..."
    gcloud compute instances create $INSTANCE_NAME \
        --project=$PROJECT_ID \
        --zone=$ZONE \
        --machine-type=e2-micro \
        --image-family=ubuntu-2204-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=10GB \
        --boot-disk-type=pd-standard \
        --scopes=cloud-platform \
        --tags=discord-bot
    
    echo "Waiting for VM to initialize (30s)"
    sleep 30
else
    echo "VM $INSTANCE_NAME already exists"
fi

echo "Building image with Cloud Build and pushing to gcr.io/$PROJECT_ID/$IMAGE_NAME:$TAG"

gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME:$TAG

echo "Copying env file to VM (bot.env or .env expected locally)"
if [[ -f bot.env ]]; then
    ENV_FILE=bot.env
elif [[ -f .env ]]; then
    ENV_FILE=.env
else
    echo "No bot.env or .env found in current directory. Create one from bot.env.example and fill in TOKEN."
    exit 1
fi

gcloud compute scp --zone=$ZONE --project=$PROJECT_ID $ENV_FILE $INSTANCE_NAME:~/bot.env

echo "Installing Docker on VM, pulling image and running container..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID --command="bash -s" <<SSH
set -euo pipefail
IMAGE="gcr.io/$PROJECT_ID/$IMAGE_NAME:$TAG"

if ! command -v docker >/dev/null 2>&1; then
  echo "Installing docker..."
  sudo apt-get update
  sudo apt-get install -y docker.io
  sudo usermod -aG docker $USER || true
fi

echo "Logging to gcr..."
gcloud auth configure-docker --quiet || true

echo "Pulling image: $IMAGE"
docker pull "$IMAGE"

if docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
  echo "Stopping and removing existing container..."
  docker rm -f "$CONTAINER_NAME" || true
fi

echo "Creating and running container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --env-file ~/bot.env \
  -p ${PORT}:${PORT} \
  "$IMAGE"

echo "Done. Container $CONTAINER_NAME is running."
SSH

echo "Deploy finished."
echo "Logs: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID --command='docker logs -f $CONTAINER_NAME'"
echo "SSH:  gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID"

