let ws
const API_URL = window.ENV.API_URL

ws = new WebSocket(
    (location.protocol === "https:" ? "wss://" : "ws://") +
    location.host +
    "/ws/chat"
)

ws.onmessage = function(event) {
    // const messages = document.getElementById('messages')
    // const message = document.createElement('li')
    // message.textContent = event.data
    // messages.appendChild(message)
    // message.scrollIntoView({ behavior: 'smooth', block: 'end' })
    const data = JSON.parse(event.data)

    switch (data.type) {
        case "friend_request_received":
            showIncomingRequest(data)
            break
        case "friend_request_accepted":
            removeRequestItem(data.request_id)
            addFriend(data)
            break
        case "friend_request_rejected":
            removeRequestItem(data.request_id)
            break
        case "friend_request_sent":
            showSentRequest(data)
            break
        case "load_friend":
            addFriend(data)
            break
        case "message_sent":
            showMessage(data)
            break
        case "message_received":
            showReceivedMessage(data)
            break
        case "Error":
            console.log(data.message)
            break
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    const res = await fetch(API_URL + '/users/user', {
        credentials: "include"
    }).catch(err => {
        console.error("Error: ", err)
    })

    const data = await res.json()
    
    
    document.querySelector("#ws-id").textContent = data.email + ", ID: " + data.id

    showLogoutButton()
})

function sendMessage(event) {
    event.preventDefault()
    
    const input = document.getElementById("messageText");
    const friends = document.getElementsByName('friends');

    let selectedFriendId = null;
    for (const f of friends) {
        if (f.checked) {
            selectedFriendId = f.value;
            break;
        }
    }

    if (!selectedFriendId) {
        alert("Please select a friend to send a message to.");
        return;
    }

    const messageText = input.value.trim();
    if (!messageText) {
        alert("Message cannot be empty.");
        return;
    }

    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('WebSocket is not open');
        return;
    }

    try {
        ws.send(JSON.stringify({
            type: "message",
            to_user_id: selectedFriendId,
            content: messageText
        }));
    } catch (e) {
        console.error('WebSocket send failed', e);
    }

    input.value = '';
}

async function sendFriendRequest() {
    const input = document.getElementById("friend-id-input")
    
    // const res = await fetch(API_URL + '/friends/request', {
    //     credentials: "include",
    //     method: "POST",
    //     headers: {
    //         "Content-Type": "application/json",
    //     },
    //     body: JSON.stringify({ friend_id: input.value })
    // }).catch(err => {
    //     console.error("Error: ", err)
    // })

    // const data = await res.json()

    // console.log(data)
    ws.send(JSON.stringify({"type": "friend_request", "to_user_id": input.value}))
}

function addFriend(data) {
    const friendsDiv = document.getElementById('friends');
    console.log(data)

    const label = document.createElement('label');
    label.classList.add('friend-item');

    const input = document.createElement('input');
    input.type = 'radio';
    input.name = 'friends';          //grouping
    input.value = data.user_id;

    input.addEventListener('change', () => {
        clearMessages();
        console.log("change friend id", input.value);

        ws.send(JSON.stringify({
            type: "get_messages",
            friend_id: input.value
        }));
    });

    const text = document.createTextNode(data.username);

    label.append(input, text);
    friendsDiv.append(label);
}

function showIncomingRequest(data) {
    const requests = document.getElementById('pending-sent-requests')

    const item = document.createElement('li')
    item.classList.add('friend-request', 'friend-request--incoming')


    item.dataset.requestId = data.request_id

    const info = document.createElement('div')
    info.classList.add('friend-request__info')
    info.textContent = `${data.username} (ID: ${data.from_user_id})`

    const actions = document.createElement('div')
    actions.classList.add('friend-request__actions')

    const acceptBtn = document.createElement('button')
    acceptBtn.textContent = 'Accept'
    acceptBtn.classList.add('btn', 'btn--accept')
    acceptBtn.onclick = () => acceptFriendRequest(data.request_id)

    const rejectBtn = document.createElement('button')
    rejectBtn.textContent = 'Reject'
    rejectBtn.classList.add('btn', 'btn--reject')
    rejectBtn.onclick = () => rejectFriendRequest(data.request_id)

    actions.append(acceptBtn, rejectBtn)
    item.append(info, actions)
    requests.append(item)
}


function showSentRequest(data) {
    const requests = document.getElementById('pending-received-requests')
    const request = document.createElement('li')
    request.classList.add('friend-request', 'friend-request--sent')
    request.dataset.requestId = data.request_id
    request.textContent = `Pending ${data.username}, ID: ${data.to_user_id}`
    requests.appendChild(request)
}

function acceptFriendRequest(requestId) {
    ws.send(JSON.stringify({"type": "friend_accept", "request_id": requestId}))
}

function rejectFriendRequest(requestId) {
    ws.send(JSON.stringify({"type": "friend_reject", "request_id": requestId}))
}

const showLogoutButton = () => {
    const logoutDiv = document.getElementById('logout-div')
    const button = document.createElement('button')
    button.addEventListener("click", logout)
    button.textContent = "Logout"
    logoutDiv.append(button)
}

async function logout() {
    const res = await fetch(API_URL + '/users/logout', {
        method: "POST",
        credentials: "include"
    })

    if (!res.ok) return

    const data = await res.json()

    console.log(data)
    window.location.href = "/"
}

function showMessage(data) {
    const messagesDiv = document.getElementById('messages');
    const li = document.createElement('li');
    li.textContent = data.content;
    messagesDiv.appendChild(li);
    li.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function showReceivedMessage(data) {
    const messagesDiv = document.getElementById('messages');

    //only show if this friend is currently selected
    const friends = document.getElementsByName('friends');
    let selectedFriendId = null;
    for (const f of friends) {
        if (f.checked) {
            selectedFriendId = f.value;
            break;
        }
    }

    if (selectedFriendId !== String(data.from)) return;

    const li = document.createElement('li');
    li.textContent = data.content;
    messagesDiv.appendChild(li);
    li.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function clearMessages() {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML = '';
}

function removeRequestItem(requestId) {
    const item = document.querySelector(
        `.friend-request[data-request-id="${requestId}"]`
    )

    if (item) {
        item.remove()
    }
}