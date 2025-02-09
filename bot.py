from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, Application
from nlp_utils import generate_text  # Import the Hugging Face text generation function
from web3_utils import create_token_solana, create_token_flow, create_account_solana, fetch_balance_solana, transact_solana # Import blockchain functions
from config import TELEGRAM_BOT_TOKEN
import logging
import web3_utils
from transformers import pipeline
import re
import requests
from solana.rpc.api import Client
from solathon.solana_pay import create_qr
import time
import json

# Load intents from JSON file
with open("intents.json", "r", encoding="utf-8") as file:
    intents = json.load(file)["intents"]

# Convert intents into a usable dictionary
INTENTS = {intent["name"]: intent["patterns"] for intent in intents}


# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Load Hugging Face model for intent recognition
nlp_pipeline = pipeline("text-classification", model="facebook/bart-large-mnli")
model = pipeline("text2text-generation", model="facebook/blenderbot-400M-distill")

# Solana RPC Endpoint (Change if needed)
SOLANA_RPC_URL = "https://api.devnet.solana.com"
solana_client = Client(SOLANA_RPC_URL)

# Solana Explorer URL
EXPLORER_URL = "https://solscan.io/"

# Intent categories (These match what our bot can do)


# Detect user intent using NLP
def get_intent(message):

    message = message.lower()

    # Rule-based matching for specific intents
    if re.search(r'send \d+ sol to \b[A-Za-z0-9]{32,44}\b', message):
        return "send_sol"
    if re.search(r'create token (named|with name) \w+ (symbol|with symbol) \w+ (supply|with supply) \d+ (decimals|with decimals) \d+', message):
        return "create_token_solana"
    if "check balance" in message:
        return "check_balance"
    if "create wallet" in message or "new solana account" in message:
        return "create_account"
    if "what is" in message or "explain" in message:
        return "web3_education"
    if "how to" in message:
        return "tutorials"
    if "recommend resources" in message or "where can I learn more" in message:
        return "resources"
    if "help" in message:
        return "help"
    if "exit" in message or "goodbye" in message:
        return "exit"

    scores = nlp_pipeline(message)
    label = scores[0]["label"]

    return label

    # # Match label with predefined intents
    # for intent, keywords in INTENTS.items():
    #     if any(keyword in message.lower() for keyword in keywords):
    #         return intent
    # return "unknown"

def process_message(message):
    message = message.lower()

    # Check for "create account"
    if "create" in message and "solana" in message:
        return create_account_solana()

    # Check for "balance check"
    if "check balance" in message:
        match = re.search(r'(\b[A-Za-z0-9]{32,44}\b)', message)
        if match:
            address = match.group(0)
            return f"Fetching balance for {address}...\nBalance: {fetch_balance_solana(address)} SOL"
        else:
            return "Please provide a valid Solana wallet address."

    # Check for "transfer SOL"
    if "transfer" in message and "sol" in message:
        match = re.search(r'(\d+\.?\d*) sol to (\b[A-Za-z0-9]{32,44}\b)', message)
        if match:
            amount = float(match.group(1))
            receiver = match.group(2)
            return transact_solana("<YOUR_PRIVATE_KEY>", receiver, amount)
        else:
            return "Invalid transfer command. Try: 'Transfer 2 SOL to <wallet_address>'"

    # Default response (uses AI)
    response = model(message)
    return response[0]['generated_text']



# Command handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to the Coingenie! 🚀\n Here's what I can do:\n - I can help you create tokens on Solana or Flow blockchain \n - Bridge tokens between chains\n - Swap tokens\n - Check balances\n - Schedule transactions\n Just type your request, and I'll help you!"
    )

async def help_command(update: Update, context: CallbackContext):
    help_text = """
        🚀 **Welcome to the Coingenie!** 🚀

        Here’s what I can do:

        🔹 **Wallet Management**
        - `/create_account` - Create a new Solana wallet.
        - `/balance <wallet_address>` - Check the balance of a wallet.

        🔹 **Token Management**
        - `/create_token_solana <name> <symbol> <supply> <decimals>` - Create a new token on Solana.
        - `/create_token_flow <name> <symbol> <supply> <decimals>` - Create a new token on Flow.

        🔹 **Transactions**
        - `/send <private_key> <receiver> <amount>` - Send SOL or tokens to another wallet.
        - `/transfer <sender> <receiver> <amount> <token>` - Transfer tokens to another wallet.
        - `/schedule <wallet> <amount> <token> <time>` - Schedule a transaction for a future time.

        🔹 **Bridging and Swapping**
        - `/bridge <source_chain> <target_chain> <amount> <token>` - Bridge tokens between Solana and Flow.
        - `/swap <input_token> <output_token> <amount>` - Swap tokens.

        🔹 **Help**
        - `/help` - Show this help menu.

        🔹 **Exit**
        - `/exit` - End the conversation.


        Just type your request, and I'll help you! 😊
    """
    await update.message.reply_text(help_text)

