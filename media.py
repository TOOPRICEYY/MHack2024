from flask import Flask, Response, request, stream_with_context
import subprocess
import shlex

app = Flask(__name__)

@app.route('/stream_frames', methods=['POST'])
def stream_frames():
    def generate_frames():
        command = "ffmpeg -i pipe:0 -f image2pipe -vcodec mjpeg -"
        process = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
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
