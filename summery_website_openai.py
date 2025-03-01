from dotenv import load_dotenv
from openai import OpenAI
import os
import requests
from bs4 import BeautifulSoup



api_key = "YOUR_API_KEY_HERE"
if not api_key:
    raise ValueError("API key not found. Make sure you set OPENAI_API_KEY in your .env file.")

# Initialize OpenAI client
openai = OpenAI(api_key=api_key)

# System prompt for the assistant
system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."


def user_prompt_for(website):
    """
    Generates a prompt for the chatbot using website title and content.
    """
    website_title = website.title or "No Title"
    user_prompt = f"You are looking at a website titled {website_title}."
    user_prompt += "\nThe contents of this website are as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, summarize them too.\n\n"
    user_prompt += website.text
    return user_prompt


# Function to structure messages for the chatbot
def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]


# Headers for HTTP requests
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


# Class to scrape and store website content
class Website:
    def __init__(self, url):
        """
        Creates a Website object from the given URL using BeautifulSoup.
        """
        self.url = url
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Check if request was successful
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            self.title = "Error fetching website"
            self.text = ""
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"

        # Remove irrelevant elements (script, style, img, input)
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()

        self.text = soup.body.get_text(separator="\n", strip=True)


# Function to summarize a website
def summarize(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_for(website)
    )
    return response.choices[0].message.content


# Example: Summarizing Google homepage
summary = summarize("https://www.google.com/")
print(summary)
