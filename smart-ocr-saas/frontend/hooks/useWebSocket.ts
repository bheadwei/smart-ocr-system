'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useAuthStore } from '@/stores/authStore'

const WS_URL = process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000'

interface ProgressMessage {
  type: string
  task_id: string
  progress: number
  status: string
  timestamp: string
}

export function useOCRProgress(taskId: string | null) {
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'failed'>('idle')
  const wsRef = useRef<WebSocket | null>(null)
  const { token } = useAuthStore()

  const connect = useCallback(() => {
    if (!taskId || !token) return

    const ws = new WebSocket(`${WS_URL}/api/v1/ws/ocr-progress?task_id=${taskId}`)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const data: ProgressMessage = JSON.parse(event.data)
        if (data.type === 'progress' && data.task_id === taskId) {
          setProgress(data.progress)
          setStatus(data.status as any)
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      console.log('WebSocket closed')
      // Attempt to reconnect after delay if not completed/failed
      if (status !== 'completed' && status !== 'failed') {
        setTimeout(() => {
          if (wsRef.current === ws) {
            connect()
          }
        }, 3000)
      }
    }

    wsRef.current = ws
  }, [taskId, token, status])

  useEffect(() => {
    if (taskId) {
      connect()
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [taskId, connect])

  // Keep alive with ping
  useEffect(() => {
    if (!wsRef.current) return

    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping')
      }
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  return { progress, status }
}
