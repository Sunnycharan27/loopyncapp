import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { ArrowLeft, Heart, MessageCircle, Users, ShoppingBag, Ticket, UserPlus, UserCheck, UserX, Bell } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import BottomNav from "../components/BottomNav";
import { useWebSocket } from "../context/WebSocketContext";

const Notifications = () => {
  const { currentUser } = useContext(AuthContext);
  const { connected } = useWebSocket() || { connected: false };
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [friendRequests, setFriendRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all"); // all, requests

  useEffect(() => {
    fetchNotifications();
    fetchFriendRequests();
  }, []);

  const fetchFriendRequests = async () => {
    try {
      const res = await axios.get(`${API}/friend-requests?userId=${currentUser.id}`);
      const incoming = res.data?.filter(req => req.status === 'pending' && req.toUserId === currentUser.id) || [];
      setFriendRequests(incoming);
    } catch (error) {
      console.error("Failed to load friend requests", error);
      setFriendRequests([]);
    }
  };

  const [roomInvites, setRoomInvites] = useState([]);

  const fetchRoomInvites = async () => {
    try {
      const res = await axios.get(`${API}/rooms/invites/${currentUser.id}`);
      setRoomInvites(res.data);
    } catch (error) {
      console.error("Failed to load room invites");
    }
  };

  useEffect(() => {
    fetchRoomInvites();
  }, []);

  const handleAcceptRoomInvite = async (inviteId) => {
    try {
      const res = await axios.post(`${API}/rooms/invites/${inviteId}/accept?userId=${currentUser.id}`);
      toast.success("Joining room...");
      navigate(`/rooms/${res.data.room.id}`);
    } catch (error) {
      toast.error("Failed to accept invite");
    }
  };

  const handleDeclineRoomInvite = async (inviteId) => {
    try {
      await axios.post(`${API}/rooms/invites/${inviteId}/decline?userId=${currentUser.id}`);
      setRoomInvites(roomInvites.filter(inv => inv.id !== inviteId));
      toast.success("Invite declined");
    } catch (error) {
      toast.error("Failed to decline");
    }
  };

  const fetchNotifications = async () => {
    try {
      const res = await axios.get(`${API}/notifications?userId=${currentUser.id}`);
      setNotifications(res.data);
    } catch (error) {
      toast.error("Failed to load notifications");
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRequest = async (requestId, fromUser) => {
    try {
      await axios.post(`${API}/friend-requests/${requestId}/accept`);
      toast.success(`You and ${fromUser.name} are now friends! 🎉`);
      fetchFriendRequests();
      fetchNotifications();
    } catch (error) {
      toast.error("Failed to accept request");
    }
  };

  const handleRejectRequest = async (requestId) => {
    try {
      await axios.post(`${API}/friend-requests/${requestId}/reject`);
      toast.success("Friend request rejected");
      fetchFriendRequests();
    } catch (error) {
      toast.error("Failed to reject request");
    }
  };

  const handleNotificationClick = async (notif) => {
    // Mark as read
    if (!notif.read) {
      await axios.post(`${API}/notifications/${notif.id}/read`);
    }

    // Deep link routing
    const { type, payload } = notif;
    switch (type) {
      case 'post_like':
      case 'post_comment':
        navigate('/');
        break;
      case 'tribe_join':
        navigate(`/tribes/${payload.tribeId}`);
        break;
      case 'order_placed':
      case 'order_ready':
        navigate('/discover');
        break;
      case 'ticket_bought':
        navigate('/discover');
        break;
      case 'dm':
        navigate('/messenger');
        break;
      default:
        break;
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'friend_request':
        return <UserPlus size={18} className="text-blue-400" />;
      case 'friend_accepted':
        return <UserCheck size={18} className="text-green-400" />;
      case 'post_like':
        return <Heart size={18} className="text-pink-400" />;
      case 'post_comment':
      case 'dm':
        return <MessageCircle size={18} className="text-cyan-400" />;
      case 'tribe_join':
        return <Users size={18} className="text-green-400" />;
      case 'order_placed':
      case 'order_ready':
        return <ShoppingBag size={18} className="text-yellow-400" />;
      case 'ticket_bought':
        return <Ticket size={18} className="text-purple-400" />;
      default:
        return <Bell size={18} className="text-gray-400" />;
    }
  };

  const getNotificationText = (notif) => {
    const { type, payload } = notif;
    switch (type) {
      case 'friend_request':
        return 'sent you a friend request';
      case 'friend_accepted':
        return 'accepted your friend request';
      case 'post_like':
        return 'liked your post';
      case 'post_comment':
        return 'commented on your post';
      case 'tribe_join':
        return 'joined your tribe';
      case 'order_placed':
        return `Order placed • ₹${payload.total}`;
      case 'order_ready':
        return 'Your order is ready!';
      case 'ticket_bought':
        return 'Ticket purchased successfully';
      case 'dm':
        return payload.text || 'sent you a message';
      default:
        return 'New notification';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0f021e' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-2xl mx-auto">
        <div className="sticky top-0 z-10 glass-surface p-4">
          <div className="flex items-center gap-3 mb-4">
            <button onClick={() => navigate('/')} className="text-cyan-400">
              <ArrowLeft size={24} />
            </button>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold neon-text">Notifications</h1>
                {connected && (
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
                    <span className="text-xs text-green-400">Live</span>
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-400">Stay updated</p>
            </div>
            {friendRequests.length > 0 && (
              <div className="px-3 py-1 rounded-full bg-red-500 text-white text-xs font-bold">
                {friendRequests.length}
              </div>
            )}
          </div>

          {/* Tabs */}
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab("all")}
              className={`flex-1 py-2 px-4 rounded-full font-medium text-sm transition-all ${
                activeTab === "all"
                  ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              <Bell size={16} className="inline mr-2" />
              All
            </button>
            <button
              onClick={() => setActiveTab("requests")}
              className={`flex-1 py-2 px-4 rounded-full font-medium text-sm transition-all relative ${
                activeTab === "requests"
                  ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              <UserPlus size={16} className="inline mr-2" />
              Friend Requests
              {friendRequests.length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
                  {friendRequests.length}
                </span>
              )}
            </button>
          </div>
        </div>

        <div className="p-4 space-y-3">
          {/* Friend Requests Tab */}
          {activeTab === "requests" && (
            <>
              {/* Room Invites Section */}
              {roomInvites.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-400 mb-3">Room Invitations</h3>
                  {roomInvites.map(invite => (
                    <div key={invite.id} className="glass-card p-4 mb-3">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-14 h-14 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                          <Users size={24} className="text-white" />
                        </div>
                        <div className="flex-1">
                          <p className="font-semibold text-white">{invite.fromUserName}</p>
                          <p className="text-sm text-gray-400">invited you to join</p>
                          <p className="text-sm text-cyan-400 font-semibold mt-1">{invite.roomName}</p>
                          <p className="text-xs text-gray-500 capitalize">{invite.roomCategory}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleAcceptRoomInvite(invite.id)}
                          className="flex-1 py-2 px-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold hover:opacity-90"
                        >
                          Join Room
                        </button>
                        <button
                          onClick={() => handleDeclineRoomInvite(invite.id)}
                          className="px-4 py-2 rounded-full border-2 border-red-400/30 text-red-400 hover:bg-red-400/10"
                        >
                          Decline
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Friend Requests Section */}
              <h3 className="text-sm font-semibold text-gray-400 mb-3">Friend Requests</h3>
              {friendRequests.length === 0 ? (
                <div className="text-center py-12 glass-card p-8">
                  <UserPlus size={48} className="text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No pending friend requests</p>
                </div>
              ) : (
                friendRequests.map(request => (
                  <div key={request.id} className="glass-card p-4">
                    <div className="flex items-center gap-3">
                      <img 
                        src={request.fromUser?.avatar || 'https://i.pravatar.cc/150?img=1'} 
                        alt={request.fromUser?.name} 
                        className="w-14 h-14 rounded-full"
                      />
                      <div className="flex-1">
                        <p className="font-semibold text-white">{request.fromUser?.name || 'User'}</p>
                        <p className="text-sm text-gray-400">@{request.fromUser?.handle || 'user'}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(request.createdAt).toLocaleDateString('en-IN', {
                            day: 'numeric',
                            month: 'short'
                          })}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2 mt-3">
                      <button
                        onClick={() => handleAcceptRequest(request.id, request.fromUser)}
                        className="flex-1 py-2 px-4 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 text-white font-semibold hover:opacity-90 transition-all"
                      >
                        <UserCheck size={16} className="inline mr-2" />
                        Accept
                      </button>
                      <button
                        onClick={() => handleRejectRequest(request.id)}
                        className="flex-1 py-2 px-4 rounded-full border-2 border-gray-700 text-gray-400 font-semibold hover:bg-gray-800/50 transition-all"
                      >
                        <UserX size={16} className="inline mr-2" />
                        Reject
                      </button>
                    </div>
                  </div>
                ))
              )}
            </>
          )}

          {/* All Notifications Tab */}
          {activeTab === "all" && (
            <>
              {notifications.length === 0 ? (
                <div className="text-center py-12 glass-card p-8">
                  <Bell size={48} className="text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No notifications yet</p>
                </div>
              ) : (
                notifications.map(notif => (
                  <div
                    key={notif.id}
                    onClick={() => handleNotificationClick(notif)}
                    className={`glass-card p-4 cursor-pointer hover:bg-cyan-400/5 transition-all ${
                      !notif.read ? 'border-l-4 border-cyan-400' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center flex-shrink-0">
                        {getNotificationIcon(notif.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="text-sm">
                              <span className="font-semibold text-white">{notif.fromUser?.name || 'Loopync'}</span>
                              <span className="text-gray-400"> {getNotificationText(notif)}</span>
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(notif.createdAt).toLocaleDateString('en-IN', {
                                day: 'numeric',
                                month: 'short',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </p>
                          </div>
                          {!notif.read && (
                            <div className="w-2 h-2 rounded-full bg-cyan-400 flex-shrink-0 mt-1"></div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </>
          )}
        </div>
      </div>
      <BottomNav active="notifications" />
    </div>
  );
};

export default Notifications;