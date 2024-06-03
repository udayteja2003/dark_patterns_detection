document.addEventListener('DOMContentLoaded', function () {
    const checkButton = document.getElementById('checkButton');
    
    checkButton.addEventListener('click', function () {
        chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            const url = tabs[0].url;

            // Programmatically inject content script
            chrome.tabs.sendMessage(tabs[0].id, { action: 'call_content' }, function() {
                // Send a message to the content script to run logic
                chrome.tabs.sendMessage(tabs[0].id, { action: 'check_patterns', url: url }, function(response) {
                    if (chrome.runtime.lastError) {
                        console.error(chrome.runtime.lastError);
                        return;
                    }
                   
                    console.log('Received response from content.js:', response);
                    displayDetectedPatterns(response.detected_patterns);
                });
            
            
            });
        });
    });
    document.getElementById("knowMoreButton").addEventListener("click", function(event) {
        // Prevent the default behavior (e.g., navigating to the href)
        event.preventDefault();
        console.log("Button clicked");
        // Your custom JavaScript code can go here
        // For example, you can open the link in a new tab:
        window.open("https://www.deceptive.design/", "_blank");
    });

    function displayDetectedPatterns(detectedPatterns) {
        const resultContainer = document.getElementById('result');
        const ul = document.createElement('ul');
      
        detectedPatterns.forEach(pattern => {
            const li = document.createElement('li');
            li.textContent = pattern;
            ul.appendChild(li);
        });
      
        resultContainer.innerHTML = ''; // Clear previous results
        resultContainer.appendChild(ul);
    }
});
