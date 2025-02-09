import re
import requests
from solana.rpc.api import Client
from solana.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.system_program import transfer
from solders.transaction import Transaction

# Solana RPC Endpoint (Change if needed)
SOLANA_RPC_URL = "https://api.devnet.solana.com"
solana_client = Client(SOLANA_RPC_URL)

# Solana Explorer URL
EXPLORER_URL = "https://solscan.io"

def create_solana_wallet():
    keypair = Keypair()
    public_key = keypair.public_key()
    secret_key = keypair.private_key()
    
    return {
        "address": str(public_key),
        "secret_key": secret_key.hex(),  # Warning: Don't expose this in production
        "explorer_link": f"{EXPLORER_URL}/account/{public_key}?cluster=devnet"
    }


def fetch_balance_solana(address):
    try:
        balance = solana_client.get_balance(Pubkey.from_string(address))
        sol_balance = balance['result']['value'] / 1e9  # Convert lamports to SOL
        return sol_balance
    except Exception as e:
        return f"Error fetching balance: {str(e)}"


def transact_solana(sender_private_key, receiver_address, amount):
    try:
        sender_keypair = Keypair.from_bytes(bytes.fromhex(sender_private_key))
        receiver_pubkey = Pubkey.from_string(receiver_address)
        txn = Transaction().add(
            transfer(
                {"from_pubkey": sender_keypair.pubkey(), "to_pubkey": receiver_pubkey, "lamports": int(amount * 1e9)}
            )
        )
        txn_signature = solana_client.send_transaction(txn, sender_keypair)
        return f"Transaction successful! View it here: {EXPLORER_URL}/tx/{txn_signature['result']}"
    except Exception as e:
        return f"Transaction failed: {str(e)}"


def process_message(message):
    message = message.lower()
    
    # Create Solana Wallet
    if "create wallet" in message or "new solana account" in message:
        wallet_info = create_solana_wallet()
        return f"Your Solana Wallet:
        Address: {wallet_info['address']}
        Explorer: {wallet_info['explorer_link']}"
    
    # Check Balance
    if "check balance" in message:
        match = re.search(r'([A-Za-z0-9]{32,44})', message)
        if match:
            address = match.group(0)
            balance = fetch_balance_solana(address)
            return f"Balance for {address}: {balance} SOL
            Explorer: {EXPLORER_URL}/account/{address}"
        else:
            return "Please provide a valid Solana wallet address."
    
    # Transfer SOL
    if "transfer" in message and "sol" in message:
        match = re.search(r'([0-9]+\.?[0-9]*) sol to ([A-Za-z0-9]{32,44})', message)
        if match:
            amount = float(match.group(1))
            receiver = match.group(2)
            return "Transaction needs your private key. Please enter securely."
        else:
            return "Invalid format. Use: Transfer 2 SOL to <wallet_address>"
    
    return "I'm here to assist! Try 'Create Wallet', 'Check Balance <wallet>' or 'Transfer 2 SOL to <wallet>'"
