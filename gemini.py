from flask import Flask, Response, request, stream_with_context
import subprocess
import shlex
from threading import Thread
from time import sleep
from datetime import datetime
import pyaudio
import wave
from pydub import AudioSegment
import os
import shutil
import queue
import media

q_audio = queue.Queue()
q_video = queue.Queue()

class File:
  def __init__(self, file_path: str, display_name: str = None):
    self.file_path = file_path
    if display_name:
      self.display_name = display_name
    timestamp = os.path.getmtime(file_path)
    self.timestamp = datetime.datetime.fromtimestamp(timestamp)

  def set_file_response(self, response):
    self.response = response

def get_timestamp(filename):
  """Extracts the frame count (as an integer) from a filename with the format '00:00.jpg'.
  """
  parts = filename.split('.')
  if len(parts) != 2:
      return None  # Indicates the filename might be incorrectly formatted
  return parts[0]


def pull_video_and_upload(url,q):
  file=File(file_path=os.path.join(url, "audio", "out.mp3"))
  print(f'Uploading: {file.file_path}...')
  # Upload the files to the API
  response = genai.upload_file(path=file.file_path)
  file.set_file_response(response)
  q.put(file)

def pull_audio_and_upload(url,q):
  # Process each frame in the output directory
  files = os.listdir(os.path.join(url,"audio"))
  files = sorted(files)
  files_to_upload = []
  for file in files:
    files_to_upload.append(
        File(file_path=os.path.join(url, file)))

  # Upload the files to the API
  uploaded_files = []
  print(f' {len(files_to_upload)} files. This might take a bit...')

  for file in files_to_upload:
    print(f'Uploading: {file.file_path}...')
    response = genai.upload_file(path=file.file_path)
    file.set_file_response(response)
    uploaded_files.append(file)

  print(f"Completed file uploads!\n\nUploaded: {len(uploaded_files)} files")
  q.put(uploaded_files)

def call_gemini(uploaded_files, uploaded_audio):
  # Create the prompt.
  prompt = "Watch and describe this video. An audio for it will be given after."
  prompt_audio = "Here is the audio. Describe the video with audio."

  # Set the model to Gemini 1.5 Pro.
  model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

  # Make GenerateContent request with the structure described above.
  def make_request(prompt, prompt_audio, files, audio):
    request = [prompt]
    for file in files:
      request.append(file.timestamp)
      request.append(file.response)
    # TODO How do we add audio exactly.. do we need the timestamp too?
    request.append(prompt_audio)
    request.append(audio.response)
    return request

  # Make the LLM request.
  request = make_request(prompt, prompt_audio, uploaded_files, uploaded_audio)
  response = model.generate_content(request,
                                    request_options={"timeout": 600})
  print(response.text)
  return response.text

def record_and_call_gemini(url):
    # Call audio and video capture threads
    tr1=Thread(target=pull_video_and_upload, args=(url,q_video))
    tr2=Thread(target=pull_audio_and_upload, args=(url,q_audio))
    tr1.start()
    tr2.start()
    tr1.join(30)
    tr2.join(30)
    uploaded_video=q_video.get()
    uploaded_audio=q_audio.get()

    # Upload files
    # Call Gemini
    response=call_gemini(uploaded_video, uploaded_audio)

    # # Send another thread to clean up tmp files
    # th=Thread(target=clean_up,args=(url,uploaded_files,uploaded_audio))
    # th.daemon=True
    # th.start()

    return response

def main_thread():
  # Record meeting by 30 second chunks
  while True:
    get_url()
    th=Thread(target=record_and_call_gemini,args=(url,))
    th.start()
    sleep(30) 
    # Kill thread if it runs for too long
    th.join(60)

url=os.path.join('.',"tmp")
os.makedirs(url,exist_ok=True)
tr=Thread(target=main_thread)
tr.start()
tr.join()
shutil.rmtree(url)
