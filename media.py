from flask import Flask, request
from flask_cors import CORS
import os
import json
import time
from moviepy.editor import VideoFileClip
from PIL import Image, ImageOps
import numpy as np
import subprocess
from pydub import AudioSegment
import numpy as np
import imageio
from periodic_call import scan_for_uploads, chatQuery, textIsComplete, textBuffer, responses
from threading import Thread
import queue


app = Flask(__name__)
CORS(app)

output_directory = 'media_output'
os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists

sendPipe = queue.Queue()
receivePipe = queue.Queue()
geminiPipe = queue.Queue()


def transcode_video(input_path, output_path):
    command = [
        'ffmpeg',
        '-loglevel', 'quiet',
        '-i', input_path,
        '-r','3',
        '-c:v', 'libx264', 
        '-c:a', 'aac',  # Transcode the audio stream to AAC
        '-b:a', '192k',  # Set the audio bitrate to 192 kbps
        '-crf', '15',
        output_path
    ]
    try:
        subprocess.run(command, check=True)
        print("Audio transcoded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during audio transcoding: {e}")
        return False
    return True

@app.route('/stream_frames', methods=['POST'])
def stream_frames():
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Read the incoming video data from request
    video_data = request.get_data()
    if not video_data:
        return "No data received", 400

    video_path = os.path.join(output_directory, f"input_{time.time()}.mp4")
    
    with open(video_path, 'wb') as f:
        f.write(video_data)

    # Load video using MoviePy
    # clip = None
    video_path_old = video_path
    video_path = video_path.split(".")
    video_path[1] = video_path[1]+"encoded"
    video_path = ".".join(video_path)
    transcode_video(video_path_old,video_path)

    try:
        clip = VideoFileClip(video_path)
    except Exception as e:
        return json.dumps({"error": f"Error loading video file: {str(e)}"}), 500

    frames = []
    num_frames = 5
    frame_times = np.linspace(0, min(clip.duration, 1), num_frames)

    for i, t in enumerate(frame_times):
        frame = clip.get_frame(t)
        frame_path = os.path.join(output_directory, f'frame_{time.time() + i}.jpg')
        frame = 0 - frame
        img = Image.fromarray((255 * frame).astype(np.uint8))
        img.save(frame_path)
        frames.append(frame_path)

    audio_path = os.path.join(output_directory, f"audio_{time.time()}.mp3")
    # clip.audio.write_audiofile(audio_path, codec='aac')

    
    audio = AudioSegment.from_file(video_path, format="mp4")
    audio.export(audio_path, format="mp3")
    os.remove(video_path_old)
    os.remove(video_path)

    response = {
        "frames": frames,
        "audio": audio_path
    }
    return json.dumps(response)


@app.route('/send_text_prompt', methods=['POST'])
def send_text_prompt():
    # global textIsComplete
    # global chatQuery
    # global textBuffer

    # chatQuery = json.loads(request.get_data())["message"]
    # # print(chatQuery)
    # receivePipe.put(chatQuery)
    # textIsComplete
    # response = sendPipe.get()
    # # if(textIsComplete==-1): return json.dumps({"response":"Gemini Api Error"})
    data = None
    try: data = geminiPipe.get(timeout=30)
    except: return json.dumps({"response":"null"})
    return json.dumps({"response":data})

dataStage = None
@app.route('/get_state_data', methods=['GET'])
def get_state_data():
    # return json.dumps({"status":"200","response":{'joy\":': 0.5, 'sadness\":': 0.5, 'anger\":': 0.5, 'fear\":': 0.5, 'disgust\":': 0.5, 'surprise\":': 0.5}})
    try: data = geminiPipe.get(timeout=320)
        
    except:  return json.dumps({"response":{"status":"404"}})

    # print(data)
    print("\n\n\n\n")

    emotions = ['joy":', 'sadness":', 'anger":', 'fear":', 'disgust":', 'surprise":']
    fullstr = data
    output = {x:.5 for x in emotions}
    for x in emotions:
        try: index = fullstr.lower().index(x)
        except: continue
        if(index!=-1): 
            print("'"+fullstr[len(x)+index+1:len(x)+index+4]+"'")
            try: output[x] = float(fullstr[len(x)+index+1:len(x)+index+4])/2.0
            except: pass

    print(output)
    if(data==None): return json.dumps({"response":{"status":"404"}})
    return json.dumps({"response":output})


import threading
import atexit
import ctypes

def kill_thread(thread):
    """Terminate a python thread from another thread."""
    if not thread.is_alive():
        return

    # Get a handle to the thread's underlying native thread object
    thread_id = thread.native_id

    # Call the appropriate OS-specific function to terminate the thread
    if ctypes.windll:
        process = ctypes.windll.kernel32.TerminateThread(thread_id, 0)
    else:
        process = ctypes.cdll.LoadLibrary("libc.so.6")
        process.pthread_cancel(thread_id)

def exit_handler():
    """Clean up handler to kill all running threads."""
    threads = threading.enumerate()
    for thread in threads:
        if thread != threading.current_thread():
            print(f"Terminating thread: {thread.name}")
            kill_thread(thread)

# Register the exit handler

atexit.register(exit_handler)
if __name__ == '__main__':
    walk =  next(os.walk("media_output"))
    for f in walk[2]: os.remove(os.path.join(walk[0],f))
   
    tr=Thread(target=scan_for_uploads,args=(receivePipe,sendPipe,geminiPipe))
    tr.start()
    app.run(debug=True, port=5001)#, ssl_context=('cert.pem', 'server.key'))
