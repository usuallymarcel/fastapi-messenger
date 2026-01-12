function toggleGroup() {
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

function createGroup() {
  const groupName = document.getElementById('group-name-input').value.trim()
  if (groupName <= 0) {
    return
  }
  ws.send(JSON.stringify({"type": "group_create", "group_name": groupName}))
}