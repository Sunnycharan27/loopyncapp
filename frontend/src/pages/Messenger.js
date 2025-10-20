import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { ArrowLeft, Send, Image as ImageIcon, Mic, Users, Shield, Video, FileText, MapPin, Calendar, Music, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const Messenger = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState("");
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showRooms, setShowRooms] = useState(false);
  const [showCircles, setShowCircles] = useState(false);
  const [activeView, setActiveView] = useState("chats"); // chats, rooms, circles
  const fileInputRef = useRef(null);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchThreads();
    
    // Poll for new threads every 10 seconds
    const threadsInterval = setInterval(() => {
      fetchThreads();
    }, 10000);
    
    // Auto-refresh messages every 3 seconds when viewing a thread
    let messagesInterval;
    if (selectedThread) {
      messagesInterval = setInterval(() => {
        fetchMessages(selectedThread.peer.id);
      }, 3000);
    }
    
    return () => {
      clearInterval(threadsInterval);
      if (messagesInterval) clearInterval(messagesInterval);
    };
  }, [selectedThread]);

  // Mock Trust Circles data
  const trustCircles = [
    { id: "c1", name: "Close Friends", members: 5, color: "from-pink-400 to-rose-500", icon: "❤️" },
    { id: "c2", name: "Work Colleagues", members: 12, color: "from-blue-400 to-cyan-500", icon: "💼" },
    { id: "c3", name: "Family", members: 8, color: "from-green-400 to-emerald-500", icon: "🏠" },
  ];

  // Mock Vibe Rooms data
  const vibeRooms = [
    { id: "r1", name: "Music Lovers Hub", members: 234, activeNow: 45, category: "Music", emoji: "🎵" },
    { id: "r2", name: "Fitness Warriors", members: 189, activeNow: 23, category: "Fitness", emoji: "💪" },
    { id: "r3", name: "Tech Talk", members: 456, activeNow: 67, category: "Technology", emoji: "💻" },
    { id: "r4", name: "Foodie Paradise", members: 321, activeNow: 34, category: "Food", emoji: "🍕" },
  ];

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
      const res = await axios.get(`${API}/messages?userId=${currentUser.id}`);
      // Group messages by peer
      const threadMap = {};
      res.data.forEach(msg => {
        const peer = msg.peer;
        if (!threadMap[peer.id]) {
          threadMap[peer.id] = {
            peer,
            lastMessage: msg.text,
            timestamp: msg.createdAt,
            unread: !msg.read && msg.toId === currentUser.id
          };
        }
      });
      setThreads(Object.values(threadMap));
    } catch (error) {
      console.error("Failed to load threads", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (peerId) => {
    try {
      const res = await axios.get(`${API}/messages/thread?userId=${currentUser.id}&peerId=${peerId}`);
      setMessages(res.data);
    } catch (error) {
      console.error("Failed to load messages", error);
    }
  };

  const handleThreadClick = (thread) => {
    setSelectedThread(thread);
    fetchMessages(thread.peer.id);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageText.trim() || !selectedThread) return;

    try {
      const res = await axios.post(`${API}/messages?fromId=${currentUser.id}&toId=${selectedThread.peer.id}`, {
        text: messageText
      });
      setMessageText("");
      // Add new message to local state immediately
      setMessages([...messages, res.data]);
      toast.success("Message sent!");
    } catch (error) {
      toast.error("Failed to send message");
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

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
      
      const mediaUrl = `${BACKEND_URL}${uploadRes.data.url}`;
      
      // Send message with media
      const res = await axios.post(`${API}/messages?fromId=${currentUser.id}&toId=${selectedThread.peer.id}`, {
        text: isVideo ? "📹 Video" : "📷 Photo",
        mediaUrl: mediaUrl,
        mediaType: isVideo ? "video" : "image"
      });
      
      setMessages([...messages, res.data]);
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

            {/* Tabs */}
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
                onClick={() => setActiveView("rooms")}
                className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-full font-medium text-sm transition-all ${
                  activeView === "rooms"
                    ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                    : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
                }`}
              >
                <Users size={16} />
                Vibe Rooms
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
              const isMe = msg.fromId === currentUser.id;
              return (
                <div key={idx} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs px-4 py-2 rounded-2xl ${
                    isMe ? 'bg-cyan-400 text-black' : 'glass-card'
                  }`}>
                    {msg.mediaUrl && (
                      <div className="mb-2">
                        {msg.mediaType === 'image' ? (
                          <img 
                            src={msg.mediaUrl} 
                            alt="Shared media" 
                            className="max-w-full h-auto rounded-lg"
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                          />
                        ) : msg.mediaType === 'video' ? (
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
                    <p className="text-sm">{msg.text}</p>
                    <span className={`text-xs ${isMe ? 'text-black/70' : 'text-gray-500'}`}>
                      {new Date(msg.createdAt).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              );
            })}
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