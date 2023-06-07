import os
import discord
from database_qa import database_qa


# Gateway intents (privileges) for the Discord bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
# Confirm that the bot is ready
async def on_ready():
  print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
  # Make sure the bot doesn't reply to itself
    if message.author == client.user:
        return
    # Invoke the bot by mention
    if client.user.mentioned_in(message):
        # Get the question from the user
        question = message.content
        
        answer = database_qa(question)
  
        # Finally, reply directly to the user with an answer
        await message.reply(answer['result'])
    

# Run the bot (make sure you set your Discord token as an environment variable)
client.run(os.getenv("DISCORD_TOKEN"))