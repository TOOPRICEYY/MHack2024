from flask import Flask, request, send_file
from flask_cors import CORS
import subprocess
import shlex
import os
import json
import time
import os
import threading

app = Flask(__name__)
CORS(app)

output_directory = 'media_output'
os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists

@app.route('/stream_frames', methods=['POST'])
def stream_frames():
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # Prepare command to extract 10 frames and audio

    video_command = "ffmpeg -i pipe:0 -vframes 1 -f image2pipe -vcodec mjpeg -"
    audio_command = f"ffmpeg -i pipe:0 -vn -acodec libmp3lame -f mp3 -y media_output/{time.time()}.mp3"

    # Start subprocesses
    video_process = subprocess.Popen(shlex.split(video_command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    audio_process = subprocess.Popen(shlex.split(audio_command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Read the incoming data from request
    chunk = request.get_data()
    if chunk:
        # Write data to both subprocesses
        def write_to_stdin(pp, chunk,im=False):
            pp.stdin.write(chunk)
            pp.stdin.flush()
            print("wrote")
            pp.stdin.close()

        thread1 = threading.Thread(target=write_to_stdin, args=(video_process, chunk,True))
        thread1.start()

        thread2 = threading.Thread(target=write_to_stdin, args=(audio_process, chunk))
        thread2.start()

        # Read video frames output
        # frame_data = video_process.stdout.read()
        frames = []
        for i in range(1):
            frame_data = video_process.stdout.read()  # Adjust buffer size as necessary
            frame_path = os.path.join(output_directory, f'frame_{time.time()+i}.jpg')
            with open(frame_path, 'wb') as f:
                f.write(frame_data)
            frames.append(frame_path)

        # Wait for subprocesses to finish
        video_process.wait()
        audio_process.wait()

        # Return paths to saved files
        response = {
            "frames": frames,
            "audio": os.path.join(output_directory, f"media_output/{time.time()}.mp3")
        }
        return json.dumps(response)

    return "No data received", 400


if __name__ == '__main__':
    walk =  next(os.walk("media_output"))
    for f in walk[2]: os.remove(os.path.join(walk[0],f))
    app.run(debug=True, port=5001, threaded=True)#, ssl_context=('cert.pem', 'server.key'))
