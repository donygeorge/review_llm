import chainlit as cl
import openai
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

configurations = {
    "mistral_7B": {
        "endpoint_url": os.getenv("MISTRAL_7B_ENDPOINT"),
        "api_key": os.getenv("RUNPOD_API_KEY"),
        "model": "mistralai/Mistral-7B-v0.1"
    },
    "openai_gpt-4": {
        "endpoint_url": os.getenv("OPENAI_ENDPOINT"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4"
    }
}

# Choose configuration
config_key = "openai_gpt-4"
#config_key = "mistral_7B"

# Get selected configuration
config = configurations[config_key]

# Initialize the OpenAI async client
client = openai.AsyncClient(api_key=config["api_key"], base_url=config["endpoint_url"])

# https://platform.openai.com/docs/models/gpt-4o
model_kwargs = {
   "model": config["model"],
   "temperature": 0.3,
   "max_tokens": 500
}

@cl.on_message
async def on_message(message: cl.Message):

    # Maintain an array of messages in the user session
    message_history = cl.user_session.get("message_history", [])
    
    message_history.append({"role": "user", "content": message.content})
    
    response_message = cl.Message(content="")
    await response_message.send()

    stream = await client.chat.completions.create(
        messages=message_history,
        stream=True, **model_kwargs
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await response_message.stream_token(token)

    await response_message.update()

    # Record the AI's response in the history
    message_history.append({"role": "assistant", "content": response_message.content})
    cl.user_session.set("message_history", message_history)
    
