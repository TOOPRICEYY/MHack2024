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


app = Flask(__name__)
CORS(app)

output_directory = 'media_output'
os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists

def transcode_video(input_path, output_path):
    command = [
        'ffmpeg',
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
    # os.remove(video_path_old)
    # os.remove(video_path)


    response = {
        "frames": frames,
        "audio": audio_path
    }
    return json.dumps(response)

if __name__ == '__main__':
    walk =  next(os.walk("media_output"))
    for f in walk[2]: os.remove(os.path.join(walk[0],f))
    app.run(debug=True, port=5001, threaded=True)#, ssl_context=('cert.pem', 'server.key'))
    # th = Thread(target = main_call,)
