document.getElementById('submit-btn').addEventListener('click', function(event) {
    event.preventDefault();
    
    const videoUrl = document.getElementById('video_url').value;

    fetch('/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ video_url: videoUrl })
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text); });
        }
        return response.json();  // Parse JSON response
    })
    .then(data => {
        if (data.summary) {
            document.getElementById('summary').innerText = data.summary;
        } else {
            console.error('No summary available.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
