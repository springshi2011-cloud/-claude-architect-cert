import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()
system_prompt="""
You are a patient math tutor. Do not directly
answer a student's questions. Guide them to a
solution step by step.
"""
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system=system_prompt,
    messages=[
        {"role": "user", "content": "What is 144 divided by 12?"}
    ]
)
print(message.content[0].text)
