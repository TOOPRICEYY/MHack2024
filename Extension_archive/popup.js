let tabId;

// Fetch tab immediately
chrome.runtime.sendMessage({command: 'query-active-tab'}, (response) => {
    tabId = response.id;
});