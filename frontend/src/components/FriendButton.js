import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { UserPlus, UserCheck, UserX, Clock } from 'lucide-react';
import { toast } from 'sonner';

const FriendButton = ({ currentUser, targetUser }) => {
  const [status, setStatus] = useState('none'); // none, friends, request_sent, request_received
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFriendStatus();
  }, [currentUser?.id, targetUser?.id]);

  const fetchFriendStatus = async () => {
    if (!currentUser || !targetUser || currentUser.id === targetUser.id) {
      setLoading(false);
      return;
    }

    try {
      const res = await axios.get(`${API}/users/${currentUser.id}/friend-status/${targetUser.id}`);
      setStatus(res.data.status);
    } catch (error) {
      console.error('Failed to fetch friend status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendRequest = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/friends/request?fromUserId=${currentUser.id}&toUserId=${targetUser.id}`);
      toast.success('Friend request sent!');
      setStatus('request_sent');
    } catch (error) {
      toast.error('Failed to send friend request');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRequest = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/friends/accept?userId=${currentUser.id}&friendId=${targetUser.id}`);
      toast.success(`You are now friends with ${targetUser.name}!`);
      setStatus('friends');
    } catch (error) {
      toast.error('Failed to accept friend request');
    } finally {
      setLoading(false);
    }
  };

  const handleRejectRequest = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/friends/reject?userId=${currentUser.id}&friendId=${targetUser.id}`);
      toast.success('Friend request rejected');
      setStatus('none');
    } catch (error) {
      toast.error('Failed to reject friend request');
    } finally {
      setLoading(false);
    }
  };

  const handleUnfriend = async () => {
    if (!confirm(`Remove ${targetUser.name} from friends?`)) return;
    
    setLoading(true);
    try {
      await axios.delete(`${API}/friends/remove?userId=${currentUser.id}&friendId=${targetUser.id}`);
      toast.success('Friend removed');
      setStatus('none');
    } catch (error) {
      toast.error('Failed to remove friend');
    } finally {
      setLoading(false);
    }
  };

  // Don't show button for own profile
  if (!currentUser || !targetUser || currentUser.id === targetUser.id) {
    return null;
  }

  if (loading && status === 'none') {
    return (
      <button className="px-4 py-2 rounded-full bg-gray-700 text-gray-400" disabled>
        Loading...
      </button>
    );
  }

  switch (status) {
    case 'friends':
      return (
        <button
          onClick={handleUnfriend}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-700 text-white hover:bg-red-500/20 hover:text-red-400 transition disabled:opacity-50"
        >
          <UserCheck size={18} />
          Friends
        </button>
      );
    
    case 'request_sent':
      return (
        <button
          disabled
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-700 text-gray-400"
        >
          <Clock size={18} />
          Request Sent
        </button>
      );
    
    case 'request_received':
      return (
        <div className="flex gap-2">
          <button
            onClick={handleAcceptRequest}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-green-500 text-white hover:bg-green-600 transition disabled:opacity-50"
          >
            <UserCheck size={18} />
            Accept
          </button>
          <button
            onClick={handleRejectRequest}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-700 text-white hover:bg-red-500/20 hover:text-red-400 transition disabled:opacity-50"
          >
            <UserX size={18} />
            Reject
          </button>
        </div>
      );
    
    default: // 'none'
      return (
        <button
          onClick={handleSendRequest}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-400 text-black hover:bg-cyan-300 transition disabled:opacity-50"
        >
          <UserPlus size={18} />
          Add Friend
        </button>
      );
  }
};

export default FriendButton;
