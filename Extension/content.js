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
    chrome.runtime.sendMessage({command: 'query-active-tab'}, (response) => {
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

function captureAndStreamMedia(streamId) {
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
        
    }).then(stream => {
        console.log("RECORDING!!!");
        inspectTracks(stream); // Inspect the tracks

        streamToServer(stream, 'http://127.0.0.1:5001/stream_frames', 'http://127.0.0.1:5001/stream_audio');
    })
}

function streamToServer(mediaStream, videoUrl, audioUrl) {

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
        videoRecorder.onstop = (e) => {sendData(new Blob(chunks), videoUrl);
            console.log("Video sent");    
            // saveToFile(new Blob(chunks),"file.webm")
            chunks = []
            videoRecorder.start(); // Collect data for 5.5 seconds per blob
            setTimeout(() => {videoRecorder.stop(); console.log("killed video recorder")}, 5000);
        }
        videoRecorder.start(); // Collect data for 5.5 seconds per blob

        setTimeout(() => {videoRecorder.stop(); console.log("killed video recorder")}, 5000);

        

        
        console.log("Video recorder started!!!!!");
    // } catch (e) {
    //     console.error("Error starting video recorder:", e);
    // }

    
}


function sendData(data, url) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.send(data);

    xhr.onload = function() {
        if (xhr.status === 200) {
            console.log('Success:', xhr.responseText);
        } else {
            console.log('Error:', xhr.statusText);
        }
    };

    xhr.onerror = function() {
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
