from flask import Flask, Response, request, stream_with_context
import subprocess
import shlex

app = Flask(__name__)

def stream_video_frames(url):
    """
    Use ffmpeg to stream video frames from a URL and convert them to JPEG.
    Yields JPEG frames.
    """
    command = f"ffmpeg -i {shlex.quote(url)} -f image2pipe -vcodec mjpeg -"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True, bufsize=10**8)
    while True:
        # Read frame-by-frame
        data = process.stdout.read(4096)
        if not data:
            break
        yield data

def stream_audio_data(url):
    """
    Use ffmpeg to extract and stream audio from a video URL.
    Yields audio data in MP3 format.
    """
    command = f"ffmpeg -i {shlex.quote(url)} -f mp3 -vn -"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True, bufsize=10**8)
    while True:
        # Read audio data
        data = process.stdout.read(4096)
        if not data:
            break
        yield data

@app.route('/stream_frames')
def stream_frames():
    video_url = request.args.get('video_url')
    if not video_url:
        return "Missing video_url parameter", 400
    return Response(stream_with_context(stream_video_frames(video_url)), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream_audio')
def stream_audio():
    video_url = request.args.get('video_url')
    if not video_url:
        return "Missing video_url parameter", 400
    return Response(stream_with_context(stream_audio_data(video_url)), mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=True, port=5000)