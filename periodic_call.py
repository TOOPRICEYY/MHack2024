from mutagen.mp3 import MP3
import os
from threading import Thread
from time import sleep
import google.generativeai as genai
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

  Remember, Deniz's success is your top priority.

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

def scan_for_uploads():
    # Upload files that are not on Gemini API yet
    # Keep scanning forever
    picCache = []
    audioCache = []
    while True:
        for file in os.listdir(APPDATA):
            if file.endswith('.mp3'):
                if (file not in all_uploaded_audios) and (file not in audioCache) and (len(audioCache) < 6):
                    audioCache.append(file)
            else:
                if (file not in all_uploaded_frames) and (file not in picCache) and (len(picCache) < 30):
                    picCache.append(file)
            if ((len(audioCache) == 6) and (len(picCache) == 30)):
                th2=Thread(target=upload_30s, args=[audioCache, picCache])
                th2.start()
                upload_30s(audioCache, picCache)
                th2.join() #TODO CHECK THIS!!!
                audioCache = []
                picCache = []
        sleep(1)

def upload_audio(url):
    all_uploaded_audios[url]=response
    print(f'Uploading: {url}...')
    response = genai.upload_file(path=url)
    all_uploaded_audios[url]=response
    return response

def upload_frame(url):
    print(f'Uploading: {url}...')
    response = genai.upload_file(path=url)
    all_uploaded_frames[url]=response
    return response

def upload_30s(audioCache, picCache):
    # Get Gemini file URLs correpsonding to this batch of files
    frames = []
    audios = []
    picCache = sorted(picCache.values(),key=get_timestamp)
    audioCache = sorted(audioCache.values(),key=get_timestamp)

    for file in audioCache:
        audios.append(upload_audio(file))
    for file in picCache:
        frames.append(upload_frame(file))
    #frames = [all_uploaded_frames[url] for url in match_video(audioCache)]
    #audios = [all_uploaded_audios[url] for url in audioCache]
    response = call_gemini(frames, audios)
    print(response)


    print("processing")

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
    response = model.generate_content(request, request_options={"timeout": 600})
    return response.text

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

def match_video(audios):
    audios = sorted(audios, key=get_timestamp)
    start_time, end_time = get_time_frame(audios)
    imgs = []
    for im in os.listdir(APPDATA):
        imfp = os.path.join(APPDATA,im)
        ts = get_timestamp(imfp)
        if start_time<=ts<=end_time:
            imgs.append(imfp)
    return imgs

def main_thread():
    th1=Thread(target=scan_for_uploads)
    th1.start()

tr=Thread(target=main_thread)
tr.start()
tr.join(timeout=40)
