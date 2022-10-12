import html
import json
import logging
from secrets import choice
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
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import traceback

from typing import Dict

from urllib.parse import urlparse

import validators

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
    TOKEN = f.read().decode('UTF-8').strip()

CHOOSING, USER_CHOICE, USER_RESOURCE_CHOICE, TYPING_REPLY = range(4)

reply_keyboard = [
    ["Done"],["Start over"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# This can be your own ID, or one for a developer group/channel.
# You can use the /start command of this bot to see your chat id.

DEVELOPER_CHAT_ID = sqlite_connector.get_admin_id()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

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


async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Raise an error to trigger the error handler."""
    await context.bot.wrong_method_name()  # type: ignore[attr-defined]


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    # TODO: replace to /cancel command
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
    resources = []
    for resource in  sqlite_connector.get_resources_names():
        resources.append(resource[0])
    resources.sort()
    reply_keyboard = [resources,["Cancel"]]
    user = update.message.from_user
    logger.info("User %s said %s, and has ID %s", user.first_name, update.message.text, user.id)
    users = sqlite_connector.get_telegram_ids()
    if user.id in users:
        subscription_text = "You have already subscribed to notifications."
        
    else:
        write_result = sqlite_connector.write_telegram_id(user.id)
        logger.info('New ID recorded in DB: %s' % write_result)
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
    user = update.message.from_user
    logger.info("User %s with id %s choosed the platform %s", user.first_name, user.id, text)
    # TODO: add Cancel button and URL placeholder
    await update.message.reply_text(f"Platform is {text}. Please paste the URL to the title.")
    return TYPING_REPLY

async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    user = update.message.from_user
    logger.info("User %s with id %s send us the link: %s", user.first_name, user.id, text)
    
    if validators.url(text):
        # TODO: check if url correct for platform (me, don't forget mirrors) and it can be added to DB (lev) 
        domain = urlparse(text).netloc
        resource_id = sqlite_connector.get_resource_id_by_name(user_data["choice"])
        platform_url = sqlite_connector.get_resource(resource_id)[2]
        platform_domain = urlparse(platform_url).netloc
        if domain != platform_domain:
            logger.info(
                "User %s with id %s provide us bad url %s. Domain mismatch. Returning to url enter.", user.first_name, user.id, text
            )
            # TODO: add Cancel button
            await update.message.reply_text(f"URL you provided is not from this platform. Please enter correct one.")
            return TYPING_REPLY
        if 1 == 1 and 2 == 2:
            urlcheck = sqlite_connector.get_title_by_url(text)
            new_title_id = ''
            if urlcheck is None:
                resource = sqlite_connector.get_resource_id_by_name(category)
                new_title_id = sqlite_connector.write_title(resource, text)
                logger.info('New title recorded, ID is: %s' % new_title_id)
            else:
                logger.info("We already have %s in DB, ID is %s" % (urlcheck[2], urlcheck[0]))
            user_id = sqlite_connector.get_user_id(user.id)[0]
            subscriptions = sqlite_connector.get_user_subscriptions(user_id)
            if subscriptions:
                if urlcheck:
                    if urlcheck[0] in subscriptions:
                        logger.info(
                            "User %s with id %s (internal ID %s) already got subscription to the link: %s", 
                            user.first_name, user.id, user_id, urlcheck[2]
                        )
                        del user_data["choice"]
                        # TODO: let user claim us about no notifications
                        await update.message.reply_text(
                            "You are already subscribed to"
                            f"{facts_to_str(user_data)}\nIf there is no notifications -"
                            " please let us know.",
                            reply_markup=markup,
                        )

                        user_data.clear()

                        return CHOOSING
                    else:
                        result_id = sqlite_connector.write_subscription(user_id, urlcheck[0])
                        logger.info("New subscription for existing url recorded, ID is %s" % result_id)
                        if "choice" in user_data:
                            del user_data["choice"]
                        await update.message.reply_text(
                            "Neat! Just so you know, this is what you already told me:"
                            f"{facts_to_str(user_data)}\nYour subscription to this title was created.",
                            reply_markup=markup,
                        )

                        user_data.clear()

                        return CHOOSING
                else:
                    result_id = sqlite_connector.write_subscription(user_id, new_title_id)
                    logger.info("New subscription for newly added url recorded, ID is %s" % result_id)
                    if "choice" in user_data:
                        del user_data["choice"]
                    await update.message.reply_text(
                        "Neat! Just so you know, this is what you already told me:"
                        f"{facts_to_str(user_data)}\nYour subscription to this title was created.",
                        reply_markup=markup,
                    )

                    user_data.clear()

                    return CHOOSING
            else:
                if urlcheck:
                    result_id = sqlite_connector.write_subscription(user_id, urlcheck[0])
                    logger.info("New subscription for existing url recorded, ID is %s" % result_id)
                    if "choice" in user_data:
                        del user_data["choice"]
                    await update.message.reply_text(
                        "Neat! Just so you know, this is what you already told me:"
                        f"{facts_to_str(user_data)}\nYour subscription to this title was created.",
                        reply_markup=markup,
                    )

                    user_data.clear()

                    return CHOOSING
                else:
                    result_id = sqlite_connector.write_subscription(user_id, new_title_id)
                    logger.info("New subscription for newly added url recorded, ID is %s" % result_id)
                    if "choice" in user_data:
                        del user_data["choice"]
                    await update.message.reply_text(
                        "Neat! Just so you know, this is what you already told me:"
                        f"{facts_to_str(user_data)}\nYour subscription to this title was created.",
                        reply_markup=markup,
                    )

                    user_data.clear()

                    return CHOOSING
        else:
            logger.info(
                "User %s with id %s provide us bad url %s. Returning to url enter.", user.first_name, user.id, text
            )
            # TODO: add Cancel button
            await update.message.reply_text(f"URL you provided not match the platform. Please enter correct URL.")
            return TYPING_REPLY
                      
    else:
        logger.info(
            "User %s with id %s provide us bad url %s. Returning to url enter.", user.first_name, user.id, text
        )
        # TODO: add Cancel button
        await update.message.reply_text(f"URL you provided is malformed. Please enter correct one.")
        return TYPING_REPLY


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    reply_keyboard = [["Start over"]]
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
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

# for bot testing
async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Raise an error to trigger the error handler."""
    await context.bot.wrong_method_name()  # type: ignore[attr-defined]

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

        application.add_handler(CommandHandler("bad_command", bad_command))
        application.add_error_handler(error_handler)

        # Run the bot until the user presses Ctrl-C
        application.run_polling()
    else:
        print('No token - no bot.')
        exit

if __name__ == "__main__":
    main()