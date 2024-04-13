// Service worker sent us the stream ID, use it to get the stream
let tabId;

// Fetch tab immediately
if (document.readyState !== 'loading') {
    console.log('document is already ready, just execute code here');
    myInitCode();
} else {
    document.addEventListener('DOMContentLoaded', function () {
        console.log('document was not ready, place code here');
        myInitCode();
    });
}
function myInitCode() {

// content.js
chrome.runtime.sendMessage({command: 'query-active-tab'}, (response) => {
    tabId = response.id;
    console.log("querying tab")
});
console.log("Past tab query")

// Example of functionality to run immediately
    
    
    // Additional code to perform actions goes here

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("content running")
    navigator.mediaDevices.getUserMedia({
        video: true,
        video: {
            mandatory: {
                chromeMediaSource: 'tab',
                chromeMediaSourceId: request.streamId
            }
        },
        audio: true,
        audio: {
            mandatory: {
                chromeMediaSource: 'tab',
                chromeMediaSourceId: request.streamId
            }
        }
    })
    .then((stream) => {
        // Once we're here, the audio in the tab is muted
        // However, recording the audio works!
        console.log("RECORDING!!!")
        const recorder = new MediaRecorder(stream);
        const chunks = [];
        recorder.ondataavailable = (e) => {
            chunks.push(e.data);
        };
        recorder.onstop = (e) => saveToFile(new Blob(chunks), "test.webm");
        recorder.start();
        setTimeout(() => recorder.stop(), 5000);
    });
});

console.log("on to media query")
// chrome.tabCapture.getMediaStreamId({consumerTabId: tabId}, (streamId) => {
//     console.log("Getting media")
//     chrome.runtime.sendMessage({
//         command: 'tab-media-stream',
//         tabId: tabId,
//         streamId: streamId
//     })
// });
}

function saveToFile(blob, name) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    a.href = url;
    a.download = name;
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
}
