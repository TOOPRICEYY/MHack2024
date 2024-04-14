from mutagen.mp3 import MP3
import os
from threading import Thread, Event
from time import sleep
import google.generativeai as genai
import google.api_core
GOOGLE_API_KEY='AIzaSyD3CTe6s7RIWeQKVfrUaaGVEkteYOa7eKU'
genai.configure(api_key=GOOGLE_API_KEY)
# textBuffer=''
# textIsComplete=False
# from media import chatQuery

prompt = '[ur prompt here]'

def call_gemini_lite(context, chatHistory=None):
    global textIsComplete
    global textBuffer
    global chatQuery
    # context: summary of what just happened in gemini 1.5
    # chatInput: user's question typed in chat box
    # chatHistory: copy of chat history. the whole prompt.

    # Set the model to Gemini 1.5 Pro.
    model = genai.GenerativeModel(model_name="models/gemini-1.0-pro")

    # Make GenerateContent request with the structure described above.
    request = chatHistory
    request += ('\nNew context: '+context)
    request += ('\nQuestion: '+chatQuery)
    print(request)
    request = [request]
    response = model.generate_content(request, request_options={"timeout": 600}, stream=True)
    textIsComplete = False
    for token in response:
        print(token.text)
        textBuffer=textBuffer+token.text
        print(textBuffer)
    textIsComplete = True
    chatQuery = ''
    return

chat = input('chat box:')
response = call_gemini_lite('',chat,prompt)