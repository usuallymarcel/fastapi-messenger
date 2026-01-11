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