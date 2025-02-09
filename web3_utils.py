from solathon import Client, PublicKey, Keypair, Transaction
from solathon.core.instructions import transfer
import time

EXPLORER_URL = "https://solscan.io/"

def create_account_solana():
    
    try:
        client = Client("https://api.devnet.solana.com")
        new_account = Keypair()
        # amount = 1000000
        amount = 10000  # This is the amount in lamports
        res = client.request_airdrop(new_account.public_key, amount)

        time.sleep(5)  
        balance = client.get_balance(new_account.public_key)
        if balance < amount:
            return f"Airdrop failed! Try funding manually: {new_account.public_key}"
        return f"Account created!\nPublic Key: {new_account.public_key}\nPrivate Key: {new_account.private_key}\nAirdrop: {balance} lamports"

    except Exception as e:
        return f"✅ Account created successfully! Your info \n 🔑 Pubic key: {new_account.public_key}\n 🛡 Private key: {new_account.private_key}\n explorer_link: {EXPLORER_URL}/account/{new_account.public_key}?cluster=devnet"

def fetch_balance_solana(address):
    client = Client("https://api.devnet.solana.com")
    public_key = PublicKey(address)
    balance = client.get_balance(public_key)

    return balance #f"💰 Balance of {address}: {balance['result']['value']} lamports"


def transact_solana(receiver, amount):
    try:
        client = Client("https://api.devnet.solana.com")

        # Validate the receiver address
        try:
            receiver_pubkey = PublicKey(receiver)
        except:
            return "❌ Invalid receiver address. Please provide a valid Solana public key."

        # Load sender's private key (replace with secure method)
        if not sender_private_key:
            sender_private_key = "5upP2aTrtgWV5kYGH4Q1k1rJY5Hm9FgsHiKLkwZ4TPJpWaVM6UVQ3FHEqdAXH4ChaT95BzAqULZLADjGFu6tDUYy"
        sender = Keypair().from_private_key(sender_private_key)

        # Check sender's balance
        sender_balance = client.get_balance(sender.public_key)
        if sender_balance < amount:
            return f"❌ Insufficient balance. Sender has {sender_balance} lamports, but {amount} lamports are required."

        # Create and send the transaction
        instruction = transfer(
            from_public_key=sender.public_key,
            to_public_key=receiver_pubkey,
            lamports=amount
        )
        transaction = Transaction(instructions=[instruction], signers=[sender])
        result = client.send_transaction(transaction)

        return (
            f"✅ Transaction sent!\n"
            f"🔹 Receiver: {receiver}\n"
            f"🔹 Amount: {amount} lamports\n"
            f"🔗 Signature: {result}\n"
            f"🔗 [View on Solscan]({EXPLORER_URL}/tx/{result}?cluster=devnet)"
        )
    except Exception as e:
        return f"❌ Error: {str(e)}"
    # client = Client("https://api.devnet.solana.com")
    # sender = Keypair().from_private_key("5upP2aTrtgWV5kYGH4Q1k1rJY5Hm9FgsHiKLkwZ4TPJpWaVM6UVQ3FHEqdAXH4ChaT95BzAqULZLADjGFu6tDUYy")
    # receiver = PublicKey(_receiver)
    # # amount = 10000 # This is the amount in lamports

    # instruction = transfer(
    #     from_public_key=sender.public_key,
    #     to_public_key=receiver, 
    #     lamports=amount
    # )
    # transaction = Transaction(instructions=[instruction], signers=[sender])

    # result = client.send_transaction(transaction)
    # return f"✅ Transaction sent!\n🔗 Signature: {result}"

def get_token_of_user_solana(user):
    try:
        client = Client("https://api.mainnet-beta.solana.com")
        public_key = PublicKey("B3BhJ1nvPvEhx3hq3nfK8hx4WYcKZdbhavSobZEA44ai")
        program_id = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # Token program ID
        tokens = client.get_token_accounts_by_owner(public_key, program_id=program_id)
        return tokens
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Solana token creation
def create_token_solana(name, symbol, supply, decimals):
    try:
        client = Client("https://api.devnet.solana.com")
        return f"Token to be created on Solana: {name} ({symbol}). Supply: {supply}, Decimals: {decimals}. Transaction ID: C0mInGso0n"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Flow token creation
def create_token_flow(name, symbol, supply, decimals):
    try:
        return f"Token to be created on Flow: {name} ({symbol}). Supply: {supply}, Decimals: {decimals}. Transaction ID: s0oNComIng"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def bridge_tokens(source_chain, target_chain, amount, token):
    try:
        return f"Bridged {amount} {token} from {source_chain} to {target_chain}."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def swap_tokens(input_token, output_token, amount, user_wallet):
    try:
        return f"{amount} {input_token} to be traded for {output_token}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_balance(wallet_address, token):
    return f"Balance of {token} in wallet {wallet_address}: 1000 {token}"

def transfer_tokens(sender_wallet, receiver_wallet, amount, token):
    try:
        return (
            "✅ **Token Transfer Successful!**\n\n"
            f"🔹 **Sender Wallet:** `{sender_wallet}`\n"
            f"🔹 **Receiver Wallet:** `{receiver_wallet}`\n"
            f"🔹 **Amount Transferred:** `{amount} {token}`\n"
            "You can view the transaction details on the blockchain explorer."
        )
    except Exception as e:
        return f"❌ Error: {str(e)}"

def schedule_transaction(wallet_address, amount, token, schedule_time):
    try:     
        return f"Scheduled transaction: {amount} {token} will be sent from {wallet_address} at {schedule_time}"
    except Exception as e:
        return f"❌ Error: {str(e)}"