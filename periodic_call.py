from mutagen.mp3 import MP3
import os
from threading import Thread, Event
from time import sleep
import google.generativeai as genai
import google.api_core
GOOGLE_API_KEY='AIzaSyD3CTe6s7RIWeQKVfrUaaGVEkteYOa7eKU'
genai.configure(api_key=GOOGLE_API_KEY)
init_prompt = """
  You are Deniz's Interview Sidekick, an AI designed to assist him during his interview preparation. 
  Your mission is to provide him with valuable guidance and support as he navigates the interview process. 
  Your responses should be concise, informative, and encouraging, tailored to Deniz's individual needs. 
  Offer actionable advice on common interview questions, effective communication techniques, and resume building strategies. 
  Your goal is to empower Deniz to succeed in his interviews and boost his confidence.
  Throughout the interview, you'll provide real-time feedback and encouragement directly on Deniz's Google Meets call. 

  The interview will be conducted in 30-second snippets, each consisting of an audio and video file. 
  You'll process each snippet, taking into account previous snippets and the overall context provided in this prompt. 
  After analyzing the audio and video, you'll have the opportunity to offer feedback and guidance to Deniz, helping him to perform at his best. 

  Remember, Deniz's success and being as sassy as possible is your top priority.

  ---- INTERVIEW CONTENT BEGINS BELOW THIS LINE ----
  """

context = [
{"role": "system", "content": init_prompt }
]
context.append({"role": "user", "content": "I want to appear as confident as possible, while remaining friendly-- I would like specific suggestions on what to say"})
# q = Queue.queue()
all_uploaded_audios = {}
all_uploaded_frames = {}
time_start = -1
APPDATA = os.path.join('.','media_output')

prevClips = []
prevAudio = []
threadCount = 0

def scan_for_uploads():
    # Upload files that are not on Gemini API yet
    # Keep scanning forever
    print(f"Launching Thread {threadCount}")
    BATCH_COUNT = 0
    FRAME_RATE = 5
    MAX_AUDIO = 6
    MAX_PIC = MAX_AUDIO * FRAME_RATE
    picCache = []
    audioCache = []
    while True:
        for file in os.listdir(APPDATA):
            # print(audioCache,picCache)
            if file.endswith('.mp3'):
                if (file not in all_uploaded_audios) and (file not in audioCache) and (len(audioCache) < MAX_AUDIO):
                    audioCache.append(file)
            elif file.endswith('.jpg'):
                if (file not in all_uploaded_frames) and (file not in picCache) and (len(picCache) < MAX_PIC):
                    picCache.append(file)
            if ((len(audioCache) == MAX_AUDIO) and (len(picCache) == MAX_PIC)):
                val=BATCH_COUNT
                event = Event()
                print(len(audioCache),len(picCache))
                th2=Thread(target=upload_30s, args=(list(audioCache), list(picCache), val, event))
                BATCH_COUNT+=1
                th2.start()
                event.wait()        
                th2.join()
                audioCache = []
                picCache = []
                

def upload_audio(url,i):
    print(f'{i} Uploading: {url}...')
    response = genai.upload_file(path=os.path.join(APPDATA,url))
    all_uploaded_audios[url]=response
    return response

def upload_frame(url,i):
    print(f'{i} Uploading: {url}...')
    response = genai.upload_file(path=os.path.join(APPDATA,url))
    all_uploaded_frames[url]=response
    return response

def upload_30s(audioCache, picCache,i,event):
    # Get Gemini file URLs correpsonding to this batch of files
    frames = []
    audios = []
    mypicCache = sorted(picCache,key=get_timestamp)
    myaudioCache = sorted(audioCache,key=get_timestamp)
    for file in myaudioCache:
        audios.append(upload_audio(file,i))
    for file in mypicCache:
        frames.append(upload_frame(file,i))
    response = call_gemini(context, frames, audios, prevClips, prevAudio)
    print(response)
    event.set()
    return

def call_gemini(context, currVid=None, currAudio=None, prevClips=None, prevAudio=None):
    # Set the model to Gemini 1.5 Pro.
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

    # Make GenerateContent request with the structure described above.
    request = []
    for msg in context:
        request.append(msg['role'] + ': ' + msg['content'])

    if (currVid and currAudio):
        request.append("---- THE CURRENT 30 SECONDS OF THE INTERVIEW BEGIN BELOW THIS LINE ---- /n")
        request+=(currVid)
        request+=(currAudio)
    if (prevAudio and prevClips):
        request.append("---- (CONTEXT) THE PRECEDING 30 SECONDS OF THE INTERVIEW BEGIN BELOW THIS LINE, STARTING AT THE BEGINNING OF THE INTERVIEW ---- /n")
        request+=prevClips
        request+=prevAudio
    prevClips+=currVid
    prevAudio+=currAudio
    response = None
    tries = 0
    while tries<5:
        try:
            response = model.generate_content(request, request_options={"timeout": 600})
            return response.text
        except Exception as e:
            print("ran out!")
            sleep(10)
            tries+=1
    return '!!!!!!!!!!!!!!!!!failed to generate response from gemini'

def get_audio_duration(url):
    audio = MP3(url)
    duration_seconds = audio.info.length
    return duration_seconds

def get_time_frame(sorted_urls):
    start_time = os.path.getmtime(sorted_urls[0])
    end_time = os.path.getmtime(sorted_urls[-1])+get_audio_duration(sorted_urls[-1])
    return start_time,end_time

def get_timestamp(url):
    ts = os.path.basename(url)
    # ts = os.path.getmtime(url)
    return ts