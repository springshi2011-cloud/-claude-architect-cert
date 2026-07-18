import anthropic
import json
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

tools = [
    {
        "name": "set_reminder",
        "description": "Sets a reminder for a specific date and time with a given message.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "time": {"type": "string", "description": "Time in HH:MM format"},
                "message": {"type": "string", "description": "The reminder message"}
            },
            "required": ["date", "time", "message"]
        }
    }
]

def set_reminder(date, time, message):
    return f"Reminder set for {date} at {time}: {message}"

def run_conversation(user_message):
    messages = [{"role": "user", "content": user_message}]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    while response.stop_reason == "tool_use":
        tool_use = next(b for b in response.content if b.type == "tool_use")
        result = set_reminder(**tool_use.input)
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_use.id, "content": result}]})
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
    return response.content[0].text

print(run_conversation("Set a reminder for my doctor appointment on 2026-07-21 at 09:00"))
