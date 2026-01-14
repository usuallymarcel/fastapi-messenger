export let ws = null

export function initWebSocket() {
  ws = new WebSocket(
    (location.protocol === "https:" ? "wss://" : "ws://") +
    location.host +
    "/ws/chat"
  )
  return ws
}