const endpoint = 'http://127.0.0.1:5000/';

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'call_content') {
    const script = document.createElement('script');
    script.src = chrome.extension.getURL('content.js');
    (document.head || document.documentElement).appendChild(script);
    script.onload = function() {
        script.remove();
    };
}  
  if (request.action === 'check_patterns') {
      const url = request.url;
      console.log('Content script received URL from popup:', url);
  
      // Make a POST request to the Flask app to detect patterns
      fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url }),
      })
      .then(response => response.json())
      .then(data => {
        // Example: Send detected patterns back to popup.js
        sendResponse({detected_patterns: data.detected_patterns });
      })
      .catch(error => {
        console.error('Error detecting patterns:', error);
        sendResponse({ detected_patterns: [] });  // Return an empty array in case of an error
      });
  
      // Return true to indicate that sendResponse will be called asynchronously
      return true;
    }
  });