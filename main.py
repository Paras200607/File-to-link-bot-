import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import logging
from requests.exceptions import ConnectionError, ReadTimeout
from telebot.apihelper import ApiTelegramException

# Your provided credentials
BOT_TOKEN = '7982919097:AAH-pb3jZipiwd9A5WVrvt-tVBrAQTyKGF0'
USER_ID = 6428327821
GROUP_ID = -1002549085217

# Maximum file size (2GB in bytes)
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize bot with timeout
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None, threaded=False)

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != USER_ID:
        bot.reply_to(message, "Sorry, this bot is private and only accessible to its owner.")
        return
    bot.reply_to(message, "Send me a file (up to 2GB), and I'll generate a permanent download link!")

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

        # Check file size
        file_size = file_info.file_size
        if file_size > MAX_FILE_SIZE:
            bot.reply_to(message, f"Error: File is too big ({file_size / (1024 * 1024):.2f} MB). Maximum size is 2GB.")
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
        logger.error(f"Error processing file: {str(e)}")

# Polling with retry logic and 409 conflict handling
def start_polling():
    retry_count = 0
    max_retries = 5
