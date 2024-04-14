// background.js

  

chrome.runtime.onMessage.addListener(
    (request, sender, sendResponse) => {
        // Popup asks for current tab

        if (request.command === 'query-active-tab') {
            console.log("sendingTab")
            chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
                if (tabs.length > 0) {
                    sendResponse({id: tabs[0].id});
                }
            });
            // chrome.tabs.query({active: true}, (tabs) => {
            //     if (tabs.length > 0) {
            //         sendResponse({id: tabs[0].id});
            //     }
            // });

            return true;
        }
        else if (request.command === "startCapture") {
            console.log("sendingMedia")
 
            chrome.tabCapture.getMediaStreamId({consumerTabId: request.tabId}, (streamId) => {
                if (chrome.runtime.lastError) {
                    console.error('Error capturing media: ', chrome.runtime.lastError.message);
                    sendResponse({error: chrome.runtime.lastError.message});
                    return;
                }
    
                console.log("Media stream ID obtained:", streamId);
                chrome.tabs.sendMessage(request.tabId, {
                    command: 'tab-media-stream',
                    streamId: streamId
                });
            });
            return true; // Indicates that the response is sent asynchronously
        }

        else if (request.action === "executeReact") {
            chrome.scripting.executeScript({
                target: { tabId: request.tabId },
                files: ['react-Gui/build/static/js/main.88744a5a.js']
              }, (results) => {
                if (chrome.runtime.lastError) {
                  sendResponse({status: "failed", error: chrome.runtime.lastError.message});
                  return;
                }
                sendResponse({status: "success", data: results});
              });
              
            return true; // Indicates that sendResponse will be asynchronous
          }
        // } else if(message.action == "streamData"){
        //     console.log("streaming to",message.data.url)
        //     sendData(message.data,message.url);
    
        //   }
        

        // Popup sent back media stream ID, forward it to the content script
        // if (request.command === 'tab-media-stream') {
        //     console.log("sendingMedia")

        //     chrome.tabs.sendMessage(request.tabId, {
        //         command: 'tab-media-stream',
        //         streamId: request.streamId
        //     });
        // }
    }
);