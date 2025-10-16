# SpotTheSpy Telegram Bot

A complete guide to set up, locally deploy and use <b>SpotTheSpy Telegram Bot</b> infrastructure

## System Requirements:

- Python 3.13+
- Poetry 1.8.3+
- Git
- Docker

## Development Instruments:

- [PyCharm](https://www.jetbrains.com/pycharm/)
- [Redis Insight](https://redis.io/insight/)
- [Docker Desktop](https://docs.docker.com/desktop/)

## Setup

### BotFather

Go to [BotFather](https://t.me/BotFather) and create a new test bot for development.
Save a generated token for later.

### Create a project with virtual environment

- Clone a repository to any directory using the command below:
```bash
git clone https://github.com/SpotTheSpy/backend.git
```
- Open the project with ```PyCharm```, but do not create a virtual environment.
- Activate a new ```Poetry``` environment and install dependencies by using the commands below:
```bash
poetry env activate
poetry install
```

### Prepare Environmental Variables

- Create ```.env``` file with this structure:
```
TELEGRAM_BOT_TOKEN={Bot Token}

API_KEY={API-Key of you Back-End ASGI sever}
API_URL={Base URL for requesting API}

REDIS_DSN=redis://default:{Redis Password}@localhost:7379

TELEGRAM_BOT_START_URL=https://t.me/{Bot Username}?start={payload}
```
Replace placeholders in curly brackets with any value (Except for payload, this should be in curly brackets for formatting), 
and if necessary, you can also add these optional variables:
```
MIN_PLAYER_AMOUNT={Value}
MAX_PLAYER_AMOUNT={Value}
API_RETRY_CYCLES={Value}
API_RETRY_TIMEOUT={Value}
```
- Create ```redis.conf``` with this structure:
```
requirepass {Redis Password}
```
Password must be the same as in ```REDIS_DSN``` variable.

### Launch Docker Containers

To start all required Docker containers, simply run:
```bash
docker compose -f compose-local.yaml up -d
```

## Launch

### Start Bot Polling

To start polling, you need to run:
```bash
python polling.py
```
Or just create a PyCharm run configuration of a ```polling.py``` script.

## Usage

Your test bot is now polling requests from Telegram servers, and should reply to your actions.
You can test this by running ```/start``` command.

Redis' management via ```Redis Insight``` is accessible with these credentials:
- Username: ```default```
- Password: ```{Password in redis.conf file}```
- Hostname: ```localhost```
- Port: ```6379```
