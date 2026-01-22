import { 
    showIncomingRequest, 
    addFriend, 
    showSentRequest, 
    showMessage, 
    showReceivedMessage, 
    removeRequestItem,
    sendFriendRequest,
    sendMessage
} from "./scripts/friends.js"

import {
    loadGroup,
    toggleGroup,
    createGroup,
    sendGroupMessage,
    showReceivedGroupMessage,
    createGroupInvite
} from "./scripts/groups.js"

import { ws, initWebSocket } from "./scripts/ws.js"

const API_URL = window.ENV.API_URL

initWebSocket()

ws.onmessage = function(event) {
    const data = JSON.parse(event.data)

    console.log(data)

    if (data.type.toLowerCase().includes('group')) {
        switch (data.type) {
            case "load_group":
                loadGroup(data)
                break
            case "group_message_received":
                showReceivedGroupMessage(data)
                break
        }
        return
    }
        

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

    document
        .getElementById("group-toggle-button")
        .addEventListener("click", toggleGroup)

    document
        .getElementById("send-friend-request-btn")
        .addEventListener("click", sendFriendRequest)

    document
        .getElementById("create-group-btn")
        .addEventListener("click", createGroup)
    
    document
        .getElementById('messageText')
        .addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault()
                sendMessage()
            }
        })

    document
        .getElementById("send-message-button")
        .addEventListener("click", sendMessage)

    document
        .getElementById('group-messages-text')
        .addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault()
                sendGroupMessage()
            }
        })

    document
        .getElementById("group-message-send-button")
        .addEventListener("click", sendGroupMessage)

    document
        .getElementById("create-invite-link")
        .addEventListener("click", createGroupInvite)

    
})

function showLogoutButton() {
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

    window.location.href = "/"
}

