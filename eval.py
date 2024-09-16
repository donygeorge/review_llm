from langsmith import traceable
from langsmith.wrappers import wrap_openai
from langsmith.evaluation import evaluate, LangChainStringEvaluator
from langsmith.schemas import Run, Example
import openai
import json

from dotenv import load_dotenv
load_dotenv()

from config import config, model_kwargs
from prompts import EVALUATION_PROMPT


client = wrap_openai(openai.AsyncClient(api_key=config["api_key"], base_url=config["endpoint_url"]))

@traceable
def prompt_compliance_evaluator(run: Run, example: Example) -> dict:
    inputs = example.inputs['input']
    outputs = example.outputs['output']

    # Add print statements to explore inputs and outputs

    # print("Outputs:", outputs)

    return {
        "key": "prompt_compliance",
        "score": 0,  # Normalize to 0-1 range
        "reason": "None"
    }
    
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

    evaluation_data = f"""
    System Prompt: {system_prompt}

    Message History:
    {json.dumps(message_history, indent=2)}

    Latest User Message: {latest_message}

    Model Output: {model_output}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EVALUATION_PROMPT},
            {"role": "user", "content": evaluation_data}
        ],
        temperature=0.2
    )

    try:
        result = json.loads(response.choices[0].message.content)
        print("Result:", result)
        return {
            "key": "prompt_compliance",
            "score": result["accuracy_score"] / 5,  # Normalize to 0-1 range
            "reason": result["accuracy_rationale"]
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

# Evaluate the target task
results = evaluate(
    lambda inputs: inputs,
    data=data,
    evaluators=evaluators,
    experiment_prefix=experiment_prefix,
)

print(results)