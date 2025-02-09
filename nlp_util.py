from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load pre-trained model and tokenizer
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)


def generate_text(prompt):
    # Hardcoded responses based on user input
    if "create token" in prompt.lower():
        return "Sure! Please provide the token name, symbol, supply, and decimals."
    elif "bridge" in prompt.lower():
        return "Sure! Please specify the source chain, target chain, amount, and token."
    elif "swap" in prompt.lower():
        return "Sure! Please specify the input token, output token, and amount."
    elif "balance" in prompt.lower():
        return "Sure! Please provide your wallet address and the token."
    elif "transfer" in prompt.lower():
        return "Sure! Please provide the sender wallet, receiver wallet, amount, and token."
    elif "schedule" in prompt.lower():
        return "Sure! Please provide the wallet address, amount, token, and schedule time."
    else:
        return "I'm sorry, I didn't understand that. How can I assist you?"