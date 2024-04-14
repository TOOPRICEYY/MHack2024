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

async function captureAndCombineMedia(streamId) {
    try {
        // Create a new audio context for processing audio
        const audioContext = new AudioContext();

        // Get the tab's media including video and audio
        const tabMedia = await navigator.mediaDevices.getUserMedia({
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
        });

        // Get the microphone's audio
        const micMedia = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Create source nodes for the tab and microphone audio
        const tabAudioSource = audioContext.createMediaStreamSource(tabMedia);
        const micAudioSource = audioContext.createMediaStreamSource(micMedia);

        // Merge the audio sources into a single mono channel
        const merger = audioContext.createChannelMerger(2);
        tabAudioSource.connect(merger, 0, 0);
        micAudioSource.connect(merger, 0, 0);

        const monoChannel = audioContext.createChannelSplitter(2);
        merger.connect(monoChannel);
        const monoOutput = audioContext.createGain();
        monoChannel.connect(monoOutput, 0);  // Connect only one channel for mono output

        // Create a destination node to output the processed audio stream
        const destination = audioContext.createMediaStreamDestination();
        monoOutput.connect(destination);

        // Combine the processed audio with the tab's video
        const combinedStream = new MediaStream([
            ...tabMedia.getVideoTracks(),  // Include the video track from the tab
            ...destination.stream.getAudioTracks()  // Include the combined mono audio track
        ]);

        return combinedStream;
    } catch (error) {
        console.error('Error capturing and processing media:', error);
    }
}



async function captureAndStreamMedia(streamId) {
    // First, get the tab's media.
    const stream = await captureAndCombineMedia(streamId);
    // const audioTracks = audioStream();
    // const combinedStream = new MediaStream([
    //     // ...tabStream.getVideoTracks(),  // Tab's video track
    //     ...audioTracks
    //     // ...tabStream.getAudioTracks(),  // Tab's audio track
    //     // ...micStream.getAudioTracks()  // Microphone's audio track
    // ]);
    inspectTracks(stream);  // Inspect the combined stream tracks
    streamToServer(stream, 'http://127.0.0.1:5001/stream_frames');


    // navigator.mediaDevices.getUserMedia({
    //     video: {
    //         mandatory: {
    //             chromeMediaSource: 'tab',
    //             chromeMediaSourceId: streamId
    //         }
    //     },
    //     // audio: {
    //     //     mandatory: {
    //     //         chromeMediaSource: 'tab',
    //     //         chromeMediaSourceId: streamId
    //     //     }
    //     // }
    // }).then(tabStream => {
    //     console.log("Tab media stream captured.");
    //     inspectTracks(tabStream);

    //     // Now, get the microphone's media.
       

    //     // Combine the audio tracks from both the tab and the microphone.

    //     // Get audio tracks from the combined audio stream
    //     // const audioTracks = audioStream.getAudioTracks();
    //     const combinedStream = new MediaStream([
    //         ...tabStream.getVideoTracks(),  // Tab's video track
    //         ...audioTracks
    //         // ...tabStream.getAudioTracks(),  // Tab's audio track
    //         // ...micStream.getAudioTracks()  // Microphone's audio track
    //     ]);

    //     console.log("Combined stream tracks:");
    //     inspectTracks(combinedStream);  // Inspect the combined stream tracks

    //     // Pass the combined stream for recording and streaming.
    //     streamToServer(combinedStream, 'http://127.0.0.1:5001/stream_frames');
        
    //     // .catch(error => {
    //     //     console.error("Error capturing microphone media:", error);
    //     // });
    // })
    //.catch(error => {
    //     console.error("Error capturing tab media:", error);
    // });
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
