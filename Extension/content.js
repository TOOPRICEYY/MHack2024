let tabId;

// Initialize the extension's functionality once the document is ready
if (document.readyState !== 'loading') {
    console.log('Document is ready woo');
    myInitCode();
} else {
    document.addEventListener('DOMContentLoaded', function () {
        console.log('Document was not ready, place code here');
        myInitCode();
    });
}

function myInitCode() {
    // Request the active tab ID from the background script
    chrome.runtime.sendMessage({ command: 'query-active-tab' }, (response) => {
        tabId = response.id;
        console.log("Querying tab");
    });
    console.log("Past tab query");

    // Listener for messages from the background script
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        console.log("Content running");
        captureAndStreamMedia(request.streamId);
    });
    console.log("On to media query");
}
function inspectTracks(mediaStream) {
    mediaStream.getTracks().forEach(track => {
        console.log(`Track kind: ${track.kind}, enabled: ${track.enabled}, readyState: ${track.readyState}`);
    });
}

async function captureAndCombineAudio(streamId) {
    try {
        // Create a new audio context
        const audioContext = new AudioContext();

        // Get the media streams
        const tabStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                mandatory: {
                    chromeMediaSource: 'tab',
                    chromeMediaSourceId: streamId
                }
            }
        });
        const micStream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        // Create source nodes from the streams
        const tabSource = audioContext.createMediaStreamSource(tabStream);
        const micSource = audioContext.createMediaStreamSource(micStream);

        // Create a ChannelMergerNode to combine the two audio sources into one
        const merger = audioContext.createChannelMerger(2);

        // Connect both sources to the merger
        // Since we want mono output, we connect both inputs to the same channel (channel 0)
        tabSource.connect(merger, 0, 0);
        micSource.connect(merger, 0, 0);

        // Optional: Use a ChannelSplitterNode to discard one channel if necessary
        const splitter = audioContext.createChannelSplitter(2);
        merger.connect(splitter);
        const monoOutput = audioContext.createGain();
        splitter.connect(monoOutput, 0); // Connect only the first channel for mono

        // Connect the output to the destination to play out the speakers (for testing)
        monoOutput.connect(audioContext.destination);

        // Also, create a MediaStream from the output for further use, such as sending to a server
        const outputStream = monoOutput.stream || audioContext.createMediaStreamDestination().stream;

        return outputStream;
    } catch (error) {
        console.error('Error processing audio:', error);
    }
}


function captureAndStreamMedia(streamId) {
    // First, get the tab's media.
    navigator.mediaDevices.getUserMedia({
        video: {
            mandatory: {
                chromeMediaSource: 'tab',
                chromeMediaSourceId: streamId
            }
        },
        audio: {
            mandatory: {
                chromeMediaSource: 'tab',
                chromeMediaSourceId: streamId
            }
        }
    }).then(tabStream => {
        console.log("Tab media stream captured.");
        inspectTracks(tabStream);

        // Now, get the microphone's media.
        navigator.mediaDevices.getUserMedia({
            audio: true // Default audio source (microphone)
        }).then(micStream => {
            console.log("Microphone media stream captured.");
            inspectTracks(micStream);

            // Combine the audio tracks from both the tab and the microphone.
            
            const combinedStream = new MediaStream([
                ...tabStream.getVideoTracks(),  // Tab's video track
                ...micStream.getAudioTracks(),  // Microphone's audio track
                ...tabStream.getAudioTracks()  // Tab's audio track
            ]);

            console.log("Combined stream tracks:");
            inspectTracks(combinedStream);  // Inspect the combined stream tracks

            // Pass the combined stream for recording and streaming.
            streamToServer(combinedStream, 'http://127.0.0.1:5001/stream_frames', 'http://127.0.0.1:5001/stream_audio');
        }).catch(error => {
            console.error("Error capturing microphone media:", error);
        });
    }).catch(error => {
        console.error("Error capturing tab media:", error);
    });
}


delay = 5000
function streamToServer(mediaStream, videoUrl) {

    // try {
    //     const audioRecorder = new MediaRecorder(mediaStream, { mimeType: 'audio/webm' });
    //     audioRecorder.ondataavailable = event => {
    //         if (event.data.size > 0) {
    //             sendData(event.data, audioUrl);
    //             console.log("Audio sent");
    //         }
    //     };
    //     audioRecorder.start(5500); // Collect data for 5.5 seconds per blob
    //     console.log("Audio recorder started");
    // } catch (e) {
    //     console.error("Error starting audio recorder:", e);
    // }

    // try {
    const videoRecorder = new MediaRecorder(mediaStream);
    chunks = [];

    videoRecorder.ondataavailable = (e) => {

        chunks.push(e.data);
        console.log("dataAvailable");


    };
    videoRecorder.onstop = (e) => {
        sendData(new Blob(chunks), videoUrl, () => {
            console.log("Video sent");
            // saveToFile(new Blob(chunks),"file.webm")
            chunks = []
            videoRecorder.start(); // Collect data for 5.5 seconds per blob
            setTimeout(() => { videoRecorder.stop(); console.log("killed video recorder") }, 5000);
        });
    }
    videoRecorder.start(); // Collect data for 5.5 seconds per blob

    setTimeout(() => { videoRecorder.stop(); console.log("killed video recorder") }, 5000);




    console.log("Video recorder started!!!!!");
    // } catch (e) {
    //     console.error("Error starting video recorder:", e);
    // }


}


function sendData(data, url, callback = () => { }) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.send(data);

    let loaded = false;
    xhr.onload = function () {
        if (xhr.status === 200) {
            console.log('Success:', xhr.responseText);
        } else {
            console.log('Error:', xhr.statusText);
        }
        if (!loaded) callback();
        loaded = true;
    };
    setTimeout(() => { if (!loaded) { console.error("POST to", url, "timed out"); callback(); loaded = true } }, 5000)

    xhr.onerror = function () {
        console.error('Network error.');
    };
}


function saveToFile(blob, name) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    document.body.appendChild(a);
    a.style = 'display: none';
    a.href = url;
    a.download = name;
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
}
