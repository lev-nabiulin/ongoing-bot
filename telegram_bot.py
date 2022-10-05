import logging
import sys
import sqlite_connector

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from typing import Dict

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

fname = "./token.txt"
TOKEN = ""
try:
    f = open(fname, 'rb')
except OSError:
    print("Could not open/read Token file:", fname)
    sys.exit()

with f:
    TOKEN = f.read().decode('UTF-8')
    print(TOKEN)

CHOOSING, USER_CHOICE, USER_RESOURCE_CHOICE, TYPING_REPLY = range(4)

reply_keyboard = [
    ["Done"],["Start over"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["Yes", "Cancel"]]

    await update.message.reply_text(
        "Hello,  "
        "Send /cancel to stop talking to me.\n\n"
        "Do you want to receive updates of ongoing titles?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Wanna some fun?"
        ),
    )

    return USER_CHOICE

async def user_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Look for user id in DB and subscribing, showing list of resources"""
    #TODO: form keyboard string from resources table
    reply_keyboard = [["AnimeJoy", "RuTor","Cancel"]]
    user = update.message.from_user
    logger.info("User %s said %s, and has ID %s", user.first_name, update.message.text, user.id)
    users = sqlite_connector.get_telegram_ids()

    if user.id in users:
        subscription_text = "You have already subscribed to notifications."
        
    else:
        # TODO: user.id to sql
        subscription_text = "Subscribing to notifications."

    logger.info("Listing resources for ID %s", user.id)
    subscription_text += " Choose a platform:"
    await update.message.reply_text(
        subscription_text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Where we will track?"
        )
    )
    return USER_RESOURCE_CHOICE

async def user_resource_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Remember resource choice"""
    text = update.message.text
    context.user_data["choice"] = text

    await update.message.reply_text(f"platform is {text}. Please paste the URL to the title.")
    return TYPING_REPLY

async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    # TODO: record new titile or use existing from titles table
    # TODO: record user's choice to subscriptions table
    del user_data["choice"]

    await update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)}You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup,
    )

    return CHOOSING

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    reply_keyboard = [["Start over"]]
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        "Successfully subscribed.\n"
        "Until next time!",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )

    user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.\n"
        "Enter /start to start over.", 
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    if TOKEN != '':
        application = Application.builder().token(TOKEN).build()
    
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start),MessageHandler(filters.Regex("^Start over$"), user_choice)],
            states={
                CHOOSING: [
                    MessageHandler(filters.Regex("^Done$"), done),
                    MessageHandler(filters.Regex("^Start over$"), user_choice),
                ],
                USER_CHOICE: [
                    MessageHandler(filters.Regex("^Yes$"), user_choice),
                    MessageHandler(filters.Regex("^Cancel$"), cancel),
                ],
                USER_RESOURCE_CHOICE: [
                    MessageHandler(filters.Regex("^(AnimeJoy|RuTor)$"), user_resource_choice),
                    #TODO: form filters string from resources table
                    MessageHandler(filters.Regex("^Cancel$"), cancel)
                ],
                TYPING_REPLY: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                        received_information,
                    )
                ]
                
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )

        application.add_handler(conv_handler)

        # Run the bot until the user presses Ctrl-C
        application.run_polling()
    else:
        print('No token – no bot.')
        exit

if __name__ == "__main__":
    main()