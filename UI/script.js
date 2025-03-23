function toggleAlarm() {
    fetch('/toggle-alarm', { method: 'POST' })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error('Error:', error));
}

function fetchLogs() {
    fetch('/logs')
        .then(response => response.json())
        .then(data => {
            const logContainer = document.getElementById('logContainer');
            logContainer.innerHTML = data.logs.map(log => `<p>${log}</p>`).join('');
        });
}

setInterval(fetchLogs, 3000);
