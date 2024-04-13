from mutagen.mp3 import MP3
import os
from threading import Thread
from time import sleep
import google.generativeai as genai
GOOGLE_API_KEY='AIzaSyD3CTe6s7RIWeQKVfrUaaGVEkteYOa7eKU'
genai.configure(api_key=GOOGLE_API_KEY)

# q = Queue.queue()
all_uploaded_audios = {}
all_uploaded_frames = {}
time_start = -1
APPDATA = os.path.join('.','media_output')

def scan_for_uploads():
    # Upload files that are not on Gemini API yet
    # Keep scanning forever
    while True:
        for file in os.listdir(APPDATA):
            if file.endswith('.mp3'):
                if file not in all_uploaded_audios:
                    fp=os.path.join(APPDATA,file)
                    upload_audio(fp)
            else:
                if file not in all_uploaded_frames:
                    fp=os.path.join(APPDATA,file)
                    upload_frame(fp)
        sleep(1)

def upload_audio(url):
    all_uploaded_audios[url]=response
    print(f'Uploading: {url}...')
    response = genai.upload_file(path=url)

def upload_frame(url):
    print(f'Uploading: {url}...')
    response = genai.upload_file(path=url)
    all_uploaded_frames[url]=response

def upload_all():
    frames = sorted(all_uploaded_frames.values(),key=get_timestamp)
    audios = sorted(all_uploaded_audios.values(),key=get_timestamp)
    return frames,audios

def process():
    """Called every 30 seconds to process current audio and images in the buffer."""
    print("processing")
    frames,audios=upload_all()

    # Create the prompt.
    prompt = "Watch and describe this video. An audio for it will be given after."
    prompt_audio = "Here is the audio. Describe the video with audio."

    # Set the model to Gemini 1.5 Pro.
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

    # Make GenerateContent request with the structure described above.
    def make_request(prompt, prompt_audio, files, audio):
        req = [prompt]
        for file in files:
            req.append(file.timestamp)
            req.append(file.response)
            # TODO How do we add audio exactly.. do we need the timestamp too?
            req.append(prompt_audio)
            req.append(audio.response)
            return req

    # Make the LLM request.
    req = make_request(prompt, prompt_audio, frames,audios)
    response = model.generate_content(req,
                                        request_options={"timeout": 600})

    print(response.text)
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

    while True:
        th2=Thread(target=process)
        th2.start()
        th2.join()
        sleep(30)


tr=Thread(target=main_thread)
tr.start()
tr.join(timeout=40)
