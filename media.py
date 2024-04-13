from flask import Flask, Response, request, stream_with_context
import subprocess
import shlex
from io import BytesIO
from PIL import Image
import requests

app = Flask(__name__)
CHUNK_SIZE = 4096  # Adjust chunk size as needed
CHUNK_INTERVAL = 30  # Time interval for each chunk in seconds


@app.route('/stream_frames', methods=['POST'])
def stream_frames():
    def generate_frames():
        command = "ffmpeg -i pipe:0 -f image2pipe -vcodec mjpeg -"
        process = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            frame_count = 0
            while True:
                chunk = request.stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                process.stdin.write(chunk)
                process.stdin.flush()
                frame_data = process.stdout.read(CHUNK_SIZE)
                if not frame_data:
                    break
                yield frame_data
                frame_count += 1
                if frame_count >= 30:
                    # Pause after sending 30 frames
                    frame_count = 0
                    while True:
                        # Yield an empty frame data to indicate pause
                        yield b''
                        # Wait for the downstream function to signal to resume
                        signal = request.stream.read(CHUNK_SIZE)
                        if signal.strip() == b"resume":
                            break
        finally:
            process.terminate()
            process.wait()
    return Response(stream_with_context(generate_frames()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream_audio', methods=['POST'])
def stream_audio():
    def generate_audio():
        command = "ffmpeg -i pipe:0 -f mp3 -vn -"
        process = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            while True:
                chunk = request.stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                process.stdin.write(chunk)
                process.stdin.flush()
                audio_data = process.stdout.read(CHUNK_SIZE)
                if not audio_data:
                    break
                yield audio_data
        finally:
            process.terminate()
            process.wait()
    return Response(stream_with_context(generate_audio()), mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=True, port=5000)


all_frame_images = []

def read_streamed_audio():
    response = requests.post('http://localhost:5000/stream_audio', stream=True)
    if response.status_code == 200:
        audio_buffer = io.BytesIO()  # Buffer to accumulate audio data
        start_time = time.time()  # Start time for timing chunks

        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                audio_buffer.write(chunk)

                # Check if it's time to process a chunk
                if time.time() - start_time >= CHUNK_INTERVAL:
                    process_audio_chunk(audio_buffer.getvalue())
                    audio_buffer = io.BytesIO()  # Reset the buffer
                    start_time = time.time()  # Reset the start time

        # Process any remaining audio data
        if audio_buffer.tell() > 0:
            process_audio_chunk(audio_buffer.getvalue())

    else:
        print("Failed to stream audio")