def web3_education(user_input):
    if "what is web3" or "explain web3" or "tell me about web3" in user_input:
        return (
            "🌐 **What is Web3?**\n\n"
            "Web3 is the next generation of the internet, built on blockchain technology. "
            "It aims to create a decentralized web where users have control over their data and digital assets. "
            "Key features of Web3 include:\n"
            "- Decentralization\n"
            "- Transparency\n"
            "- User ownership\n"
            "- Smart contracts\n\n"
            "Learn more: [Web3 Explained](https://ethereum.org/en/web3/)"
        )
    elif "what is solana" or "explain solana" or "how does solana work" in user_input:
        return (
            "🚀 **What is Solana?**\n\n"
            "Solana is a high-performance blockchain designed for fast and low-cost transactions. "
            "It uses a unique consensus mechanism called **Proof of History (PoH)** to achieve high throughput. "
            "Key features of Solana include:\n"
            "- Fast transaction speeds (up to 65,000 TPS)\n"
            "- Low transaction fees\n"
            "- Support for smart contracts and decentralized apps (dApps)\n\n"
            "Learn more: [Solana Documentation](https://docs.solana.com/)"
        )
    elif "what is flow" in user_input:
        return (
            "🌊 **What is Flow?**\n\n"
            "Flow is a blockchain designed for building decentralized applications (dApps) and digital assets, "
            "such as NFTs. It is optimized for scalability and developer-friendly features. "
            "Key features of Flow include:\n"
            "- Multi-role architecture\n"
            "- Support for NFTs and gaming\n"
            "- Developer-friendly tools\n\n"
            "Learn more: [Flow Documentation](https://docs.onflow.org/)"
        )
    elif "what is a smart contract" in user_input:
        return (
            "🤖 **What is a Smart Contract?**\n\n"
            "A smart contract is a self-executing program that runs on a blockchain. "
            "It automatically enforces the terms of an agreement when predefined conditions are met. "
            "Smart contracts are used for:\n"
            "- Token creation\n"
            "- Decentralized finance (DeFi)\n"
            "- NFTs and digital assets\n\n"
            "Learn more: [Smart Contracts Explained](https://ethereum.org/en/developers/docs/smart-contracts/)"
        )
    elif "what is proof of stake" in user_input or "explain proof of stake" in user_input:
        return (
            "🔐 **What is Proof of Stake (PoS)?**\n\n"
            "Proof of Stake (PoS) is a consensus mechanism used by many blockchains to validate transactions and secure the network. "
            "Instead of miners (as in Proof of Work), PoS relies on **validators** who stake their tokens to participate in the consensus process. "
            "Key features of PoS include:\n"
            "- Energy efficiency\n"
            "- Scalability\n"
            "- Decentralization\n\n"
            "Learn more: [Proof of Stake Explained](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/)"
        )
    elif "what is proof of history" in user_input or "explain proof of history" in user_input:
        return (
            "⏳ **What is Proof of History (PoH)?**\n\n"
            "Proof of History (PoH) is a consensus mechanism used by Solana to order transactions efficiently. "
            "It creates a historical record of events, allowing the network to process transactions quickly and securely. "
            "Key features of PoH include:\n"
            "- High throughput\n"
            "- Low latency\n"
            "- Scalability\n\n"
            "Learn more: [Proof of History Explained](https://solana.com/news/proof-of-history)"
        )
    elif "what is an nft" in user_input or "explain nft" in user_input:
        return (
            "🖼️ **What is an NFT?**\n\n"
            "An NFT (Non-Fungible Token) is a unique digital asset that represents ownership of a specific item, such as art, music, or collectibles. "
            "NFTs are stored on a blockchain, ensuring their authenticity and scarcity. "
            "Key features of NFTs include:\n"
            "- Uniqueness\n"
            "- Ownership verification\n"
            "- Interoperability\n\n"
            "Learn more: [NFT School](https://nftschool.dev/)"
        )
    else:
        return (
            "🤔 **I probably dont get what youre saying but I'm here to help!**\n\n"
            "Here are some topics I can explain:\n"
            "- What is Web3?\n"
            "- What is Solana?\n"
            "- What is Flow?\n"
            "- What is a smart contract?\n"
            "- What is an NFT?\n\n"
            "Just ask me a question!"
        )
    
