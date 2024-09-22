from langsmith import traceable
from langsmith.wrappers import wrap_openai
from langsmith.evaluation import evaluate, LangChainStringEvaluator
from langsmith.schemas import Run, Example
import openai
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
load_dotenv()

from config import config, model_kwargs
from prompts import EVALUATION_PROMPT
from helper import get_parsed_articles

client = wrap_openai(openai.AsyncClient(api_key=config["api_key"], base_url=config["endpoint_url"]))

@traceable
def prompt_compliance_evaluator(run: Run, example: Example) -> dict:
    inputs = example.inputs['input']
    outputs = example.outputs['output']

    # Add print statements to explore inputs and outputs
    # print("Inputs:", inputs)
    # print("Outputs:", outputs)

    # Extract system prompt
    system_prompt = next((msg['data']['content'] for msg in inputs if msg['type'] == 'system'), "")

    # Extract message history
    message_history = []
    for msg in inputs:
        if msg['type'] in ['human', 'ai']:
            message_history.append({
                "role": "user" if msg['type'] == 'human' else "assistant",
                "content": msg['data']['content']
            })

    # Extract latest user message and model output
    latest_message = message_history[-1]['content'] if message_history else ""
    model_output = outputs['data']['content']

    # print("--> Message History -->", message_history)
    # print("--> Latest Message -->", latest_message)
    # print("--> Model Output -->", model_output) 

    evaluation_data = f"""
    Original Content: {get_parsed_articles()}

    Message History:
    {json.dumps(message_history, indent=2)}

    Latest User Message: {latest_message}

    Model Output: {model_output}
    """
    
    # print("--> Evaluation Data -->", evaluation_data)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EVALUATION_PROMPT},
            {"role": "user", "content": evaluation_data}
        ],
        temperature=0.2
    )

    try:
        print("Response", response.dict()["choices"][0]["message"]["content"])
        # result = json.loads(response.choices[0].message.content)
        # return {
        #     "key": "prompt_compliance",
        #     "score": result["accuracy_score"] / 5,  # Normalize to 0-1 range
        #     "reason": result["accuracy_rationale"]
        # }
        return {
            "key": "prompt_compliance",
            "score": 0,
            "reason": "Incomplete evaluation"
        }
    except json.JSONDecodeError:
        print("Result: exception!!!")
        return {
            "key": "prompt_compliance",
            "score": 0,
            "reason": "Failed to parse evaluator response"
        }
  
  # The name or UUID of the LangSmith dataset to evaluate on.
data = "review_laptop"

# A string to prefix the experiment name with.
experiment_prefix = "Review prompt compliance"

# List of evaluators to score the outputs of target task
evaluators = [
    prompt_compliance_evaluator
]

def run_evaluation():
    results = evaluate(
        lambda inputs: inputs,
        data=data,
        evaluators=evaluators,
        experiment_prefix=experiment_prefix,
    )
    print(results)

if __name__ == "__main__":
    run_evaluation()