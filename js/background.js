console.log('Background script is running');

chrome.runtime.onInstalled.addListener(function() {
  console.log('Flask Extension Installed');
});

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'check_patterns') {
      chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
          chrome.tabs.sendMessage(tabs[0].id, { action: 'check_patterns' });
      });
  }
});