def provide_tutorials(user_input):
    if "how to create a wallet" in user_input:
        return (
            "📒 **How to Create a Wallet**\n\n"
            "1. Use the `/create_account` command to generate a new wallet.\n"
            "2. Save your wallet address and private key securely.\n"
            "3. Use your wallet to send, receive, and store tokens.\n\n"
            "Example: `/create_account`"
        )
    elif "how to create a token" or "how to deploy a token"  in user_input:
        return (
            "🪙 **How to Create a Token**\n\n"
            "1. Use the `/create_token` command to create a new token.\n"
            "2. Provide the token name, symbol, supply, and decimals.\n"
            "3. Your token will be deployed on the blockchain.\n\n"
            "Example: `/create_token MyToken MTK 1000000 9`"
        )
    else:
        return (
            "📚 **Tutorials**\n\n"
            "Here are some tutorials I can provide:\n"
            "- How to create a wallet\n"
            "- How to create a token\n"
            "- How to send tokens\n"
            "- How to check your balance\n\n"
            "Just ask me for a tutorial!"
        )
    
def provide_resources():
    return (
        "📖 **Educational Resources**\n\n"
        "Here are some great resources to learn more about Web3, Solana, and Flow:\n"
        "- [Solana Documentation](https://docs.solana.com/)\n"
        "- [Flow Documentation](https://docs.onflow.org/)\n"
        "- [Web3 Explained](https://ethereum.org/en/web3/)\n"
        "- [Smart Contracts Explained](https://ethereum.org/en/developers/docs/smart-contracts/)\n"
        "- [NFT School](https://nftschool.dev/)\n\n"
        "Happy learning! 🚀"
    )

async def create_account(update: Update, context: CallbackContext):
    response = web3_utils.create_account_solana()
    await update.message.reply_text(response)



