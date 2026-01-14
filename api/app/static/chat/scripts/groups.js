import { ws } from './ws.js'

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
  if (groupName <= 0) {
    return
  }
  ws.send(JSON.stringify({"type": "group_create", "group_name": groupName}))
}

export function load_group(data) {
  const groupDiv = document.getElementById('group-list')

  const label = document.createElement('label')
  label.classList.add('group-item')

  const input = document.createElement('input')
  input.type = 'radio'
  input.name = 'friends'
  input.value = data.group_id

  const name = document.createElement('span')
  const count = document.createElement('span')
  
  count.classList.add('message-count')
  // count.textContent = data.unread_count
  name.textContent = data.group_name

  input.addEventListener('change', () => {
    ws.send(JSON.stringify({
      type: "group_get_messages", 
      group_id: input.value
    }))
  })

  label.append(input, name, count)
  groupDiv.append(label)
}