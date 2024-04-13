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
  });
  
  function handleStream(stream) {
    // Handle the stream as before
  }
  
  function handleError(error) {
    console.error('Error capturing audio: ', error);
  }
  