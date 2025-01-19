# Motivation Bot

This project integrates a Django-based backend with a Telegram bot. The bot interacts with users, offering tasks and feedback, while the backend handles task storage and bot logic. The project is containerized using Docker for easy deployment.

## Features
- Task-based interaction (e.g., self-help tips, mindfulness exercises).
- Integration with OpenAI API for generating and evaluating content.
- Uses Django's ORM for storing user task data.
- Modular design for scalability and maintainability.

## Prerequisites

- Docker and Docker Compose installed.
- Python 3.10+ for local development (optional).
- Telegram Bot API Token and OpenAI API Key set in the environment variables

## Setup Instructions
1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```
2. Configure Environment Variables
```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
OPENAI_API_KEY=your-openai-api-key
```
3. Run Container
```bash
docker-compose build
docker-compose up -d
```

4. Run Bot Inside Container
```bash
python manage.py run_bot
```

