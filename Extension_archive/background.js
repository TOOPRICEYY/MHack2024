function sendData(data, url) {
  console.log("DATA sent to",url)
  const xhr = new XMLHttpRequest();
  xhr.timeout = 3; // Set timeout as desired, e.g., 5000 milliseconds (5 seconds)

  // Optional: Handle timeout event
  xhr.ontimeout = function () {
      console.error("The request for " + url + " timed out.");
  };
  xhr.open('PUT', url, true);
  xhr.send(data);
}
console.log("DATA sent to sdf sdf")

sendData("","https://127.0.0.1:5001/stream_frames");


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "startCapture") {
      // Use message.tabId to specify the target tab for APIs that require it
      chrome.desktopCapture.chooseDesktopMedia(["audio"], targetTab = sender.tab, (streamId) => {
        if (!streamId) {
          console.error('User cancelled the desktop capture.');
          return;
        }
        navigator.mediaDevices.getUserMedia({
          audio: {
            mandatory: {
              chromeMediaSource: 'desktop',
              chromeMediaSourceId: streamId
            }
          }
        }).then(handleStream).catch(handleError);
      });
    }
      else if(message.action == "streamData"){
        console.log("streaming to",message.data.url)
        sendData(message.data,message.url);

      }
});
  



  function handleStream(stream) {
    // Handle the stream as before
  }
  
  function handleError(error) {
    console.error('Error capturing audio: ', error);
  }
  