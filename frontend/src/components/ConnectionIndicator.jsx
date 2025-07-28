/*******************************************************************************
 * ConnectionIndicator.jsx
 * Purpose: Displays a visual indicator of WebSocket connection status, showing
 *          "Live" when connected and "Connecting..." when disconnected,
 *          using styles defined in ConnectionIndicator.css.
 ******************************************************************************/

import { useWebSocket } from '../hooks/useWebSocket'
import './ConnectionIndicator.css'

function ConnectionIndicator() {
  const { connectionStatus } = useWebSocket()

  // Show connected state UI
  if (connectionStatus.connected) {
    return (
      <div className="connection-indicator connected"
            title="Connected to real-time updates">
        <div className="status-dot"></div>
        <span>Live</span>
      </div>
    )
  }

  // Show disconnected/reconnecting state UI
  return (
    <div className="connection-indicator disconnected"
            title="Reconnecting to real-time updates...">
      <div className="status-dot"></div>
      <span>Connecting...</span>
    </div>
  )
}

export default ConnectionIndicator
