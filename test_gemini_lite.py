from mutagen.mp3 import MP3
import os
from threading import Thread, Event
from time import sleep
import google.generativeai as genai
import google.api_core
GOOGLE_API_KEY='AIzaSyD3CTe6s7RIWeQKVfrUaaGVEkteYOa7eKU'
genai.configure(api_key=GOOGLE_API_KEY)

prompt = 'You\'re a professional analyst of interpersonal relations in an ongoing social interaction with your client, helping answer their questions as they \
come up. You\'re using a JSON interface to provide responses. Here is the context of the conversation:\n'

def call_gemini_lite(context, chatInput=None, chatHistory=None):
    # context: summary of what just happened in gemini 1.5
    # chatInput: user's question typed in chat box
    # chatHistory: copy of chat history. the whole prompt.

    # Set the model to Gemini 1.5 Pro.
    model = genai.GenerativeModel(model_name="models/gemini-1.0-pro")

    # Make GenerateContent request with the structure described above.
    request = chatHistory
    request += ('\nNew context: '+context)
    request += ('\nClient: '+chatInput)
    print(request)
    request = [request]
    tries = 0
    while tries<3:
        try:
            response = model.generate_content(request, request_options={"timeout": 600})
            print(response.text)
            return response.text
        except Exception as e:
            print("failed to talk to gemini. trying again...")
            sleep(5)
            tries+=1
    return '!!!failed to generate response from gemini'

while True:
    initial = True
    chat = input('chat box:')
    if initial:
        newContext = 'I\'m in an interview for the google gemini team n my intereviewer just greeted me'
    else:
        # use gemini 1.5 output here
        newContext = ''
    response = call_gemini_lite(newContext,chat,prompt)
    prompt+=(response+"\n")