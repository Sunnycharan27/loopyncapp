import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { ArrowLeft, Heart, MessageCircle, Users, ShoppingBag, Ticket } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

const Notifications = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

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
        return <Heart size={18} className="text-gray-400" />;
    }
  };

  const getNotificationText = (notif) => {
    const { type, payload } = notif;
    switch (type) {
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
    <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-2xl mx-auto">
        <div className="sticky top-0 z-10 glass-surface p-4 flex items-center gap-3">
          <button onClick={() => navigate('/')} className="text-cyan-400">
            <ArrowLeft size={24} />
          </button>
          <div>
            <h1 className="text-2xl font-bold neon-text">Notifications</h1>
            <p className="text-xs text-gray-400">Stay updated</p>
          </div>
        </div>

        <div className="p-4 space-y-3">
          {notifications.length === 0 ? (
            <div className="text-center py-12 glass-card p-8">
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
                data-testid="notification-item"
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center">
                    {getNotificationIcon(notif.type)}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm">
                      <span className="font-semibold">{notif.payload.fromName || 'Someone'}</span>
                      {' '}{getNotificationText(notif)}
                    </p>
                    <span className="text-xs text-gray-500">
                      {new Date(notif.createdAt).toLocaleString()}
                    </span>
                  </div>
                  {!notif.read && (
                    <div className="w-2 h-2 rounded-full bg-cyan-400"></div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Notifications;