import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.constants import ParseMode
import html
import json
import traceback
import os
import platform
from dotenv import load_dotenv

load_dotenv()

DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID","6052271063")
TOKEN=os.getenv("TOKEN","6116569761:AAFtFMJWSRKnLizqAqEzuGfN_QviZuIScQ8")



# Get the current date
from datetime import datetime
current_date = datetime.now().strftime("%Y-%m-%d")
# Create the log file name
log_file_name = f"./app/logs/{current_date}.log"

logging.basicConfig(
    filename=log_file_name,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def delete_old_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the current date and time
    import datetime
    current_time = datetime.datetime.now()
    
    # Get the operating system name
    os_name = platform.system()

    # Get the path
    path = os.path.dirname(os.path.realpath(__file__))
    # directory=path

    # Check if the operating system is Windows
    if os_name == "Windows":
        directory = path + "\logs\\"        
    # Check if the operating system is Linux
    elif os_name == "Linux":
        directory = path + "/logs/"

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # Check if the file is a log file
        if os.path.isfile(filepath) and filename.endswith('.log'):
            # Get the modification time of the file
            modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))

            # Calculate the difference between the current time and the modification time
            time_difference = current_time - modification_time

            # Check if the file is older than 3 days
            if time_difference.days >= 3:
                # Delete the file
                os.remove(filepath)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Deleted file: {filepath}")
            
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"File is not older than 3 days: {filepath}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    delete_old_log = CommandHandler('delete_old_log', delete_old_logs)

    # ...and the error handler
    application.add_error_handler(error_handler)

    application.add_handler(start_handler)
    application.add_handler(delete_old_log)
    
    application.run_polling()