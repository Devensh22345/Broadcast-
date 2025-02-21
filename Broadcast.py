import telebot
from pymongo import MongoClient
import os

# Telegram Bot Token
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))  # Replace with your Telegram user ID
bot = telebot.TeleBot(TOKEN)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["telegram_bot"]
users_collection = db["users"]

# Handle /start command
@bot.message_handler(commands=["start"])
def start_message(message):
    chat_id = message.chat.id
    user = users_collection.find_one({"chat_id": chat_id})
    
    if not user:
        users_collection.insert_one({"chat_id": chat_id})
    
    bot.send_message(chat_id, "Hello")

# Handle /broadcast command (Owner Only)
@bot.message_handler(commands=["broadcast"])
def handle_broadcast(message):
    if message.chat.id != OWNER_ID:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return
    
    text = message.text.replace("/broadcast", "").strip()
    if text:
        broadcast_message(text)
    else:
        bot.send_message(message.chat.id, "Please provide a message to broadcast.")

# Function to broadcast a message to all users
def broadcast_message(text):
    users = users_collection.find()
    for user in users:
        try:
            bot.send_message(user["chat_id"], text)
        except Exception as e:
            print(f"Failed to send message to {user['chat_id']}: {e}")

# Start the bot
if __name__ == "__main__":
    import logging
    import time
    from flask import Flask
    from threading import Thread

    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Bot is running"
    
    def start_bot():
        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as e:
                logging.error(f"Bot crashed: {e}")
                time.sleep(5)
    
    Thread(target=start_bot).start()

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
