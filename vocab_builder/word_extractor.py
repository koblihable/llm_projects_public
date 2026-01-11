import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI

# creating environment
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')
openai = OpenAI()
MODEL = 'gpt-4o-mini'

# get the url string
website_str = input('What site whoud you like to search? ')

# get confirmation that the url is valid- returns YES or NO
def confirm_url(url):
    response = openai.chat.completions.create(
        messages=[
            {'role':'system','content':'you are helpful ai'},
            {'role':'user','content':f'please check if {website_str} is a valid and complete url. Please answer YES or NO only'}
        ],
        model=MODEL
    )
    return response.choices[0].message.content

# get the word class to be listed - testing with hardcoded word classes
supported_word_classes = ['nouns','verbs','adjectives']
word_class = input('What kind of word class would you like to list? Please select between "NOUNS", "VERBS" or "ADJECTIVES": ')

while word_class.lower() not in supported_word_classes:
    word_class = input('Not a supported word class. Please choose again ')

# website headers
'''
The headers identify us as best as can be done as real users rather than python code
To find a header - google the webpage, press ctrl+shift+i to enter developer tools
                 - go to network tab
                 - reload the page to get some activity
                 - click on any resource to see details
                 - the header we are after is request header: user agent
'''
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

# scrape the website to get the text and the title
# this code is borrowed
class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)
    def get_contents(self):
        return self.text

while confirm_url(website_str)=='NO':
    website_str = input('Please submit a valid url: ')
    result = confirm_url(website_str)

# create the api call
def list_of_words(url):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {'role':'system','content':'you are a language teacher'},
            {'role':'user','content':f'Find all {word_class} in the text and give me their list together with their translation into English - {Website(website_str).get_contents()}'}
        ]
    )
    return response.choices[0].message.content

# return the vocabulary
print(list_of_words(website_str))
