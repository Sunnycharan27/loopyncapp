import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { X, Search, Send, Check } from "lucide-react";
import { toast } from "sonner";

const ShareToFriendsModal = ({ currentUser, item, type, onClose }) => {
  const [friends, setFriends] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFriends, setSelectedFriends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchFriends();
  }, []);

  const fetchFriends = async () => {
    try {
      // Get actual friends list
      const res = await axios.get(`${API}/users/${currentUser.id}/friends`);
      setFriends(res.data || []);
    } catch (error) {
      console.error("Failed to fetch friends:", error);
      toast.error("Failed to load friends");
    } finally {
      setLoading(false);
    }
  };

  const filteredFriends = friends.filter(friend =>
    friend.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    friend.handle?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const toggleFriend = (friendId) => {
    if (selectedFriends.includes(friendId)) {
      setSelectedFriends(selectedFriends.filter(id => id !== friendId));
    } else {
      setSelectedFriends([...selectedFriends, friendId]);
    }
  };

  const getShareMessage = () => {
    switch (type) {
      case 'post':
        return `${currentUser.name} shared a post with you: ${item.caption?.substring(0, 50) || 'Check this out!'}`;
      case 'reel':
        return `${currentUser.name} shared a reel with you: ${item.caption?.substring(0, 50) || 'Watch this!'}`;
      case 'room':
        return `${currentUser.name} invited you to join "${item.name}" - Live audio room!`;
      case 'event':
        return `${currentUser.name} shared an event: ${item.name}`;
      case 'tribe':
        return `${currentUser.name} invited you to join "${item.name}" tribe`;
      case 'venue':
        return `${currentUser.name} wants you to check out ${item.name}`;
      case 'product':
        return `${currentUser.name} shared a product: ${item.name}`;
      default:
        return `${currentUser.name} shared something with you!`;
    }
  };

  const getShareLink = () => {
    const baseUrl = window.location.origin;
    switch (type) {
      case 'post':
        return `${baseUrl}/posts/${item.id}`;
      case 'reel':
        return `${baseUrl}/reels/${item.id}`;
      case 'room':
        return `${baseUrl}/viberooms/${item.id}`;
      case 'event':
        return `${baseUrl}/events/${item.id}`;
      case 'tribe':
        return `${baseUrl}/tribes/${item.id}`;
      case 'venue':
        return `${baseUrl}/venues/${item.id}`;
      case 'product':
        return `${baseUrl}/marketplace/${item.id}`;
      default:
        return baseUrl;
    }
  };

  const handleSend = async () => {
    if (selectedFriends.length === 0) {
      toast.error("Please select at least one friend");
      return;
    }

    setSending(true);
    try {
      const message = getShareMessage();
      const link = getShareLink();
      
      // Send to each selected friend
      const sendPromises = selectedFriends.map(friendId =>
        axios.post(`${API}/share`, {
          fromUserId: currentUser.id,
          toUserId: friendId,
          contentType: type,
          contentId: item.id,
          message: message,
          link: link
        }).catch(error => {
          console.error(`Failed to share with ${friendId}:`, error);
          return null; // Don't fail entire operation if one fails
        })
      );

      await Promise.all(sendPromises);
      
      toast.success(`Shared with ${selectedFriends.length} friend${selectedFriends.length > 1 ? 's' : ''}!`);
      onClose();
    } catch (error) {
      console.error("Failed to share:", error);
      toast.error("Failed to share with friends");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-b from-gray-900 to-black w-full max-w-md rounded-3xl border border-gray-800 flex flex-col max-h-[80vh]">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white">Share with Friends</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition"
            >
              <X size={24} />
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search friends..."
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-full text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400"
            />
          </div>

          {/* Selected Count */}
          {selectedFriends.length > 0 && (
            <div className="mt-3 text-center">
              <span className="text-sm text-cyan-400">
                {selectedFriends.length} friend{selectedFriends.length > 1 ? 's' : ''} selected
              </span>
            </div>
          )}
        </div>

        {/* Friends List */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
            </div>
          ) : filteredFriends.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400">
                {searchQuery ? "No friends found" : "No friends to share with"}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                {!searchQuery && "Follow people to see them here"}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredFriends.map((friend) => {
                const isSelected = selectedFriends.includes(friend.id);
                return (
                  <button
                    key={friend.id}
                    onClick={() => toggleFriend(friend.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-2xl transition ${
                      isSelected
                        ? 'bg-cyan-400/20 border-2 border-cyan-400'
                        : 'bg-gray-800 hover:bg-gray-700 border-2 border-transparent'
                    }`}
                  >
                    <img
                      src={friend.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${friend.name}`}
                      alt={friend.name}
                      className="w-12 h-12 rounded-full"
                    />
                    <div className="flex-1 text-left">
                      <p className="text-white font-semibold">{friend.name}</p>
                      <p className="text-sm text-gray-400">@{friend.handle}</p>
                    </div>
                    {isSelected && (
                      <div className="w-6 h-6 rounded-full bg-cyan-400 flex items-center justify-center">
                        <Check size={16} className="text-black" />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800">
          <button
            onClick={handleSend}
            disabled={selectedFriends.length === 0 || sending}
            className="w-full py-3 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 transition flex items-center justify-center gap-2"
          >
            {sending ? (
              <>
                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
                Sending...
              </>
            ) : (
              <>
                <Send size={20} />
                Send to {selectedFriends.length || '...'} Friend{selectedFriends.length !== 1 ? 's' : ''}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ShareToFriendsModal;
