import openai
import os
import base64
import asyncio
from dotenv import load_dotenv

from langsmith import traceable
from langsmith.wrappers import wrap_openai

from prompts import SYSTEM_PROMPT
from config import config, model_kwargs
from queries import evaluation_questions_laptops
from helper import get_system_prompt_category


# Load environment variables
load_dotenv()

# Initialize the OpenAI async client
client = wrap_openai(openai.AsyncClient(api_key=config["api_key"], base_url=config["endpoint_url"]))


@traceable
async def process_questions(questions, system_prompt):
    message_history = []
    
    message_history.insert(0, {"role": "system", "content": system_prompt})
    
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
        await process_questions(thread, get_system_prompt_category())


if __name__ == "__main__":
   asyncio.run(process_threads(evaluation_questions_laptops))
   # asyncio.run(process_threads(questions_with_followups_edge_cases))
