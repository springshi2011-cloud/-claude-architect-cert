import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()
prompt = """
Generate three different sample AWS CLI commands. Each should be very short.
"""
messages = [
    {"role": "user", "content": prompt}, 
    {"role": "assistant", "content": "1."}, 
]
response = client.messages.create(
        model="claude-haiku-4-5-20251001", 
        max_tokens=1024,
        stop_sequences=["4."], 
        messages=messages
)
print("1." + response.content[0].text)