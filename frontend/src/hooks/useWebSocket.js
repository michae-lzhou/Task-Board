/*******************************************************************************
 * useWebSocket.js
 * Purpose: Provides a reusable React hook to manage WebSocket connection state,
 *          event subscriptions, and sending messages; includes specialized
 *          hooks for handling real-time updates on projects, tasks, and
 *          members.
 ******************************************************************************/

import { useEffect, useState, useCallback } from 'react'
import websocketService from '../services/websocketService'

export const useWebSocket = () => {
  // Track connection status, client ID, and reconnect attempts
  const [connectionStatus, setConnectionStatus] = useState({
    connected: false,
    id: null,
    reconnectAttempts: 0
  })

  useEffect(() => {
    // Connect to WebSocket when hook initializes
    websocketService.connect()

    // Update connection status on status events
    const handleConnectionStatus = (status) => {
      setConnectionStatus(status)
    }
    websocketService.on('connection_status', handleConnectionStatus)

    // Cleanup event listener on unmount
    return () => {
      websocketService.off('connection_status', handleConnectionStatus)
      // Note: Do not disconnect socket here to allow persistence across
      // components
    }
  }, [])

  // Subscribe to a specific event with a callback; returns unsubscribe function
  const subscribe = useCallback((event, callback) => {
    websocketService.on(event, callback)
    return () => websocketService.off(event, callback)
  }, [])

  // Send event and data via WebSocket
  const send = useCallback((event, data) => {
    websocketService.send(event, data)
  }, [])

  return {
    connectionStatus,
    subscribe,
    send,
    isConnected: connectionStatus.connected
  }
}

// Specialized hook: listen to project-related WebSocket events and trigger
// callback
export const useWebSocketProjects = (onProjectsChange) => {
  const { subscribe } = useWebSocket()

  useEffect(() => {
    const unsubscribeCreated = subscribe('project_created', (data) => {
      console.log('Project created event received:', data)
      if (onProjectsChange) onProjectsChange('created', data.data)
    })
    const unsubscribeUpdated = subscribe('project_updated', (data) => {
      console.log('Project updated event received:', data)
      if (onProjectsChange) onProjectsChange('updated', data.data)
    })
    const unsubscribeDeleted = subscribe('project_deleted', (data) => {
      console.log('Project deleted event received:', data)
      if (onProjectsChange) onProjectsChange('deleted', data.data)
    })

    // Cleanup all subscriptions on unmount
    return () => {
      unsubscribeCreated()
      unsubscribeUpdated()
      unsubscribeDeleted()
    }
  }, [subscribe, onProjectsChange])
}

// Specialized hook: listen to task-related WebSocket events and trigger
// callback
export const useWebSocketTasks = (onTasksChange) => {
  const { subscribe } = useWebSocket()

  useEffect(() => {
    const unsubscribeCreated = subscribe('task_created', (data) => {
      console.log('Task created event received:', data)
      if (onTasksChange) onTasksChange('created', data.data)
    })
    const unsubscribeUpdated = subscribe('task_updated', (data) => {
      console.log('Task updated event received:', data)
      if (onTasksChange) onTasksChange('updated', data.data)
    })
    const unsubscribeDeleted = subscribe('task_deleted', (data) => {
      console.log('Task deleted event received:', data)
      if (onTasksChange) onTasksChange('deleted', data.data)
    })

    return () => {
      unsubscribeCreated()
      unsubscribeUpdated()
      unsubscribeDeleted()
    }
  }, [subscribe, onTasksChange])
}

// Specialized hook: listen to member- and user-related WebSocket events and
// trigger callback
export const useWebSocketMembers = (onMembersChange) => {
  const { subscribe } = useWebSocket()

  useEffect(() => {
    const unsubscribeAdded = subscribe('member_added', (data) => {
      console.log('Member added event received:', data)
      if (onMembersChange) onMembersChange('added', data.data)
    })
    const unsubscribeRemoved = subscribe('member_removed', (data) => {
      console.log('Member removed event received:', data)
      if (onMembersChange) onMembersChange('removed', data.data)
    })
    const unsubscribeUserCreated = subscribe('user_created', (data) => {
      console.log('User created event received:', data)
      if (onMembersChange) onMembersChange('user_created', data.data)
    })
    const unsubscribeUserDeleted = subscribe('user_deleted', (data) => {
      console.log('User deleted event received:', data)
      if (onMembersChange) onMembersChange('user_deleted', data.data)
    })

    return () => {
      unsubscribeAdded()
      unsubscribeRemoved()
      unsubscribeUserCreated()
      unsubscribeUserDeleted()
    }
  }, [subscribe, onMembersChange])
}
