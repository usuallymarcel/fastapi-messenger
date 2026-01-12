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
  const groupName = document.getElementById('group-name-input')
  if (groupName.value.trim() <= 0) {
    console.log('no group name')
    return
  }
  console.log(groupName.value.trim())
  ws.send(JSON.stringify({"type": "group_create", "group_name": groupName.textContent}))
}