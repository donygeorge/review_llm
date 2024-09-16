import openai
import os
import base64
import asyncio
from dotenv import load_dotenv

from langsmith import traceable
from langsmith.wrappers import wrap_openai

from prompts import SYSTEM_PROMPT
from config import config, model_kwargs
from queries import questions_with_followups, questions_with_followups_edge_cases
# Load environment variables
load_dotenv()

# Initialize the OpenAI async client
client = wrap_openai(openai.AsyncClient(api_key=config["api_key"], base_url=config["endpoint_url"]))

# Configuration setting to enable or disable the system prompt
ENABLE_SYSTEM_PROMPT = True

@traceable
async def process_questions(questions):
    message_history = []
    
    if ENABLE_SYSTEM_PROMPT:
        system_prompt_content = SYSTEM_PROMPT
        message_history.insert(0, {"role": "system", "content": system_prompt_content})
    
    for i, question in enumerate(questions):
        print(f"Processing question {i + 1}: {question}")
        message_history.append({"role": "user", "content": question})
        response = await client.chat.completions.create(messages=message_history, **model_kwargs)
        answer = response.choices[0].message.content

        # Append the response to message history
        message_history.append({"role": "assistant", "content": answer})
        print(f"Response {i + 1}: {answer}")


@traceable
async def process_threads(threads):
    for i, thread in enumerate(threads):
        print(f"Processing thread {i + 1}")
        await process_questions(thread)


if __name__ == "__main__":
   asyncio.run(process_threads(questions_with_followups))
   # asyncio.run(process_threads(questions_with_followups_edge_cases))
