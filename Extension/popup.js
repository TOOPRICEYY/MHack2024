let tabId;

// Fetch tab immediately
chrome.runtime.sendMessage({command: 'query-active-tab'}, (response) => {
    tabId = response.id;
});

// On command, get the stream ID and forward it back to the service worker
// chrome.commands.onCommand.addListener((command) => {
//     chrome.tabCapture.getMediaStreamId({consumerTabId: tabId}, (streamId) => {
//         chrome.runtime.sendMessage({
//             command: 'tab-media-stream',
//             tabId: tabId,
//             streamId: streamId
//         })
//     });
// });

document.getElementById('startCapture').addEventListener('click', function() {
    // chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    //     const currentTab = tabs[0];
    //     chrome.runtime.sendMessage({action: "startCapture", tabId: currentTab.id});
    // });
    chrome.runtime.sendMessage({ command: "startCapture", tabId: tabId });

    // chrome.tabCapture.getMediaStreamId({consumerTabId: tabId}, (streamId) => {
    //     chrome.runtime.sendMessage({
    //         command: 'tab-media-stream',
    //         tabId: tabId,
    //         streamId: streamId
    //     })
    // });

  });
  