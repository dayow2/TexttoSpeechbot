import os
from flask import Flask, request
import telebot
from gtts import gTTS

# Initialize Flask app
app = Flask(__name__)

# Get tokens from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5000)) 
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

bot = telebot.TeleBot(BOT_TOKEN)

# Telegram Bot Command Handlers
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Send me any text, and I will turn it into voice.")

@bot.message_handler(func=lambda message: True)
def text_to_speech(message):
    text = message.text
    bot.send_chat_action(message.chat.id, 'record_audio')
    
    try:
        # Generate TTS using gTTS
        tts = gTTS(text=text, lang='en')
        filename = f"tts_{message.message_id}.mp3"
        tts.save(filename)
        
        # Send audio back to user
        with open(filename, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)
            
        # Clean up the local file
        os.remove(filename)
    except Exception as e:
        bot.reply_to(message, f"Sorry, something went wrong: {str(e)}")

# Flask Routes for Webhook
@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + BOT_TOKEN)
    return "Bot is running and Webhook is set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
