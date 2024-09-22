import chainlit as cl
import openai
import os
import base64
from dotenv import load_dotenv

from langsmith import traceable
from langsmith.wrappers import wrap_openai

from config import config, model_kwargs, category_websites, category_key
from helper import get_system_prompt_category

# Load environment variables
load_dotenv()

# Initialize the OpenAI async client
client = wrap_openai(openai.AsyncClient(api_key=config["api_key"], base_url=config["endpoint_url"]))


@traceable
@cl.on_message
async def on_message(message: cl.Message):

    print("Chat interface: message received")

    # Maintain an array of messages in the user session
    message_history = cl.user_session.get("message_history", [])
    
    # Add system prompt to the start of the message history if not already present
    if (not message_history or message_history[0].get("role") != "system"):
        system_prompt_content = get_system_prompt_category()
        print("Updating system prompt:" + system_prompt_content)
        message_history.insert(0, {"role": "system", "content": system_prompt_content})
    
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


if __name__ == "__main__":
    cl.main()
