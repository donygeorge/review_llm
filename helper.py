from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

from config import config, model_kwargs, category_websites, category_key
from prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_WEBSITE

# Load environment variables
load_dotenv()

def parse_articles(website):
    response = requests.get(website)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = [p.text for p in soup.find_all("p")]
    full_text = "\n".join(text)
    print("Parsing:" + website)
    return full_text

def get_parsed_articles():
    websites = category_websites[category_key]
    parsed_articles = ""
    for website in websites:
        parsed_article = parse_articles(website)
        if parsed_article:
            parsed_articles += parsed_article + "\n\n"
    return parsed_articles


def get_system_prompt_category():
    return SYSTEM_PROMPT_WEBSITE.format(parsed_articles=get_parsed_articles())