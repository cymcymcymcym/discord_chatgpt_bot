## Discord ChatGPT Bot

This program deploys openai's chat models on a discord bot.

Simultaneous multi-user chatting is supported.

Audio transcription is supported.

## Deployment
Create a .env file in the root directory and add the following:
```env
    OPENAI_API_KEY=
    BOT_TOKEN=
    DISCORD_TOKEN=
```
Run the following commands
```sh
    pip install -r requirements.txt
    python app.py
```