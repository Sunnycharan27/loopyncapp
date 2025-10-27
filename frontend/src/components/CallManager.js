import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import IncomingCallModal from './IncomingCallModal';
import AgoraCallModal from './AgoraCallModal';
import { toast } from 'sonner';

const CallManager = ({ currentUser }) => {
  const [incomingCall, setIncomingCall] = useState(null);
  const [activeCall, setActiveCall] = useState(null);
  const { socket } = useWebSocket();

  useEffect(() => {
    if (!socket || !currentUser) return;

    // Listen for incoming call events
    socket.on('incoming_call', (data) => {
      console.log('Incoming call received:', data);
      setIncomingCall(data);
      toast.info(`Incoming ${data.callType} call from ${data.callerName}`);
    });

    return () => {
      socket.off('incoming_call');
    };
  }, [socket, currentUser]);

  const handleAcceptCall = () => {
    if (!incomingCall) return;

    // Join the call with recipient token
    const callData = {
      callId: incomingCall.callId,
      channelName: incomingCall.channelName,
      appId: incomingCall.appId,
      callerToken: incomingCall.token, // Use recipient token
      callerUid: incomingCall.uid, // Use recipient UID
      callType: incomingCall.callType,
      peerName: incomingCall.callerName,
      isInitiator: false
    };

    setActiveCall(callData);
    setIncomingCall(null);
  };

  const handleRejectCall = () => {
    toast.info('Call declined');
    setIncomingCall(null);
  };

  const handleCloseCall = () => {
    setActiveCall(null);
  };

  return (
    <>
      {incomingCall && (
        <IncomingCallModal
          callData={incomingCall}
          onAccept={handleAcceptCall}
          onReject={handleRejectCall}
        />
      )}

      {activeCall && (
        <AgoraCallModal
          callData={activeCall}
          currentUserId={currentUser?.id}
          onClose={handleCloseCall}
          isIncoming={!activeCall.isInitiator}
        />
      )}
    </>
  );
};

export default CallManager;
