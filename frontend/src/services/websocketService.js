import { io } from 'socket.io-client'

class WebSocketService {
  constructor() {
    this.socket = null
    this.isConnected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 1000
    this.listeners = new Map()
  }

  connect() {
    if (this.socket && this.isConnected) {
      console.log('WebSocket already connected')
      return
    }

    console.log('Connecting to WebSocket server...')
    
    this.socket = io('http://localhost:8000', {
      transports: ['websocket', 'polling'],
      upgrade: true,
      rememberUpgrade: true,
      timeout: 20000,
      forceNew: true
    })

    this.setupEventHandlers()
  }

  setupEventHandlers() {
    this.socket.on('connect', () => {
      console.log('Connected to WebSocket server:', this.socket.id)
      this.isConnected = true
      this.reconnectAttempts = 0
      
      // Notify listeners about connection
      this.emit('connection_status', { connected: true, id: this.socket.id })
    })

    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected from WebSocket server:', reason)
      this.isConnected = false
      
      // Notify listeners about disconnection
      this.emit('connection_status', { connected: false, reason })
      
      // Auto-reconnect logic
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, don't reconnect automatically
        console.log('Server disconnected, not attempting to reconnect')
      } else {
        this.handleReconnection()
      }
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.isConnected = false
      this.handleReconnection()
    })

    this.socket.on('connection_established', (data) => {
      console.log('Connection established:', data)
    })

    // Project events
    this.socket.on('project_created', (data) => {
      console.log('Project created:', data)
      this.emit('project_created', data)
    })

    this.socket.on('project_updated', (data) => {
      console.log('Project updated:', data)
      this.emit('project_updated', data)
    })

    this.socket.on('project_deleted', (data) => {
      console.log('Project deleted:', data)
      this.emit('project_deleted', data)
    })

    // Member events
    this.socket.on('member_added', (data) => {
      console.log('Member added:', data)
      this.emit('member_added', data)
    })

    this.socket.on('member_removed', (data) => {
      console.log('Member removed:', data)
      this.emit('member_removed', data)
    })

    // Task events
    this.socket.on('task_created', (data) => {
      console.log('Task created:', data)
      this.emit('task_created', data)
    })

    this.socket.on('task_updated', (data) => {
      console.log('Task updated:', data)
      this.emit('task_updated', data)
    })

    this.socket.on('task_deleted', (data) => {
      console.log('Task deleted:', data)
      this.emit('task_deleted', data)
    })

    // User events
    this.socket.on('user_created', (data) => {
      console.log('User created:', data)
      this.emit('user_created', data)
    })

    this.socket.on('user_deleted', (data) => {
      console.log('User deleted:', data)
      this.emit('user_deleted', data)
    })
  }

  handleReconnection() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached')
      this.emit('connection_status', { 
        connected: false, 
        error: 'Max reconnection attempts reached' 
      })
      return
    }

    this.reconnectAttempts++
    console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      if (!this.isConnected) {
        this.connect()
      }
    }, this.reconnectInterval * this.reconnectAttempts)
  }

  disconnect() {
    if (this.socket) {
      console.log('Disconnecting from WebSocket server...')
      this.socket.disconnect()
      this.socket = null
      this.isConnected = false
      this.listeners.clear()
    }
  }

  // Event listener management
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
      if (callbacks.length === 0) {
        this.listeners.delete(event)
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error)
        }
      })
    }
  }

  // Send message to server (if you need custom events)
  send(event, data) {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data)
    } else {
      console.warn('Cannot send message: WebSocket not connected')
    }
  }

  getConnectionStatus() {
    return {
      connected: this.isConnected,
      id: this.socket?.id || null,
      reconnectAttempts: this.reconnectAttempts
    }
  }
}

// Create singleton instance
const websocketService = new WebSocketService()

export default websocketService
