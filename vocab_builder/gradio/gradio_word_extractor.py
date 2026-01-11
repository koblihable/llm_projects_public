import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI
import gradio as gr

# creating environment

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')
openai = OpenAI()
MODEL = 'gpt-4o-mini'

# scrape the given website
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)    

# get the vocab from the website
def get_vocab(url, word_class):
    user_message = f'Find all {word_class} in the text and give me their list together with their translation into English - {Website(url).text}'
    stream = openai.chat.completions.create(
        messages=[
            {'role':'system','content':'you are a language expert'},
            {'role':'user','content':user_message}
        ],
        model=MODEL,
        stream=True
    )
    result = ''
    for chunk in stream:
        result += chunk.choices[0].delta.content or ''
        yield result

# create the gradio interface
view = gr.Interface(
    fn=get_vocab,
    inputs=[
        gr.Textbox(label='Please input the website valid url:', lines=1),
        gr.Dropdown(['nouns','adjectives','verbs'],label='Select a word class')
    ],
    outputs=[gr.Textbox(label='Vocabulary:', lines=8)],
    flagging_mode='never'
)
view.launch(inbrowser=True)

