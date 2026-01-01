let ws;

document.addEventListener('DOMContentLoaded', function() {
    const client_id = Date.now()
    document.querySelector("#ws-id").textContent = client_id;

    const protocol = location.protocol === "https:" ? "wss://" : "ws://";
    ws = new WebSocket(protocol + location.host + `/ws/${client_id}`);

    ws.onmessage = function(event) {
        const messages = document.getElementById('messages')
        const message = document.createElement('li')
        message.textContent = event.data
        messages.appendChild(message)
        message.scrollIntoView({ behavior: 'smooth', block: 'end' })
    };
});

function sendMessage(event) {
    event.preventDefault()
    const input = document.getElementById("messageText")
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('WebSocket is not open')
        return
    }
    try {
        ws.send(input.value)
    } catch (e) {
        console.error('WebSocket send failed', e)
    }
    input.value = ''
}