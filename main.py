import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Your provided credentials
BOT_TOKEN = '7982919097:AAHrM7hRB1FViwSqdWP_JKnE1tTF4AKeXY8'
USER_ID = 6428327821
GROUP_ID = -1002549085217

bot = telebot.TeleBot(BOT_TOKEN)

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != USER_ID:
        bot.reply_to(message, "Sorry, this bot is private and only accessible to its owner.")
        return
    bot.reply_to(message, "Send me a file, and I'll generate a permanent download link!")

# Handle all file types
@bot.message_handler(content_types=['document', 'video', 'audio', 'photo'])
def handle_file(message):
    if message.from_user.id != USER_ID:
        bot.reply_to(message, "Sorry, this bot is private and only accessible to its owner.")
        return
    try:
        # Get file info
        file_info = None
        if message.document:
            file_info = message.document
        elif message.video:
            file_info = message.video
        elif message.audio:
            file_info = message.audio
        elif message.photo:
            file_info = message.photo[-1]  # Highest resolution photo
        else:
            bot.reply_to(message, "Unsupported file type!")
            return

        # Forward file to group
        forwarded_message = bot.forward_message(GROUP_ID, message.chat.id, message.message_id)

        # Get file ID
        file_id = file_info.file_id

        # Get file path
        file_path = bot.get_file(file_id).file_path

        # Generate Telegram link (permanent as long as message exists in group)
        file_url = f"https://t.me/c/{str(GROUP_ID)[4:]}/{forwarded_message.message_id}"

        # Create a button with the link
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Download File", url=file_url))

        bot.reply_to(message, "Here’s your permanent file link:", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

# Start the bot
bot.polling()
