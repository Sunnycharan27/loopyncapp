import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { ArrowLeft, Send, Image as ImageIcon, Users, Shield, Search, X, Sparkles, FileText, MapPin, Calendar } from "lucide-react";
import { toast } from "sonner";
import { useNavigate, useParams } from "react-router-dom";
import { useWebSocket } from "../context/WebSocketContext";

const Messenger = () => {
  const { threadId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const { connected, emitTyping } = useWebSocket();
  const navigate = useNavigate();
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null); // { id, peer }
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState("");
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [activeView, setActiveView] = useState("chats"); // chats, circles
  const [searchQuery, setSearchQuery] = useState("");
  const [friendResults, setFriendResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showCreateCircle, setShowCreateCircle] = useState(false);
  const [trustCircles, setTrustCircles] = useState([]);
  const [selectedCircle, setSelectedCircle] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    fetchThreads();
    fetchTrustCircles();
  }, []);

  useEffect(() => {
    // If URL has a threadId param, try to open it once threads are loaded/updated
    if (threadId && threads.length > 0) {
      const t = threads.find(t => t.id === threadId);
      if (t) {
        setSelectedThread(t);
        fetchMessages(t.id);
      }
    }
  }, [threadId, threads]);

  const fetchTrustCircles = async () => {
    try {
      const res = await axios.get(`${API}/trust-circles?userId=${currentUser.id}`);
      setTrustCircles(res.data);
    } catch (error) {
      console.error("Failed to fetch trust circles:", error);
      // Use fallback mock data if endpoint not ready
      setTrustCircles([
        { 
          id: "c1", 
          name: "Close Friends", 
          members: [], 
          memberCount: 5, 
          color: "from-pink-400 to-rose-500", 
          icon: "❤️",
          description: "My closest friends",
          createdBy: currentUser.id
        },
        { 
          id: "c2", 
          name: "Family", 
          members: [], 
          memberCount: 8, 
          color: "from-green-400 to-emerald-500", 
          icon: "🏠",
          description: "Family members",
          createdBy: currentUser.id
        }
      ]);
    }
  };

  const createTrustCircle = async (name, description, icon, color, members) => {
    try {
      const res = await axios.post(`${API}/trust-circles`, {
        name,
        description,
        icon,
        color,
        members,
        createdBy: currentUser.id
      });
      setTrustCircles([...trustCircles, res.data]);
      toast.success(`Trust Circle "${name}" created!`);
      setShowCreateCircle(false);
      return res.data;
    } catch (error) {
      console.error("Failed to create trust circle:", error);
      // Fallback: create locally
      const newCircle = {
        id: `c${Date.now()}`,
        name,
        description,
        icon,
        color,
        members: members || [],
        memberCount: members?.length || 0,
        createdBy: currentUser.id,
        createdAt: new Date().toISOString()
      };
      setTrustCircles([...trustCircles, newCircle]);
      toast.success(`Trust Circle "${name}" created!`);
      setShowCreateCircle(false);
      return newCircle;
    }
  };

  const addMemberToCircle = async (circleId, memberId) => {
    try {
      await axios.post(`${API}/trust-circles/${circleId}/members`, { memberId });
      fetchTrustCircles();
      toast.success("Member added to circle");
    } catch (error) {
      toast.error("Failed to add member");
    }
  };

  const removeMemberFromCircle = async (circleId, memberId) => {
    try {
      await axios.delete(`${API}/trust-circles/${circleId}/members/${memberId}`);
      fetchTrustCircles();
      toast.success("Member removed from circle");
    } catch (error) {
      toast.error("Failed to remove member");
    }
  };

  const deleteCircle = async (circleId) => {
    if (!confirm("Are you sure you want to delete this Trust Circle?")) return;
    
    try {
      await axios.delete(`${API}/trust-circles/${circleId}`);
      setTrustCircles(trustCircles.filter(c => c.id !== circleId));
      toast.success("Trust Circle deleted");
    } catch (error) {
      // Fallback: delete locally
      setTrustCircles(trustCircles.filter(c => c.id !== circleId));
      toast.success("Trust Circle deleted");
    }
  };

  // Context Card for active chat
  const getContextCard = (peer) => {
    if (!peer) return null;
    
    // Mock context data
    return {
      sharedInterests: ["Music", "Food", "Travel"],
      mutualFriends: 12,
      lastInteraction: "Liked your post 2 days ago",
      location: "Mumbai, India",
      upcomingEvents: ["TechCrunch Disrupt Mumbai - Nov 15"]
    };
  };

  const fetchThreads = async () => {
    try {
      // Use DM threads API
      const res = await axios.get(`${API}/dm/threads?userId=${currentUser.id}`);
      const items = res.data.items || [];
      const normalized = items.map(it => ({
        id: it.id,
        peer: it.peer,
        lastMessage: it.lastMessage?.text || '',
        timestamp: it.updatedAt,
        unread: (it.unreadCount || 0) > 0
      }));
      setThreads(normalized);
    } catch (error) {
      console.error("Failed to load threads", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (threadIdToLoad) => {
    try {
      const res = await axios.get(`${API}/dm/threads/${threadIdToLoad}/messages?userId=${currentUser.id}`);
      setMessages(res.data.items || []);
    } catch (error) {
      console.error("Failed to load messages", error);
    }
  };

  const handleThreadClick = (thread) => {
    setSelectedThread(thread);
    fetchMessages(thread.id);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageText.trim() || !selectedThread) return;

    const tempMessage = {
      id: `temp-${Date.now()}`,
      threadId: selectedThread.id,
      senderId: currentUser.id,
      text: messageText,
      createdAt: new Date().toISOString(),
      sending: true
    };

    // Optimistic update
    setMessages([...messages, tempMessage]);
    setMessageText("");

    try {
      await axios.post(`${API}/dm/threads/${selectedThread.id}/messages?userId=${currentUser.id}`, {
        text: messageText
      });
      await fetchMessages(selectedThread.id);
    } catch (error) {
      // If thread was missing for some reason, auto-create and retry once
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;
      if ((status === 404 || status === 403) && selectedThread?.peer?.id) {
        try {
          const create = await axios.post(`${API}/dm/thread?userId=${currentUser.id}&peerUserId=${selectedThread.peer.id}`);
          const newThreadId = create.data.threadId;
          setSelectedThread({ ...selectedThread, id: newThreadId });
          await axios.post(`${API}/dm/threads/${newThreadId}/messages?userId=${currentUser.id}`, { text: messageText });
          await fetchThreads();
          await fetchMessages(newThreadId);
          return;
        } catch (e2) {
          toast.error(e2?.response?.data?.detail || 'Unable to create thread');
        }
      } else {
        toast.error(detail || "Failed to send message");
      }
      // Remove temp message on error
      setMessages(prev => prev.filter(msg => msg.id !== tempMessage.id));
    }
  };

  const searchFriends = async (q) => {
    if (!q.trim()) { setFriendResults([]); return; }
    setSearching(true);
    try {
      const res = await axios.get(`${API}/friends/list?userId=${currentUser.id}&q=${encodeURIComponent(q)}&limit=20`);
      const items = (res.data.items || []).map(it => it.user);
      setFriendResults(items);
    } catch (e) {
      console.error('friend search failed', e);
    } finally {
      setSearching(false);
    }
  };

  const startChatWith = async (user) => {
    try {
      const res = await axios.post(`${API}/dm/thread?userId=${currentUser.id}&peerUserId=${user.id}`);
      const threadId = res.data.threadId;
      // Refresh threads and open
      await fetchThreads();
      const t = { id: threadId, peer: user };
      setSelectedThread(t);
      fetchMessages(threadId);
      setSearchQuery("");
      setFriendResults([]);
      setActiveView('chats');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Unable to start chat');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !selectedThread) return;

    // Validate file type
    const isImage = file.type.startsWith('image/');
    const isVideo = file.type.startsWith('video/');
    
    if (!isImage && !isVideo) {
      toast.error("Only images and videos are supported");
      return;
    }

    // Validate size
    const maxSize = isVideo ? 50 * 1024 * 1024 : 10 * 1024 * 1024;
    if (file.size > maxSize) {
      toast.error(`File too large. Max ${isVideo ? '50MB' : '10MB'}`);
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const uploadRes = await axios.post(`${API}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      
      const relativeUrl = uploadRes.data.url; // starts with /uploads
      const mediaUrl = `${API}${relativeUrl}`; // ensure /api/uploads for ingress
      
      // Send message with media via DM API
      await axios.post(`${API}/dm/threads/${selectedThread.id}/messages?userId=${currentUser.id}`, {
        text: isVideo ? "📹 Video" : "📷 Photo",
        mediaUrl,
        mimeType: file.type
      });
      
      await fetchMessages(selectedThread.id);
      toast.success(`${isVideo ? 'Video' : 'Photo'} sent!`);
    } catch (error) {
      toast.error("Failed to upload media");
    } finally {
      setUploading(false);
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
      {!selectedThread ? (
        // Thread List with Tabs
        <div className="max-w-2xl mx-auto pb-24">
          <div className="sticky top-0 z-10 glass-surface p-4">
            <div className="flex items-center gap-3 mb-4">
              <button onClick={() => navigate('/')} className="text-cyan-400">
                <ArrowLeft size={24} />
              </button>
              <div>
                <h1 className="text-2xl font-bold neon-text">Messenger</h1>
                <p className="text-xs text-gray-400">Connect with your vibes</p>
              </div>
            </div>

            {/* Tabs - Only Chats and Trust Circles */}
            <div className="flex gap-2 overflow-x-auto scrollbar-hide">
              <button
                onClick={() => setActiveView("chats")}
                className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-full font-medium text-sm transition-all ${
                  activeView === "chats"
                    ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                    : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
                }`}
              >
                <Send size={16} />
                Chats
              </button>
              <button
                onClick={() => setActiveView("circles")}
                className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-full font-medium text-sm transition-all ${
                  activeView === "circles"
                    ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                    : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
                }`}
              >
                <Shield size={16} />
                Trust Circles
              </button>
            </div>

            <div className="flex items-center gap-2">
              <div className="flex-1 relative">
                <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    const v = e.target.value;
                    setSearchQuery(v);
                    searchFriends(v);
                  }}
                  placeholder="Search chats or friends..."
                  className="w-full pl-10 pr-3 py-2 rounded-full bg-black/30 border border-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                  data-testid="friend-search-input"
                />
                {searchQuery && (
                  <button className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white" onClick={() => { setSearchQuery(""); setFriendResults([]); }}>
                    <X size={16} />
                  </button>
                )}

                {/* Friend search results dropdown */}
                {searchQuery && friendResults.length > 0 && (
                  <div className="absolute z-10 mt-2 w-full max-h-72 overflow-auto rounded-xl bg-black/80 border border-gray-800 backdrop-blur p-2 space-y-2">
                    {friendResults.map((u) => (
                      <div key={u.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 cursor-pointer" onClick={() => startChatWith(u)}>
                        <img src={u.avatar} alt={u.name} className="w-8 h-8 rounded-full" />
                        <div className="flex-1">
                          <p className="text-sm text-white font-semibold">{u.name}</p>
                          <p className="text-xs text-gray-400">@{u.handle}</p>
                        </div>
                        <button className="px-2 py-1 rounded-full bg-cyan-400 text-black text-xs font-semibold">Message</button>
                      </div>
                    ))}
                    {searching && (
                      <div className="text-center text-xs text-gray-500 py-2">Searching…</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Chats View */}
          {activeView === "chats" && (
            <div className="p-4 space-y-3">
              {threads.length === 0 ? (
                <div className="text-center py-12 glass-card p-8">
                  <p className="text-gray-400">No messages yet</p>
                  <p className="text-sm text-gray-500 mt-2">Start a conversation from a profile</p>
                </div>
              ) : (
                threads.map(thread => (
                  <div
                    key={thread.peer.id}
                    onClick={() => handleThreadClick(thread)}
                    className="glass-card p-4 cursor-pointer hover:bg-cyan-400/5 transition-all"
                    data-testid="message-thread"
                  >
                    <div className="flex items-center gap-3">
                      <img src={thread.peer.avatar} alt={thread.peer.name} className="w-12 h-12 rounded-full" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className="font-semibold">{thread.peer.name}</p>
                          <span className="text-xs text-gray-400">
                            {new Date(thread.timestamp).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 truncate">{thread.lastMessage}</p>
                      </div>
                      {thread.unread && (
                        <div className="w-3 h-3 rounded-full bg-cyan-400"></div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Vibe Rooms View */}
          {activeView === "rooms" && (
            <div className="p-4 space-y-3">
              <div className="glass-card p-4 mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles size={20} className="text-yellow-400" />
                  <h3 className="font-bold text-white">Vibe Rooms</h3>
                </div>
                <p className="text-sm text-gray-400">Join group spaces based on your interests</p>
              </div>

              {vibeRooms.map(room => (
                <div
                  key={room.id}
                  className="glass-card p-4 cursor-pointer hover:scale-[1.01] transition-transform"
                  onClick={() => toast.info("Vibe Rooms coming soon!")}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-400/20 to-pink-500/20 flex items-center justify-center text-4xl">
                      {room.emoji}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-white mb-1">{room.name}</h3>
                      <div className="flex items-center gap-3 text-xs text-gray-400">
                        <span>{room.members} members</span>
                        <span className="flex items-center gap-1">
                          <div className="w-2 h-2 rounded-full bg-green-400"></div>
                          {room.activeNow} active
                        </span>
                      </div>
                      <div className="mt-2">
                        <span className="inline-block px-2 py-1 rounded-full bg-cyan-400/10 text-cyan-400 text-xs font-semibold">
                          {room.category}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Trust Circles View */}
          {activeView === "circles" && (
            <div className="p-4 space-y-3">
              <div className="glass-card p-4 mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Shield size={20} className="text-blue-400" />
                  <h3 className="font-bold text-white">Trust Circles</h3>
                </div>
                <p className="text-sm text-gray-400">Organize your connections into private groups</p>
              </div>

              <button
                onClick={() => toast.info("Create Circle feature coming soon!")}
                className="w-full py-3 rounded-full border-2 border-dashed border-gray-700 text-gray-400 hover:border-cyan-400 hover:text-cyan-400 transition-all"
              >
                + Create New Circle
              </button>

              {trustCircles.map(circle => (
                <div
                  key={circle.id}
                  className="glass-card p-4 cursor-pointer hover:scale-[1.01] transition-transform"
                  onClick={() => toast.info("Circle details coming soon!")}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${circle.color} flex items-center justify-center text-3xl`}>
                      {circle.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-white mb-1">{circle.name}</h3>
                      <p className="text-sm text-gray-400">{circle.members} members</p>
                    </div>
                    <ArrowLeft size={20} className="text-gray-500 rotate-180" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        // Chat View with Context Card
        <div className="flex flex-col h-screen">
          <div className="glass-surface p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button onClick={() => setSelectedThread(null)} className="text-cyan-400">
                <ArrowLeft size={24} />
              </button>
              <img src={selectedThread.peer.avatar} alt={selectedThread.peer.name} className="w-10 h-10 rounded-full" />
              <div className="flex-1">
                <p className="font-semibold">{selectedThread.peer.name}</p>
                <p className="text-xs text-gray-400">@{selectedThread.peer.handle}</p>
              </div>
            </div>
            
            {/* Context Card Toggle */}
            <button
              onClick={() => setShowCircles(!showCircles)}
              className="p-2 rounded-full hover:bg-cyan-400/10 text-cyan-400"
              title="View context"
            >
              <FileText size={20} />
            </button>
          </div>

          {/* Context Card */}
          {showCircles && (
            <div className="glass-card m-4 p-4 space-y-3">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles size={18} className="text-cyan-400" />
                <h3 className="font-bold text-white">Connection Context</h3>
              </div>
              
              {(() => {
                const context = getContextCard(selectedThread.peer);
                return context ? (
                  <>
                    <div>
                      <p className="text-xs text-gray-500 mb-2">Shared Interests</p>
                      <div className="flex flex-wrap gap-2">
                        {context.sharedInterests.map((interest, idx) => (
                          <span key={idx} className="px-2 py-1 rounded-full bg-purple-500/20 text-purple-400 text-xs">
                            {interest}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <Users size={16} className="text-cyan-400" />
                      <span>{context.mutualFriends} mutual friends</span>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <MapPin size={16} className="text-cyan-400" />
                      <span>{context.location}</span>
                    </div>

                    {context.upcomingEvents.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 mb-2">Upcoming Events</p>
                        {context.upcomingEvents.map((event, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-sm text-gray-400">
                            <Calendar size={16} className="text-cyan-400" />
                            <span>{event}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="pt-2 border-t border-gray-700">
                      <p className="text-xs text-gray-500 mb-1">Last Interaction</p>
                      <p className="text-sm text-gray-400">{context.lastInteraction}</p>
                    </div>
                  </>
                ) : null;
              })()}
            </div>
          )}

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg, idx) => {
              const isMe = (msg.senderId || msg.fromId) === currentUser.id;
              const mime = msg.mimeType || '';
              const isImage = mime.startsWith('image/') || (msg.mediaUrl || '').match(/\.(png|jpe?g|gif|webp)$/i);
              const isVideo = mime.startsWith('video/') || (msg.mediaUrl || '').match(/\.(mp4|webm|mov|avi)$/i);
              return (
                <div key={msg.id || idx} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs px-4 py-2 rounded-2xl ${
                    isMe ? 'bg-cyan-400 text-black' : 'glass-card'
                  } ${msg.sending ? 'opacity-50' : ''}`}>
                    {msg.mediaUrl && (
                      <div className="mb-2">
                        {isImage ? (
                          <img 
                            src={msg.mediaUrl} 
                            alt="Shared media" 
                            className="max-w-full h-auto rounded-lg"
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                          />
                        ) : isVideo ? (
                          <video 
                            src={msg.mediaUrl} 
                            controls 
                            className="max-w-full h-auto rounded-lg"
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                          />
                        ) : null}
                      </div>
                    )}
                    {msg.text && <p className="text-sm">{msg.text}</p>}
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-xs ${isMe ? 'text-black/70' : 'text-gray-500'}`}>
                        {new Date(msg.createdAt).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      {msg.sending && (
                        <div className="w-3 h-3 border-2 border-black/30 border-t-black/70 rounded-full animate-spin"></div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="glass-surface p-4">
            <div className="flex items-center gap-2">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept="image/*,video/*"
                className="hidden"
              />
              <button 
                type="button" 
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="w-10 h-10 rounded-full flex items-center justify-center text-gray-400 hover:text-cyan-400 disabled:opacity-50"
              >
                <ImageIcon size={20} />
              </button>
              <input
                type="text"
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 bg-gray-900 border border-gray-700 rounded-full px-4 py-2"
                data-testid="message-input"
              />
              <button type="submit" disabled={!messageText.trim() || uploading} className="w-10 h-10 rounded-full bg-cyan-400 flex items-center justify-center text-black disabled:opacity-50">
                {uploading ? (
                  <div className="animate-spin w-4 h-4 border-2 border-black border-t-transparent rounded-full"></div>
                ) : (
                  <Send size={18} />
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default Messenger;