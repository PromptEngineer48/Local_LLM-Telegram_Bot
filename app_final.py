import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import openai

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!. My Name is Bot. I can have any conversation with you. Please say something!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("I can help you with anything!")
    

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


############################################################################


openai.api_type = "open_ai"
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "Whatever"

messages = [{'role': 'system', 'content': 'You are a helpful assistant. Keep replies within 20 words'}]


async def bot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns the reply to user after getting reply from server."""
    user = update.message.from_user
    
    logger.info("Question from User: %s", update.message.text)
    
    if update.message.text != '':
        user_input = update.message.text
        
        messages.append({'role': 'user', 'content': user_input})
        
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=messages,
            temperature=0,
            max_tokens=-1
        )
        
        messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
        
        # llm_reply = update.message.text
        llm_reply = response.choices[0].message.content
        
    else:
        return 

    await update.message.reply_text(llm_reply)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("your-bot-token").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_reply))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
