// src/components/ConnectionIndicator.jsx
import { useWebSocket } from '../hooks/useWebSocket'
import './ConnectionIndicator.css'

function ConnectionIndicator() {
  const { connectionStatus } = useWebSocket()

  if (connectionStatus.connected) {
    return (
      <div className="connection-indicator connected" title="Connected to real-time updates">
        <div className="status-dot"></div>
        <span>Live</span>
      </div>
    )
  }

  return (
    <div className="connection-indicator disconnected" title="Reconnecting to real-time updates...">
      <div className="status-dot"></div>
      <span>Connecting...</span>
    </div>
  )
}

export default ConnectionIndicator
