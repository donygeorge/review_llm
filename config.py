import os
from dotenv import load_dotenv
configurations = {
    "mistral_7B": {
        "endpoint_url": os.getenv("MISTRAL_7B_ENDPOINT"),
        "api_key": os.getenv("RUNPOD_API_KEY"),
        "model": "mistralai/Mistral-7B-v0.1"
    },
    "openai_gpt-4": {
        "endpoint_url": os.getenv("OPENAI_ENDPOINT"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4o-mini"
    }
}

# Choose configuration
config_key = "openai_gpt-4"
#config_key = "mistral_7B"

# Get selected configuration
config = configurations[config_key]

# https://platform.openai.com/docs/models/gpt-4o
model_kwargs = {
   "model": config["model"],
   "temperature": 0.3,
   "max_tokens": 2000
}

category_key = "laptops"

category_websites = {
    "projectors" : [
        "https://www.pcmag.com/picks/the-best-projectors",
        "https://www.nytimes.com/wirecutter/reviews/best-projectors/"
    ],     
    "laptops" : [
        "https://www.pcmag.com/picks/the-best-laptops",
        "https://www.nytimes.com/wirecutter/reviews/best-laptops/", 
        "https://www.tomsguide.com/best-picks/best-laptops"
    ],
    "smart_home" : [
        "https://www.pcmag.com/picks/the-best-smart-home-devices"
    ]
}

