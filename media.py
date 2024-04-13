from flask import Flask, Response, request, stream_with_context
import subprocess
import shlex
from io import BytesIO
from PIL import Image
import requests

app = Flask(__name__)

@app.route('/stream_frames', methods=['POST'])
def stream_frames():
    def generate_frames():
        command = "ffmpeg -i pipe:0 -f image2pipe -vcodec mjpeg -"
        process = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            frame_count = 0
            while True:
                chunk = request.stream.read(4096)
                if not chunk:
                    break
                process.stdin.write(chunk)
                process.stdin.flush()
                frame_data = process.stdout.read(4096)
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
                        signal = request.stream.read(4096)
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
                chunk = request.stream.read(4096)
                if not chunk:
                    break
                process.stdin.write(chunk)
                process.stdin.flush()
                audio_data = process.stdout.read(4096)
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

def process_mjpeg_stream(stream):
    frame_data = b''
    while True:
        # Read the stream in chunks
        chunk = stream.read(4096)
        if not chunk:
            break

        # Check for the JPEG start marker (0xFFD8)
        start_marker = chunk.find(b'\xff\xd8')
        if start_marker >= 0:
            # If a start marker is found, append the remaining data from the previous frame
            frame_data += chunk[:start_marker]

            # Process the complete frame
            frame_image=process_frame(frame_data)
            all_frame_images.append(frame_image)

            # Reset the frame_data and start processing the next frame
            frame_data = chunk[start_marker:]
        else:
            # If no start marker is found, append the data to the frame_data
            frame_data += chunk

    # Process the last frame, if any
    if frame_data:
        frame_image=process_frame(frame_data)
        all_frame_images.append(frame_image)

def process_frame(frame_data):
    frame_bytes = BytesIO(frame_data)
    frame_image = Image.open(frame_bytes)

    # Convert the image to the format you desire (e.g., RGB)
    frame_image = frame_image.convert("RGB")

    # Now you can use the frame_image for further processing or display
    return frame_image

# Make a POST request to the /stream_frames route
response = requests.post('http://localhost:5000/stream_frames', stream=True)

# Process the streamed frames
if response.status_code == 200:
    process_mjpeg_stream(response.raw)
else:
    print(f"Error: {response.status_code}")
