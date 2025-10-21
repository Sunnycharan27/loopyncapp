import React, { createContext, useContext, useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const WebSocketContext = createContext(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [friendRequests, setFriendRequests] = useState([]);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('loopync_token');
    
    if (!token) {
      console.log('No token found, skipping WebSocket connection');
      return;
    }

    // Connect to WebSocket server
    const BACKEND_URL = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;
    if (!BACKEND_URL) {
      console.warn('REACT_APP_BACKEND_URL is not set. Skipping WebSocket connection.');
      return;
    }
    const newSocket = io(BACKEND_URL, {
      auth: token ? { token } : undefined,
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    newSocket.on('connect', () => {
      console.log('✅ WebSocket connected');
      setConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('❌ WebSocket disconnected');
      setConnected(false);
    });

    newSocket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
    });

    // Listen for friend requests
    newSocket.on('friend_request', (data) => {
      console.log('📬 New friend request:', data);
      setFriendRequests(prev => [data, ...prev]);
      
      // Show toast notification
      if (window.Notification && Notification.permission === 'granted') {
        new Notification('New Friend Request', {
          body: `${data.from_user?.name} sent you a friend request`,
          icon: data.from_user?.avatar
        });
      }
    });

    // Listen for friend events
    newSocket.on('friend_event', (data) => {
      console.log('👥 Friend event:', data);
      
      if (data.type === 'accepted') {
        if (window.Notification && Notification.permission === 'granted') {
          new Notification('Friend Request Accepted', {
            body: `${data.peer?.name} accepted your friend request`,
            icon: data.peer?.avatar
          });
        }
      }
    });

    // Listen for messages
    newSocket.on('message', (data) => {
      console.log('💬 New message:', data);
      setMessages(prev => [...prev, data.message]);
      
      // Show notification
      if (window.Notification && Notification.permission === 'granted') {
        const sender = data.message?.sender;
        new Notification(`Message from ${sender?.name}`, {
          body: data.message?.text || 'Sent a photo',
          icon: sender?.avatar
        });
      }
    });

    // Listen for typing indicators
    newSocket.on('typing', (data) => {
      console.log('⌨️ User typing:', data);
    });

    // Listen for read receipts
    newSocket.on('read', (data) => {
      console.log('✓✓ Message read:', data);
    });

    setSocket(newSocket);

    // Request notification permission
    if (window.Notification && Notification.permission === 'default') {
      Notification.requestPermission();
    }

    // Cleanup on unmount
    return () => {
      newSocket.close();
    };
  }, []);

  const emitTyping = (threadId) => {
    if (socket && connected) {
      socket.emit('typing', { threadId });
    }
  };

  const value = {
    socket,
    connected,
    friendRequests,
    messages,
    emitTyping,
    clearFriendRequests: () => setFriendRequests([]),
    clearMessages: () => setMessages([])
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export default WebSocketContext;
