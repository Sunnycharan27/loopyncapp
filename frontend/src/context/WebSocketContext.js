import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { io } from 'socket.io-client';
import { toast } from 'sonner';

const WebSocketContext = createContext(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    console.warn('useWebSocket called outside WebSocketProvider');
    return { connected: false, socket: null };
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState(new Set());

  useEffect(() => {
    const token = localStorage.getItem('loopync_token');
    
    if (!token) {
      console.log('No token found, skipping WebSocket connection');
      return;
    }

    // Connect to WebSocket server
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    
    const newSocket = io(BACKEND_URL, {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
      path: '/socket.io/'
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

    // Friend request notifications
    newSocket.on('friend_request', (data) => {
      console.log('📬 New friend request:', data);
      toast.info(`${data.from_user?.name} sent you a friend request`);
    });

    // Friend events
    newSocket.on('friend_event', (data) => {
      console.log('👥 Friend event:', data);
      
      if (data.type === 'accepted') {
        toast.success('Friend request accepted!');
      } else if (data.type === 'removed') {
        toast.info('A friend was removed');
      }
    });

    // Message events
    newSocket.on('message', (data) => {
      console.log('💬 New message:', data);
      // This will be handled by individual components
    });

    // Typing indicators
    newSocket.on('typing', (data) => {
      console.log('⌨️ Typing:', data);
      // This will be handled by Messenger component
    });

    // Read receipts
    newSocket.on('message_read', (data) => {
      console.log('✓✓ Message read:', data);
      // This will be handled by Messenger component
    });

    // Call events
    newSocket.on('call_incoming', (data) => {
      console.log('📞 Incoming call:', data);
      // This will be handled by components that have call handling
    });

    newSocket.on('call_initiated', (data) => {
      console.log('📞 Call initiated:', data);
    });

    newSocket.on('call_answered', (data) => {
      console.log('📞 Call answered:', data);
    });

    newSocket.on('call_rejected', (data) => {
      console.log('📞 Call rejected:', data);
    });

    newSocket.on('call_ended', (data) => {
      console.log('📞 Call ended:', data);
    });

    // WebRTC signaling events
    newSocket.on('webrtc_offer', (data) => {
      console.log('🔄 WebRTC offer:', data);
    });

    newSocket.on('webrtc_answer', (data) => {
      console.log('🔄 WebRTC answer:', data);
    });

    newSocket.on('webrtc_ice_candidate', (data) => {
      console.log('🔄 ICE candidate:', data);
    });

    setSocket(newSocket);

    // Cleanup
    return () => {
      console.log('Cleaning up WebSocket connection');
      newSocket.close();
    };
  }, []);

  // Helper function to emit typing indicator
  const emitTyping = useCallback((threadId, isTyping = true) => {
    if (socket && connected) {
      socket.emit('typing', { threadId, isTyping });
    }
  }, [socket, connected]);

  // Helper function to emit message read
  const emitMessageRead = useCallback((messageId, threadId) => {
    if (socket && connected) {
      socket.emit('message_read', { messageId, threadId });
    }
  }, [socket, connected]);

  // Helper function to join a thread
  const joinThread = useCallback((threadId) => {
    if (socket && connected) {
      socket.emit('join_thread', { threadId });
    }
  }, [socket, connected]);

  // Helper function to leave a thread
  const leaveThread = useCallback((threadId) => {
    if (socket && connected) {
      socket.emit('leave_thread', { threadId });
    }
  }, [socket, connected]);

  // Calling helpers
  const initiateCall = useCallback((threadId, isVideo = false) => {
    if (socket && connected) {
      socket.emit('call_initiate', { threadId, isVideo });
    }
  }, [socket, connected]);

  const answerCall = useCallback((callId) => {
    if (socket && connected) {
      socket.emit('call_answer', { callId });
    }
  }, [socket, connected]);

  const rejectCall = useCallback((callId) => {
    if (socket && connected) {
      socket.emit('call_reject', { callId });
    }
  }, [socket, connected]);

  const endCall = useCallback((callId) => {
    if (socket && connected) {
      socket.emit('call_end', { callId });
    }
  }, [socket, connected]);

  const value = {
    socket,
    connected,
    onlineUsers,
    emitTyping,
    emitMessageRead,
    joinThread,
    leaveThread,
    initiateCall,
    answerCall,
    rejectCall,
    endCall
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export default WebSocketContext;
