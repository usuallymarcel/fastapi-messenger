let ws;
const API_URL = window.ENV.API_URL

document.addEventListener('DOMContentLoaded', async function() {
    const res = await fetch(API_URL + '/users/username', {
        credentials: "include"
    }).catch(err => {
        console.error("Error: ", err)
    })

    const data = await res.json()
    
    
    document.querySelector("#ws-id").textContent = data.username;

    const protocol = location.protocol === "https:" ? "wss://" : "ws://";
    ws = new WebSocket(protocol + location.host + `/ws`);

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