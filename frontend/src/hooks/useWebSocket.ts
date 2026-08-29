import { useState, useEffect, useRef, useCallback } from 'react';

export interface WebSocketMessage {
  type: string;
  payload?: any;
  [key: string]: any;
}

export function useWebSocket(url?: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const wsUrl = url || (typeof window !== 'undefined' ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws` : 'ws://localhost:8000/ws');

  const connect = useCallback(() => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('callsphere_token') : null;
      const fullUrl = token ? `${wsUrl}?token=${encodeURIComponent(token)}` : wsUrl;
      const ws = new WebSocket(fullUrl);

      ws.onopen = () => {
        setIsConnected(true);
        if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setLastMessage(parsed);
        } catch (e) {
          setLastMessage({ type: 'RAW', payload: event.data });
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };

      socketRef.current = ws;
    } catch (err) {
      setIsConnected(false);
    }
  }, [wsUrl]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, [connect]);

  const sendMessage = useCallback((msg: WebSocketMessage) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(msg));
    }
  }, []);

  return { isConnected, lastMessage, sendMessage };
}
