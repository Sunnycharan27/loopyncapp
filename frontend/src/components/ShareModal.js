import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { X, Users, Send, Link as LinkIcon, Copy, Check } from "lucide-react";
import { toast } from "sonner";

const ShareModal = ({ isOpen, onClose, item, type = "post" }) => {
  const { currentUser } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState("friends");
  const [friends, setFriends] = useState([]);
  const [selectedFriends, setSelectedFriends] = useState([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (isOpen) {
      fetchFriends();
    }
  }, [isOpen]);

  const fetchFriends = async () => {
    try {
      const res = await axios.get(`${API}/friends/list?userId=${currentUser.id}`);
      setFriends(res.data.items || []);
    } catch (error) {
      console.error("Failed to load friends");
    }
  };

  const handleShareToFriends = async () => {
    if (selectedFriends.length === 0) {
      toast.error("Please select at least one friend");
      return;
    }

    setLoading(true);
    try {
      // Send to each selected friend via DM
      for (const friendId of selectedFriends) {
        // Get or create DM thread
        const threadRes = await axios.post(`${API}/dm/thread?userId=${currentUser.id}&peerUserId=${friendId}`);
        const threadId = threadRes.data.threadId;

        // Send message with shared content
        const shareText = type === "post" 
          ? `Check out this post: ${item.text?.substring(0, 100) || "Shared post"}`
          : `Check out this video: ${item.caption?.substring(0, 100) || "Shared video"}`;
        
        await axios.post(`${API}/dm/threads/${threadId}/messages`, {
          text: shareText,
          userId: currentUser.id,
          mediaUrl: item.media || item.videoUrl
        });
      }

      toast.success(`Shared with ${selectedFriends.length} friend${selectedFriends.length > 1 ? 's' : ''}!`);
      onClose();
    } catch (error) {
      toast.error("Failed to share");
    } finally {
      setLoading(false);
    }
  };

  const handleShareToTimeline = async () => {
    setLoading(true);
    try {
      if (type === "post") {
        // Repost to timeline
        await axios.post(`${API}/posts/${item.id}/repost?userId=${currentUser.id}`);
        toast.success("Shared to your timeline!");
      } else {
        // Share reel to timeline as post
        await axios.post(`${API}/posts?authorId=${currentUser.id}`, {
          text: `Shared a video: ${item.caption || ""}`,
          media: item.videoUrl,
          audience: "public"
        });
        toast.success("Video shared to your timeline!");
      }
      onClose();
    } catch (error) {
      toast.error("Failed to share to timeline");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyLink = () => {
    const base = window?.location?.origin || '';
    const link = type === "post" 
      ? `${base}/post/${item.id}`
      : `${base}/reel/${item.id}`;
    
    navigator.clipboard.writeText(link);
    setCopied(true);
    toast.success("Link copied to clipboard!");
    
    setTimeout(() => {
      setCopied(false);
    }, 2000);
  };

  const toggleFriendSelection = (friendId) => {
    setSelectedFriends(prev =>
      prev.includes(friendId)
        ? prev.filter(id => id !== friendId)
        : [...prev, friendId]
    );
  };

  const filteredFriends = friends.filter(f =>
    f.user?.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.user?.handle?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.8)' }}>
      <div className="glass-card rounded-2xl max-w-md w-full max-h-[80vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">Share {type === "post" ? "Post" : "Video"}</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-700/50 text-gray-400 hover:text-white transition-all"
          >
            <X size={20} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-700">
          <button
            onClick={() => setActiveTab("friends")}
            className={`flex-1 px-4 py-3 font-medium transition-all ${
              activeTab === "friends"
                ? "text-cyan-400 border-b-2 border-cyan-400"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <Users size={18} className="inline mr-2" />
            Send to Friends
          </button>
          <button
            onClick={() => setActiveTab("options")}
            className={`flex-1 px-4 py-3 font-medium transition-all ${
              activeTab === "options"
                ? "text-cyan-400 border-b-2 border-cyan-400"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <Send size={18} className="inline mr-2" />
            More Options
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === "friends" && (
            <div className="space-y-4">
              {/* Search */}
              <input
                type="text"
                placeholder="Search friends..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 rounded-xl bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400"
              />

              {/* Friends List */}
              <div className="space-y-2">
                {filteredFriends.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    {friends.length === 0 ? "No friends yet" : "No friends found"}
                  </div>
                ) : (
                  filteredFriends.map(({ user }) => (
                    <button
                      key={user.id}
                      onClick={() => toggleFriendSelection(user.id)}
                      className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${
                        selectedFriends.includes(user.id)
                          ? "bg-cyan-400/20 border-2 border-cyan-400"
                          : "bg-gray-800/30 hover:bg-gray-800/50 border-2 border-transparent"
                      }`}
                    >
                      <img
                        src={user.avatar}
                        alt={user.name}
                        className="w-12 h-12 rounded-full"
                      />
                      <div className="flex-1 text-left">
                        <h3 className="text-white font-semibold">{user.name}</h3>
                        <p className="text-sm text-gray-400">@{user.handle}</p>
                      </div>
                      {selectedFriends.includes(user.id) && (
                        <div className="w-6 h-6 rounded-full bg-cyan-400 flex items-center justify-center">
                          <Check size={16} className="text-black" />
                        </div>
                      )}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === "options" && (
            <div className="space-y-3">
              <button
                onClick={handleShareToTimeline}
                disabled={loading}
                className="w-full flex items-center gap-4 p-4 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 transition-all disabled:opacity-50"
              >
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
                  <Send size={20} className="text-white" />
                </div>
                <div className="flex-1 text-left">
                  <h3 className="text-white font-semibold">Share to Timeline</h3>
                  <p className="text-sm text-gray-400">Share with all your followers</p>
                </div>
              </button>

              <button
                onClick={handleCopyLink}
                className="w-full flex items-center gap-4 p-4 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 transition-all"
              >
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center">
                  {copied ? <Check size={20} className="text-white" /> : <Copy size={20} className="text-white" />}
                </div>
                <div className="flex-1 text-left">
                  <h3 className="text-white font-semibold">
                    {copied ? "Link Copied!" : "Copy Link"}
                  </h3>
                  <p className="text-sm text-gray-400">Share via other apps</p>
                </div>
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        {activeTab === "friends" && (
          <div className="p-4 border-t border-gray-700">
            <button
              onClick={handleShareToFriends}
              disabled={loading || selectedFriends.length === 0}
              className="w-full py-3 rounded-xl bg-cyan-400 text-black font-semibold hover:bg-cyan-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading
                ? "Sending..."
                : `Send to ${selectedFriends.length} friend${selectedFriends.length !== 1 ? 's' : ''}`
              }
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ShareModal;
