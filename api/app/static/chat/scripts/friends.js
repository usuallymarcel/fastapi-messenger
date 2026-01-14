import { ws } from './ws.js'

export function sendMessage(event) {
    event.preventDefault()
    
    const input = document.getElementById("messageText")
    const friends = document.getElementsByName('friends')

    let selectedFriendId = null
    for (const f of friends) {
        if (f.checked) {
            selectedFriendId = f.value
            break
        }
    }

    if (!selectedFriendId) {
        alert("Please select a friend to send a message to.")
        return
    }

    const messageText = input.value.trim()
    if (!messageText) {
        alert("Message cannot be empty.")
        return
    }

    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('WebSocket is not open')
        return
    }

    try {
        ws.send(JSON.stringify({
            type: "message",
            to_user_id: selectedFriendId,
            content: messageText
        }))
    } catch (e) {
        console.error('WebSocket send failed', e)
    }

    input.value = ''
}

export function addFriend(data) {
    const friendsDiv = document.getElementById('friends')

    const label = document.createElement('label')
    label.classList.add('friend-item')

    const input = document.createElement('input')
    input.type = 'radio'
    input.name = 'friends'
    input.value = data.user_id
    
    const name = document.createElement('span')
    const count = document.createElement('span')
    count.classList.add('message-count')
    count.textContent = data.unread_count
    name.textContent = data.username

    input.addEventListener('change', () => {
        clearMessages()
        count.textContent = '' //clear notification
        ws.send(JSON.stringify({
            type: "get_messages",
            friend_id: input.value
        }))
    })

    label.append(input, name, count)
    friendsDiv.append(label)
}

export function showIncomingRequest(data) {
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


export function showSentRequest(data) {
    const requests = document.getElementById('pending-received-requests')
    const request = document.createElement('li')
    request.classList.add('friend-request', 'friend-request--sent')
    request.dataset.requestId = data.request_id
    request.textContent = `Pending ${data.username}, ID: ${data.to_user_id}`
    requests.appendChild(request)
}

export function acceptFriendRequest(requestId) {
    ws.send(JSON.stringify({"type": "friend_accept", "request_id": requestId}))
}

export function rejectFriendRequest(requestId) {
    ws.send(JSON.stringify({"type": "friend_reject", "request_id": requestId}))
}

export function showMessage(data) {
    const messagesDiv = document.getElementById('messages')
    const li = document.createElement('li')
    li.textContent = data.content
    messagesDiv.appendChild(li)
    li.scrollIntoView({ behavior: 'smooth', block: 'end' })
}

export function showReceivedMessage(data) {
    const messagesDiv = document.getElementById('messages')

    //only show if this friend is currently selected
    const friends = document.getElementsByName('friends')
    let selectedFriendId = null

    for (const f of friends) {
        if (f.checked) {
            selectedFriendId = f.value
            break
        }
    }

    if (selectedFriendId !== String(data.from)) {
        const input = [...friends].find(f => f.value === String(data.from))
        if (input) {
            const label = input.parentElement
            const count = label.querySelector('.message-count')
            const current = parseInt(count.textContent || '0', 10)
            count.textContent = current + 1
        }
        return
    }
    ws.send(JSON.stringify({"type": "message_read", "message_id": data.message_id}))
    const li = document.createElement('li')
    li.textContent = data.content
    messagesDiv.appendChild(li)
    li.scrollIntoView({ behavior: 'smooth', block: 'end' })
}

export function clearMessages() {
    const messagesDiv = document.getElementById('messages')
    messagesDiv.innerHTML = ''
}

export function removeRequestItem(requestId) {
    const item = document.querySelector(
        `.friend-request[data-request-id="${requestId}"]`
    )

    if (item) {
        item.remove()
    }
}

export async function sendFriendRequest() {
    const input = document.getElementById("friend-id-input")
    
    ws.send(JSON.stringify({"type": "friend_request", "to_user_id": input.value}))
}
