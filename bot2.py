from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, Application
from web3_utils import (
    create_token_solana,
    create_token_flow,
    bridge_tokens,
    swap_tokens,
    get_balance,
    transfer_tokens,
    schedule_transaction,
)
from config import TELEGRAM_BOT_TOKEN
from nlp_util import generate_text

# Command handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Coingeine! 🚀\n"
        "Here's what I can do:\n"
        "- Create accounts for you on Solana and Flow\n"
        "- Create tokens on Solana or Flow\n"
        "- Bridge tokens between chains\n"
        "- Swap tokens\n"
        "- Check balances\n"
        "- Transfer tokens\n"
        "- Schedule transactions\n"
        "Just type your request, and I'll help you!"
    )

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    response = generate_text(user_message)
    update.message.reply_text(response)

    # Simulate blockchain actions based on user input
    if "create token" in user_message.lower():
        response = create_token_solana("DogeCoin", "DOGE", 1000000000, 9)
        update.message.reply_text(response)
    elif "bridge" in user_message.lower():
        response = bridge_tokens("Solana", "Flow", 100, "DOGE")
        update.message.reply_text(response)
    elif "swap" in user_message.lower():
        response = swap_tokens("SOL", "USDC", 10, "UserWallet")
        update.message.reply_text(response)
    elif "balance" in user_message.lower():
        response = get_balance("UserWallet", "SOL")
        update.message.reply_text(response)
    elif "transfer" in user_message.lower():
        response = transfer_tokens("UserWallet", "AliceWallet", 50, "DOGE")
        update.message.reply_text(response)
    elif "schedule" in user_message.lower():
        response = schedule_transaction("UserWallet", 100, "DOGE", "2023-12-25 12:00:00")
        update.message.reply_text(response)

# Set up the bot
def main():
    application = Application.builder().token("7379747960:AAGlwcTUOp52GvPaRj14G-muoz75VgCUMas").build() # Replace with your bot token
    # dispatcher = updater.dispatcher

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Updated Filters

    # start the bot
    application.run_polling()
    # updater.idle()

if __name__ == "__main__":
    main()