import { ws } from './ws.js'

const API_URL = window.ENV.API_URL

export function toggleGroup() {
  const groupDiv = document.getElementById('groups-div')
  const friendDiv = document.getElementById('friends-div')
  const groupButton = document.getElementById('group-toggle-button')

  friendDiv.hidden = !friendDiv.hidden
  groupDiv.hidden = !groupDiv.hidden
  if (!groupDiv.hasAttribute('hidden')) {
    groupButton.textContent = 'Close Groups'
  }
  else {
    groupButton.textContent = 'Open Groups'
  }
}

export function createGroup() {
  const groupName = document.getElementById('group-name-input').value.trim()
  if (groupName.length === 0) {
    return
  }
  ws.send(JSON.stringify({"type": "group_create", "group_name": groupName}))
}

export function clearMessages() {
    const groupMessageDiv = document.getElementById('group-messages')
    groupMessageDiv.innerHTML = ''
}

export function loadGroup(data) {
  const groupDiv = document.getElementById('group-list')

  const label = document.createElement('label')
  label.classList.add('group-item')

  const input = document.createElement('input')
  input.type = 'radio'
  input.name = 'groups'
  input.value = data.group_id

  const name = document.createElement('span')
  const count = document.createElement('span')
  
  count.classList.add('message-count')
  // count.textContent = data.unread_count
  name.textContent = data.group_name
  input.addEventListener('change', () => {
    clearMessages()
    ws.send(JSON.stringify({
      type: "group_get_messages", 
      group_id: input.value
    }))
  })

  label.append(input, name, count)
  groupDiv.append(label)
}

function getSelectedGroupId() {
  const selected = document.querySelector('#group-list input[type="radio"]:checked')
  return selected ? selected.value : null
}

export function sendGroupMessage() {
  const input = document.getElementById('group-messages-text')
  const message = input.value.trim()
  const groupId = getSelectedGroupId()

  if (!groupId || message.length === 0) {
    return
  }

  ws.send(JSON.stringify({
    type: "group_message",
    group_id: groupId,
    group_message: message
  }))

  input.value = ''
}

export function showReceivedGroupMessage(data) {
  const groupMessagesDiv = document.getElementById('group-messages')

  const groups = document.getElementsByName('groups')

  let selectedGroupId = null

  for (const g of groups) {
    if (g.checked) {
      selectedGroupId = g.value
      break
    }
  }

  if (selectedGroupId !== String(data.from)) {
    return
  }

  const li = document.createElement('li')
  li.textContent = data.content
  groupMessagesDiv.appendChild(li)
  li.scrollIntoView({ behavior: 'smooth', block: 'end' })
}

export async function createGroupInvite() {
  const groupId = getSelectedGroupId()

  if (!groupId) return

  const res = await fetch(API_URL + `/groups/${groupId}/invite`, {
      method: "POST",
      credentials: "include",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify({ max_uses : 5 })
  }).catch(err => {
      console.error("Error: ", err)
  })

  const inviteLink = await res.json()

  if (!inviteLink) {
    console.error('No invite link created')
  }

  const groupInviteElement = document.getElementById('invite-link')

  groupInviteElement.textContent = inviteLink.invite_link
}