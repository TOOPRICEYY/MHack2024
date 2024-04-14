import google.generativeai as genai
GOOGLE_API_KEY='AIzaSyD3CTe6s7RIWeQKVfrUaaGVEkteYOa7eKU'
genai.configure(api_key=GOOGLE_API_KEY)


import pprint
for model in genai.list_models():
    pprint.pprint(model.name)
