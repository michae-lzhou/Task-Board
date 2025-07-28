// src/hooks/useWebSocket.js
import { useEffect, useState, useCallback } from 'react'
import websocketService from '../services/websocketService'

export const useWebSocket = () => {
  const [connectionStatus, setConnectionStatus] = useState({
    connected: false,
    id: null,
    reconnectAttempts: 0
  })

  useEffect(() => {
    // Connect when hook is first used
    websocketService.connect()

    // Listen for connection status changes
    const handleConnectionStatus = (status) => {
      setConnectionStatus(status)
    }

    websocketService.on('connection_status', handleConnectionStatus)

    // Cleanup on unmount
    return () => {
      websocketService.off('connection_status', handleConnectionStatus)
      // Don't disconnect here - let the service persist across components
    }
  }, [])

  const subscribe = useCallback((event, callback) => {
    websocketService.on(event, callback)
    
    // Return unsubscribe function
    return () => {
      websocketService.off(event, callback)
    }
  }, [])

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

// Specialized hooks for different data types
export const useWebSocketProjects = (onProjectsChange) => {
  const { subscribe } = useWebSocket()

  useEffect(() => {
    const unsubscribeCreated = subscribe('project_created', (data) => {
      console.log('Project created event received:', data)
      if (onProjectsChange) {
        onProjectsChange('created', data.data)
      }
    })

    const unsubscribeUpdated = subscribe('project_updated', (data) => {
      console.log('Project updated event received:', data)
      if (onProjectsChange) {
        onProjectsChange('updated', data.data)
      }
    })

    const unsubscribeDeleted = subscribe('project_deleted', (data) => {
      console.log('Project deleted event received:', data)
      if (onProjectsChange) {
        onProjectsChange('deleted', data.data)
      }
    })

    return () => {
      unsubscribeCreated()
      unsubscribeUpdated()
      unsubscribeDeleted()
    }
  }, [subscribe, onProjectsChange])
}

export const useWebSocketTasks = (onTasksChange) => {
  const { subscribe } = useWebSocket()

  useEffect(() => {
    const unsubscribeCreated = subscribe('task_created', (data) => {
      console.log('Task created event received:', data)
      if (onTasksChange) {
        onTasksChange('created', data.data)
      }
    })

    const unsubscribeUpdated = subscribe('task_updated', (data) => {
      console.log('Task updated event received:', data)
      if (onTasksChange) {
        onTasksChange('updated', data.data)
      }
    })

    const unsubscribeDeleted = subscribe('task_deleted', (data) => {
      console.log('Task deleted event received:', data)
      if (onTasksChange) {
        onTasksChange('deleted', data.data)
      }
    })

    return () => {
      unsubscribeCreated()
      unsubscribeUpdated()
      unsubscribeDeleted()
    }
  }, [subscribe, onTasksChange])
}

export const useWebSocketMembers = (onMembersChange) => {
  const { subscribe } = useWebSocket()

  useEffect(() => {
    const unsubscribeAdded = subscribe('member_added', (data) => {
      console.log('Member added event received:', data)
      if (onMembersChange) {
        onMembersChange('added', data.data)
      }
    })

    const unsubscribeRemoved = subscribe('member_removed', (data) => {
      console.log('Member removed event received:', data)
      if (onMembersChange) {
        onMembersChange('removed', data.data)
      }
    })

    const unsubscribeUserCreated = subscribe('user_created', (data) => {
      console.log('User created event received:', data)
      if (onMembersChange) {
        onMembersChange('user_created', data.data)
      }
    })

    const unsubscribeUserDeleted = subscribe('user_deleted', (data) => {
      console.log('User deleted event received:', data)
      if (onMembersChange) {
        onMembersChange('user_deleted', data.data)
      }
    })

    return () => {
      unsubscribeAdded()
      unsubscribeRemoved()
      unsubscribeUserCreated()
      unsubscribeUserDeleted()
    }
  }, [subscribe, onMembersChange])
}
