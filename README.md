# Discord Bot — Clube de Games

This repository contains a small Discord bot that looks up Steam games and prices (via GG.deals). The project is designed to be run locally, inside Docker, or deployed to a Google Cloud VM using the provided `deploy-gcp.sh` script.

## Example usage
![Command example](imgs/command_example.png)


## Contents

- `bot.py` — bot entrypoint and extension loader
- `src/steam.py` — Steam / GG.deals helper functions
- `src/commands/` — command cogs (ping, info)
- `Dockerfile` — container image definition
- `docker-compose.yml` — compose file for local testing
- `bot.env.example` — example environment variables
- `deploy-gcp.sh` — deploy script (build & push with Cloud Build, run on a Compute Engine VM)

## Requirements

- Python 3.11+ 
- Docker (if building/running containers locally)
- Google Cloud SDK (`gcloud`) with permissions to use Cloud Build and Compute Engine (for the deployment script)

## Quick start — Local (Python)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your env file from the example and fill in your values:

```bash
cp .env.example .env
# edit .env and add your Discord BOT token and GGDEALS_API_KEY
```

## Commands

- `!ping` — returns latency
- `!info <game>` or `!info <game1>, <game2>, ...` — search Steam and return current and keyshop prices (aggregated in one embed when multiple games are provided)

## Using Docker 

Build and run locally:

```bash
docker build -t discord-bot:local .

# Run container using env file
docker run -d --name discord-bot --restart unless-stopped --env-file ./bot.env -p 8081:8081 discord-bot:local

# View logs
docker logs -f discord-bot
```

Or use `docker-compose`:

```bash
docker-compose up -d
docker-compose logs -f
```

## Deploying to Google Cloud VM using the provided script

This repository includes `deploy-gcp.sh` that automates the workflow:

- Build the container using Cloud Build and push it to Google Container Registry (GCR)
- Copy your `.env` to the VM
- Install Docker on the VM (if missing)
- Pull the image and run the container with `--restart unless-stopped`

Important: the script expects an existing Compute Engine VM with the name `discord-bot` in the default zone (you can change these values in the script). If you prefer, you can create a VM first via the Cloud Console or `gcloud compute instances create`.

### Before running the script
1. Install and authenticate gcloud locally:

```bash
# Install Google Cloud SDK (follow instructions on https://cloud.google.com/sdk)
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. Export your project id (alternatively edit the top of `deploy-gcp.sh`):

```bash
export PROJECT_ID=your-gcp-project-id
```

### Run the deploy script

```bash
./deploy-gcp.sh
```