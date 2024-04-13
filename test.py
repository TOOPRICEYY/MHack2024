import select
import subprocess
import shlex

def test_non_blocking_io():
    video_command = "ffmpeg -i pipe:0 -vframes 1 -f image2pipe -vcodec mjpeg -"
    print("hi")
    video_process = subprocess.Popen(shlex.split(video_command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    data = b"some data"
    while data:
        ready_to_write = select.select([], [video_process.stdin], [], 5)[1]
        if ready_to_write:
            written = video_process.stdin.write(data)
            data = data[written:]
        else:
            print("Subprocess not ready to write")
            break

    video_process.stdin.close()
    video_process.wait()
    print("done")
test_non_blocking_io()