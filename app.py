import os
from flask import Flask, request
import telebot
from gtts import gTTS

# Initialize Flask app
app = Flask(__name__)

# Get tokens from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Safeguard: Fallback to Render's default domain if WEBHOOK_URL is missing
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', RENDER_EXTERNAL_URL)

# Ensure the webhook URL has a trailing slash
if WEBHOOK_URL and not WEBHOOK_URL.endswith('/'):
    WEBHOOK_URL += '/'

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
    if not BOT_TOKEN:
        return "Error: BOT_TOKEN environment variable is missing!", 500
    if not WEBHOOK_URL:
        return "Error: WEBHOOK_URL environment variable is missing!", 500
        
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + BOT_TOKEN)
    return f"Bot is running and Webhook is set to: {WEBHOOK_URL}", 200

if __name__ == "__main__":
    # Render assigns a port dynamically via the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