async def check_balance(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /balance <wallet_address>")
        return
    response = web3_utils.fetch_balance_solana(context.args[0])
    await update.message.reply_text(f"💰 Balance: {response} SOL")


async def check_balance(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /balance <wallet_address>")
        return
    response = web3_utils.fetch_balance_solana(context.args[0])
    await update.message.reply_text(f"💰 Balance: {response} SOL")

async def send_sol(update: Update, context: CallbackContext):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /send <receiver> <amount>")
        return
    sender, receiver, amount = context.args
    response = web3_utils.transact_solana(receiver, int(amount))
    await update.message.reply_text(response)

async def send_some_sol(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()

    # Extract amount and receiver address using regex
    match = re.search(r'send (\d+) sol to (\b[A-Za-z0-9]{32,44}\b)', user_input)
    if not match:
        await update.message.reply_text(
            "❌ **Invalid Format**\n"
            "Please use the format: `send <amount> sol to <receiver_address>`\n\n"
            "Example: `send 1000000000 sol to AZue65b548UVp1jQxx5E9ZgJ7Pum4vNkHdJRudMBVdF7`"
        )
        return

    amount = int(match.group(1))  # Extract amount
    receiver = match.group(2)  # Extract receiver address

    # Call the transact_solana function
    try:
        response = web3_utils.transact_solana(receiver, amount)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"❌ **Error**: {str(e)}")

async def create_token_solana(update: Update, context: CallbackContext):
    if len(context.args) != 4:
        await update.message.reply_text("Usage: /create_token_solana <name> <symbol> <supply> <decimal>")
        return
    name, symbol, supply, decimals = context.args
    response = web3_utils.create_token_solana(name, symbol, int(supply), int(decimals))
    await update.message.reply_text(response)

async def create_token_flow(update: Update, context: CallbackContext):
    if len(context.args) != 4:
        await update.message.reply_text("Usage: /create_token_flow <name> <symbol> <supply> <decimal>")
        return
    name, symbol, supply, decimals = context.args
    response = web3_utils.create_token_flow(name, symbol, int(supply), int(decimals))
    await update.message.reply_text(response)

async def bridge_tokens(update: Update, context: CallbackContext):
    if len(context.args) != 4:
        await update.message.reply_text("Usage: /bridge <source_chain> <target_chain> <amount> <token>")
        return
    source_chain, target_chain, amount, token = context.args
    response = web3_utils.bridge_tokens(source_chain, target_chain, int(amount), int(token))
    await update.message.reply_text(response)

async def swap_tokens(update: Update, context: CallbackContext):
    if len(context.args) != 4:
        await update.message.reply_text("Usage: /swap <input_token> <output_token> <amount> <user_wallet>")
        return
    input_token, output_token, amount, user_wallet = context.args
    response = web3_utils.swap_tokens(input_token, output_token, int(amount), user_wallet)
    await update.message.reply_text(response)

async def transfer_tokens(update: Update, context: CallbackContext):
    if len(context.args) != 4:
        await update.message.reply_text("Usage: /transfer <sender_wallet> <receiver_wallet> <amount> <token>")
        return
    sender_wallet, receiver_wallet, amount, token= context.args
    response = web3_utils.swap_tokens(sender_wallet, receiver_wallet, int(amount), token)
    await update.message.reply_text(response)

async def schedule_transaction(update: Update, context: CallbackContext):
    if len(context.args) != 3:
        await update.message.reply_text("Usage: /schedule <wallet_address> <amount> <token> <schedule_time>")
        return
    wallet_address, amount, token, schedule_time = context.args
    response = web3_utils.schedule_transaction(wallet_address, int(amount), token, int(schedule_time))
    await update.message.reply_text(response)


async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    intent = get_intent(user_input)

    if intent == "create_account":
        response = web3_utils.create_account_solana()
    elif intent == "send_sol":
        await send_some_sol(update, context)  # Call the send_sol command handler
        return
    elif intent == "check_balance":
        response = "Please provide your wallet address using '/balance <address>'"
    elif intent == "send_sol":
        address = [word for word in user_input.split() if len(word) > 40]
        response = web3_utils.transact_solana(address, 1000000000) #"Please use /send <private_key> <receiver> <amount>"
    # elif intent == "create_token":
    #     response = "Please use /create_token_solana <name> <symbol> <supply> <decimals>"
    elif intent == "create_token_solana":
        # Create a new token on Solana
        response = web3_utils.create_token_solana("DogeCoin", "DOGE", 1000000000, 9)
    elif intent == "create_token_flow":
        # Create a new token on Flow
        response = web3_utils.create_token_flow("CatCoin", "CAT", 1000000000, 9)
    elif intent == "bridge_tokens":
        # Bridge tokens between Solana and Flow
        response = web3_utils.bridge_tokens("Solana", "FLOW", 100, "DOGE")
    elif intent == "swap_tokens":
        # Swap tokens
        response = web3_utils.swap_tokens("SOL", "FLOW", 10, "UserWallet")
    elif intent == "transfer_tokens":

        # Transfer tokens to another wallet
        response = web3_utils.transfer_tokens("UserWallet", "GvqhpPLeA8A6brzkwqeSKu16N9C6hCp27g8A9yitne1o", 50, "DOGE")
    elif intent == "schedule_transaction":
        # Schedule a transaction 
        response = web3_utils.schedule_transaction("UserWallet", 100, "DOGE", "2025-12-02 12:00:00")
    elif intent == "help":
        response = help_command(update, context)
    if intent == "web3_education":
        response = web3_education(user_input)
    elif intent == "tutorials":
        response = provide_tutorials(user_input)
    elif intent == "resources":
        response = provide_resources()
    else:
        response = "Sorry, I didn't understand that. Try using '/help'."

    await update.message.reply_text(response)

# Set up the bot
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()  # Replace with your bot token

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Updated Filters
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("create_account", create_account))
    application.add_handler(CommandHandler("balance", check_balance))
    application.add_handler(CommandHandler("send", send_sol))
    application.add_handler(CommandHandler("create_token_solana", create_token_solana))
    application.add_handler(CommandHandler("create_token_flow", create_token_flow))
    application.add_handler(CommandHandler("bridge", bridge_tokens))  # Bridge tokens between Solana and Flow
    application.add_handler(CommandHandler("swap", swap_tokens))  # Swap tokens on a DEX
    application.add_handler(CommandHandler("transfer", transfer_tokens))  # Transfer tokens to another wallet
    application.add_handler(CommandHandler("schedule", schedule_transaction))  # Schedule a transaction
    # application.add_handler(CommandHandler("exit", exit_command))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()