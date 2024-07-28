import os
import discord
from discord.ext import commands
from openai import OpenAI

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

api_key = os.environ['OPENAI_API_KEY']
print(api_key)
client=OpenAI(api_key=api_key)

bot_token = os.environ['DISCORD_TOKEN']
intents = discord.Intents.default()
intents.message_content = True # Adding the message content intent
bot = commands.Bot(command_prefix="/", intents=intents)

# Dictionary to keep track of conversation history for each user
conversations = {}

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.command(name='start', aliases=['welcome'])
async def welcome(ctx):
    user_id = ctx.author.id
    print(f"User {user_id} started the conversation.")
    conversations[user_id] = [{"role": "system", "content": "You are a helpful assistant."}]
    await ctx.send("Welcome! I am a GPT bot")

async def process_voice_message(message):
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(('.mp3', '.wav','.m4a', '.flac','.ogg')):
            # Download the audio file
            audio_file_path = f"./audio/{attachment.filename}" #discord recorded audio are .ogg
            await attachment.save(audio_file_path)
            #print("transcribing audio")

            with open(audio_file_path, "rb") as audio_file:
                whisper_results = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file = audio_file
                )
            text_content = whisper_results.text
            #print(text_content)
            return text_content
            os.remove(audio_file_path)

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    user_id = message.author.id
    content=str()
    if message.attachments:
        print("processing voice message")
        content=await process_voice_message(message)
    else:
        content=message.content
        
    user_message = {"role": "user", "content": content}
    # Retrieve the conversation history for this user, or start a new one
    conversation_history = conversations.get(user_id, [{"role": "system", "content": "You are a helpful assistant."}])
    conversation_history.append(user_message)
    conversations[user_id] = conversation_history
    
    completion=client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        max_tokens=800
    )
    response_text = completion.choices[0].message.content
    conversations[user_id].append({"role": "assistant", "content": response_text})
    
    await message.channel.send(response_text)

    # Allow other on_message events and commands to work
    await bot.process_commands(message)


if __name__ == '__main__':
    print("Starting the bot...")
    bot.run(bot_token)
