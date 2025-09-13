import { io, Socket } from 'socket.io-client'
import { GraphData, Deal, Company } from '@/types'

export interface WebSocketEvents {
  'graph-update': (data: GraphData) => void
  'node-added': (node: Company) => void
  'node-removed': (nodeId: string) => void
  'edge-added': (edge: Deal) => void
  'edge-removed': (edgeId: string) => void
  'prediction-update': (predictions: Deal[]) => void
  'simulation-result': (result: any) => void
  'error': (error: string) => void
  'connected': () => void
  'disconnected': () => void
}

class WebSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private eventListeners: Map<string, Function[]> = new Map()
  private mockMode = false // Disable mock mode to use real backend

  constructor() {
    this.connect()
  }

  private connect() {
    const wsUrl = process.env.NODE_ENV === 'production' 
      ? 'https://your-backend-url.com' 
      : 'http://localhost:8000'

    try {
      this.socket = io(wsUrl, {
        transports: ['websocket', 'polling'],
        timeout: 20000,
        forceNew: true,
        autoConnect: true
      })

      this.setupEventHandlers()
    } catch (error) {
      console.warn('WebSocket connection failed, running in offline mode')
      this.mockMode = true
      setTimeout(() => {
        this.emit('disconnected')
      }, 2000)
    }
  }

  private setupEventHandlers() {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.emit('connected')
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.emit('disconnected')
      
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, reconnect manually
        this.reconnect()
      }
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.emit('error', error.message)
      this.reconnect()
    })

    // Graph data updates
    this.socket.on('graph_data_updated', (data: GraphData) => {
      console.log('Received graph data update')
      this.emit('graph-update', data)
    })

    // Node operations
    this.socket.on('node_added', (node: Company) => {
      console.log('Node added:', node.name)
      this.emit('node-added', node)
    })

    this.socket.on('node_removed', (nodeId: string) => {
      console.log('Node removed:', nodeId)
      this.emit('node-removed', nodeId)
    })

    // Edge operations
    this.socket.on('edge_added', (edge: Deal) => {
      console.log('Edge added:', edge.id)
      this.emit('edge-added', edge)
    })

    this.socket.on('edge_removed', (edgeId: string) => {
      console.log('Edge removed:', edgeId)
      this.emit('edge-removed', edgeId)
    })

    // Predictions
    this.socket.on('predictions_updated', (predictions: Deal[]) => {
      console.log('Predictions updated:', predictions.length)
      this.emit('prediction-update', predictions)
    })

    // Simulation results
    this.socket.on('simulation_complete', (result: any) => {
      console.log('Simulation completed')
      this.emit('simulation-result', result)
    })

    // Data ingestion updates
    this.socket.on('data_ingestion_progress', (progress: any) => {
      console.log('Data ingestion progress:', progress)
      this.emit('ingestion-progress', progress)
    })

    this.socket.on('data_ingestion_complete', (summary: any) => {
      console.log('Data ingestion complete:', summary)
      this.emit('ingestion-complete', summary)
    })
  }

  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      this.emit('error', 'Failed to reconnect after maximum attempts')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`)
    
    setTimeout(() => {
      this.connect()
    }, delay)
  }

  // Event subscription methods
  on<K extends keyof WebSocketEvents>(event: K, callback: WebSocketEvents[K]) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event)!.push(callback)
  }

  off<K extends keyof WebSocketEvents>(event: K, callback: WebSocketEvents[K]) {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  private emit(event: string, ...args: any[]) {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(...args)
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error)
        }
      })
    }
  }

  // Send messages to server
  emit_to_server(event: string, data?: any) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('WebSocket not connected, cannot send message:', event)
    }
  }

  // Connection status
  isConnected(): boolean {
    if (this.mockMode) return true
    return this.socket?.connected || false
  }

  // Disconnect
  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  // Join/leave rooms for targeted updates
  joinRoom(room: string) {
    this.emit_to_server('join_room', { room })
  }

  leaveRoom(room: string) {
    this.emit_to_server('leave_room', { room })
  }

  // Request specific data updates
  requestGraphUpdate() {
    this.emit_to_server('request_graph_update')
  }

  requestPredictionUpdate(companies: string[]) {
    this.emit_to_server('request_prediction_update', { companies })
  }

  // Simulation requests
  startSimulation(params: any) {
    this.emit_to_server('start_simulation', params)
  }

  // Data ingestion requests
  startDataIngestion(params: any) {
    this.emit_to_server('start_data_ingestion', params)
  }
}

// Create singleton instance
export const websocketService = new WebSocketService()

// React hook for using WebSocket in components
export const useWebSocket = () => {
  return {
    socket: websocketService,
    isConnected: websocketService.isConnected(),
    on: websocketService.on.bind(websocketService),
    off: websocketService.off.bind(websocketService),
    emit: websocketService.emit_to_server.bind(websocketService)
  }
}
