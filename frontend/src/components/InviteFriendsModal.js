import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { X, Search, UserPlus, Check, Share2, Copy, Users } from "lucide-react";
import { toast } from "sonner";

const InviteFriendsModal = ({ room, onClose }) => {
  const { currentUser } = useContext(AuthContext);
  const [friends, setFriends] = useState([]);
  const [search, setSearch] = useState("");
  const [inviting, setInviting] = useState({});
  const [invited, setInvited] = useState(new Set());
  const [shareLink, setShareLink] = useState("");
  const [activeTab, setActiveTab] = useState("friends");

  useEffect(() => {
    fetchFriends();
    fetchShareLink();
  }, []);

  const fetchFriends = async () => {
    try {
      const res = await axios.get(`${API}/users/${currentUser.id}/friends`);
      setFriends(res.data);
    } catch (error) {
      console.error("Failed to load friends");
    }
  };

  const fetchShareLink = async () => {
    try {
      const res = await axios.get(`${API}/rooms/${room.id}/share-link`);
      setShareLink(res.data.shareLink);
    } catch (error) {
      console.error("Failed to get share link");
    }
  };

  const handleInvite = async (friendId) => {
    setInviting({ ...inviting, [friendId]: true });
    try {
      await axios.post(`${API}/rooms/${room.id}/invite?fromUserId=${currentUser.id}&toUserId=${friendId}`);
      setInvited(new Set([...invited, friendId]));
      toast.success("Invitation sent!");
    } catch (error) {
      toast.error("Failed to send invitation");
    } finally {
      setInviting({ ...inviting, [friendId]: false });
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareLink || `${window.location.origin}/rooms/${room.id}`);
    toast.success("Link copied to clipboard!");
  };

  const filteredFriends = friends.filter(friend =>
    friend.name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card w-full max-w-md max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-cyan-400/20">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <UserPlus size={24} className="text-cyan-400" />
              Invite to Room
            </h2>
            <p className="text-sm text-gray-400 mt-1">{room.name}</p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-gray-800/50 hover:bg-gray-700/50 flex items-center justify-center text-gray-400"
          >
            <X size={18} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-cyan-400/20">
          <button
            onClick={() => setActiveTab("friends")}
            className={`flex-1 px-4 py-3 text-sm font-semibold transition-all ${
              activeTab === "friends"
                ? "text-cyan-400 border-b-2 border-cyan-400"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <Users size={16} className="inline mr-2" />
            Friends
          </button>
          <button
            onClick={() => setActiveTab("share")}
            className={`flex-1 px-4 py-3 text-sm font-semibold transition-all ${
              activeTab === "share"
                ? "text-cyan-400 border-b-2 border-cyan-400"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <Share2 size={16} className="inline mr-2" />
            Share Link
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {activeTab === "friends" ? (
            <>
              {/* Search */}
              <div className="relative mb-4">
                <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search friends..."
                  className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-cyan-400/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400"
                />
              </div>

              {/* Friends List */}
              {filteredFriends.length === 0 ? (
                <div className="text-center py-12">
                  <Users size={48} className="text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">
                    {search ? "No friends found" : "No friends yet"}
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredFriends.map((friend) => (
                    <div
                      key={friend.id}
                      className="flex items-center gap-3 p-3 rounded-lg bg-gray-800/30 hover:bg-gray-800/50 transition-all"
                    >
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                        <span className="text-white font-bold text-sm">
                          {friend.name?.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-semibold">{friend.name}</p>
                        <p className="text-xs text-gray-400">@{friend.handle}</p>
                      </div>
                      {invited.has(friend.id) ? (
                        <div className="flex items-center gap-1 text-green-400 text-sm">
                          <Check size={16} />
                          Invited
                        </div>
                      ) : (
                        <button
                          onClick={() => handleInvite(friend.id)}
                          disabled={inviting[friend.id]}
                          className="px-4 py-2 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white text-sm font-semibold hover:opacity-90 disabled:opacity-50"
                        >
                          {inviting[friend.id] ? "Sending..." : "Invite"}
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <>
              {/* Share Link */}
              <div className="text-center mb-6">
                <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                  <Share2 size={40} className="text-white" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Share Room Link</h3>
                <p className="text-sm text-gray-400">
                  Anyone with this link can join the room
                </p>
              </div>

              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-gray-800/50 border border-cyan-400/30">
                  <p className="text-xs text-gray-400 mb-2">Room Link</p>
                  <p className="text-white text-sm break-all">
                    {shareLink || `${window.location.origin}/rooms/${room.id}`}
                  </p>
                </div>

                <button
                  onClick={handleCopyLink}
                  className="w-full py-3 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold hover:opacity-90 flex items-center justify-center gap-2"
                >
                  <Copy size={18} />
                  Copy Link
                </button>

                <div className="text-center">
                  <p className="text-xs text-gray-500">
                    Share this link via WhatsApp, Telegram, or any messaging app
                  </p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default InviteFriendsModal;
