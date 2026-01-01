let ws;
const API_URL = window.ENV.API_URL

document.addEventListener('DOMContentLoaded', async function() {
    const res = await fetch(API_URL + '/users/user', {
        credentials: "include"
    }).catch(err => {
        console.error("Error: ", err)
    })

    const data = await res.json()
    
    
    document.querySelector("#ws-id").textContent = data.email + ", ID: " + data.id;

    const protocol = location.protocol === "https:" ? "wss://" : "ws://";
    ws = new WebSocket(protocol + location.host + `/ws/chat`);

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

async function sendFriendRequest() {
    const input = document.getElementById("friend-id-input")
    
    const res = await fetch(API_URL + '/friends/request', {
        credentials: "include",
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ friend_id: input.value })
    }).catch(err => {
        console.error("Error: ", err)
    })

    const data = await res.json()

    console.log(data)
}