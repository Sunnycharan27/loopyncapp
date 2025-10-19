import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { ArrowLeft, Send, Image as ImageIcon, Mic } from "lucide-react";
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

  useEffect(() => {
    fetchThreads();
    // Auto-refresh messages every 5 seconds when viewing a thread
    let interval;
    if (selectedThread) {
      interval = setInterval(() => {
        fetchMessages(selectedThread.peer.id);
      }, 5000);
    }
    return () => clearInterval(interval);
  }, [selectedThread]);

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
      await axios.post(`${API}/messages?fromId=${currentUser.id}&toId=${selectedThread.peer.id}`, {
        text: messageText
      });
      setMessageText("");
      fetchMessages(selectedThread.peer.id);
    } catch (error) {
      toast.error("Failed to send message");
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
        // Thread List
        <div className="max-w-2xl mx-auto">
          <div className="sticky top-0 z-10 glass-surface p-4 flex items-center gap-3">
            <button onClick={() => navigate('/')} className="text-cyan-400">
              <ArrowLeft size={24} />
            </button>
            <div>
              <h1 className="text-2xl font-bold neon-text">Messages</h1>
              <p className="text-xs text-gray-400">Your conversations</p>
            </div>
          </div>

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
        </div>
      ) : (
        // Chat View
        <div className="flex flex-col h-screen">
          <div className="glass-surface p-4 flex items-center gap-3">
            <button onClick={() => setSelectedThread(null)} className="text-cyan-400">
              <ArrowLeft size={24} />
            </button>
            <img src={selectedThread.peer.avatar} alt={selectedThread.peer.name} className="w-10 h-10 rounded-full" />
            <div className="flex-1">
              <p className="font-semibold">{selectedThread.peer.name}</p>
              <p className="text-xs text-gray-400">@{selectedThread.peer.handle}</p>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg, idx) => {
              const isMe = msg.fromId === currentUser.id;
              return (
                <div key={idx} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs px-4 py-2 rounded-2xl ${
                    isMe ? 'bg-cyan-400 text-black' : 'glass-card'
                  }`}>
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
              <button type="button" className="w-10 h-10 rounded-full flex items-center justify-center text-gray-400 hover:text-cyan-400">
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
              <button type="submit" disabled={!messageText.trim()} className="w-10 h-10 rounded-full bg-cyan-400 flex items-center justify-center text-black disabled:opacity-50">
                <Send size={18} />
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default Messenger;