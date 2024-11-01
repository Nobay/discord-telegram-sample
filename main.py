import asyncio
import threading

import discord
import os
from discord.ext import commands
from telegram import Bot, Update
from telegram.error import TelegramError
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, Updater

# Define your tokens and IDs
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_USER_ID = os.environ['TELEGRAM_USER_ID']
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
DISCORD_CHANNEL_ID = os.environ['DISCORD_CHANNEL_ID']

# Define the welcome message content
WELCOME_MESSAGE = "Welcome to Mena's Gaming Penthouse! 🎮 Make friends, play games, and have fun—let's game on! 🕹️."
HELP_MESSAGE = "For help, check our discord server with the /discord command in discord-link-here."


# Telegram Bot Setup
def start_telegram_bot():
    async def welcome(update: Update, _):
        await update.message.reply_text(WELCOME_MESSAGE)

    async def help_command(update: Update, _):
        await update.message.reply_text(HELP_MESSAGE)

    async def new_member(update: Update, _):
        for member in update.message.new_chat_members:
            await update.message.reply_text(f"Welcome {member.first_name}! {WELCOME_MESSAGE}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("welcome", welcome))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))

    app.initialize()  # Make sure to initialize the app before running
    # Start polling in a non-blocking way
    app.run_polling()

# Initialize Telegram bot
telegram_bot = Bot(token=TELEGRAM_TOKEN)

# Discord Bot Setup
intents = discord.Intents.all()
intents.message_content = True
discord_bot = commands.Bot(command_prefix="!", intents=intents)


# Function to forward message to Telegram
async def send_to_telegram(message):
    try:
        await telegram_bot.send_message(chat_id=TELEGRAM_USER_ID, text=message)
    except TelegramError as e:
        print(f"Failed to send message to Telegram: {e}")


@discord_bot.event
async def on_ready():
    print(f'Logged in as {discord_bot.user}')


@discord_bot.event
async def on_message(message):
    if message.channel.id == int(DISCORD_CHANNEL_ID) and not message.author.bot:
        content = f"Message from Discord (Channel: {message.channel.name}): {message.author} said: {message.content}"

        # Forward message to Telegram user
        await send_to_telegram(content)

    # Process commands if any
    await discord_bot.process_commands(message)


def start_discord_bot():
    discord_bot.run(DISCORD_TOKEN)


# Main function to run both bots asynchronously
def main():
    telegram_thread = threading.Thread(target=start_telegram_bot)
    discord_thread  = threading.Thread(target=start_discord_bot)

    telegram_thread.start()
    discord_thread.start()

    telegram_thread.join()
    discord_thread.join()

if __name__ == "__main__":
    main()
