import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import TopHeader from "../components/TopHeader";
import { Settings, LogOut, Award, TrendingUp, Zap, Calendar, Ticket, Bookmark, Trophy, Wallet, CreditCard, ArrowRight, Edit, Film, ShoppingBag, FileText, BarChart3 } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const Profile = () => {
  const { currentUser, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("overview");
  const [analytics, setAnalytics] = useState(null);
  const [credits, setCredits] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [bookmarks, setBookmarks] = useState([]);
  const [walletBalance, setWalletBalance] = useState(0);
  const [userContent, setUserContent] = useState({ posts: [], reels: [], products: [] });
  const [showSettings, setShowSettings] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      const [analyticsRes, creditsRes, ticketsRes, bookmarksRes, walletRes] = await Promise.all([
        axios.get(`${API}/analytics/${currentUser.id}`),
        axios.get(`${API}/credits/${currentUser.id}`),
        axios.get(`${API}/tickets/${currentUser.id}`),
        axios.get(`${API}/bookmarks/${currentUser.id}`),
        axios.get(`${API}/wallet?userId=${currentUser.id}`)
      ]);

      setAnalytics(analyticsRes.data);
      setCredits(creditsRes.data);
      setTickets(ticketsRes.data);
      setBookmarks(bookmarksRes.data);
      setWalletBalance(walletRes.data.balance || 0);
    } catch (error) {
      console.error("Failed to fetch profile data");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  const getTierColor = (tier) => {
    switch(tier) {
      case "Platinum": return "from-purple-400 to-pink-500";
      case "Gold": return "from-yellow-400 to-orange-500";
      case "Silver": return "from-gray-400 to-gray-500";
      default: return "from-orange-600 to-orange-800";
    }
  };

  const getTierEmoji = (tier) => {
    switch(tier) {
      case "Platinum": return "💎";
      case "Gold": return "🏆";
      case "Silver": return "🥈";
      default: return "🥉";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <TopHeader title="Profile" subtitle={`@${currentUser.handle}`} />

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Profile Header */}
        <div className="glass-card p-6 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="relative">
              <img
                src={currentUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser.handle}`}
                alt={currentUser.name}
                className="w-20 h-20 rounded-full border-4 border-cyan-400"
              />
              <div className="absolute -bottom-2 -right-2 text-3xl">
                {getTierEmoji(analytics?.tier || "Bronze")}
              </div>
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white neon-text">{currentUser.name}</h2>
              <p className="text-gray-400">@{currentUser.handle}</p>
              <div className="mt-2">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r ${getTierColor(analytics?.tier || "Bronze")} text-white`}>
                  {analytics?.tier || "Bronze"} Tier
                </span>
              </div>
            </div>
            <button
              onClick={() => navigate('/settings')}
              className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:text-white"
            >
              <Settings size={20} />
            </button>
          </div>

          {/* Credits & Wallet Section */}
          <div className="grid grid-cols-2 gap-3">
            {/* Loop Credits Card */}
            <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-400/10 to-purple-400/10 border border-cyan-400/30">
              <div className="flex items-center gap-2 mb-2">
                <Zap size={16} className="text-cyan-400" />
                <p className="text-gray-400 text-xs">Loop Credits</p>
              </div>
              <p className="text-2xl font-bold text-cyan-400 mb-1">{credits?.balance || 0}</p>
              <p className="text-xs text-gray-500">Reward points</p>
            </div>

            {/* LoopPay Wallet Card */}
            <button
              onClick={() => navigate('/wallet')}
              className="p-4 rounded-xl bg-gradient-to-br from-green-400/10 to-emerald-400/10 border border-green-400/30 hover:border-green-400/50 transition-all text-left group"
            >
              <div className="flex items-center gap-2 mb-2">
                <Wallet size={16} className="text-green-400" />
                <p className="text-gray-400 text-xs">LoopPay Wallet</p>
              </div>
              <p className="text-2xl font-bold text-green-400 mb-1">₹{walletBalance.toFixed(2)}</p>
              <div className="flex items-center gap-1 text-xs text-green-400 group-hover:gap-2 transition-all">
                <span>Open Wallet</span>
                <ArrowRight size={12} />
              </div>
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="glass-card p-4 mb-6">
          <h3 className="text-sm font-semibold text-gray-400 mb-3">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => navigate('/wallet')}
              className="p-4 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 transition-all text-center group"
            >
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                <CreditCard size={20} className="text-white" />
              </div>
              <p className="text-sm font-medium text-white">Manage Wallet</p>
              <p className="text-xs text-gray-500">Payments & Top-up</p>
            </button>

            <button
              onClick={() => setActiveTab('tickets')}
              className="p-4 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 transition-all text-center group"
            >
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Ticket size={20} className="text-white" />
              </div>
              <p className="text-sm font-medium text-white">My Tickets</p>
              <p className="text-xs text-gray-500">{tickets?.length || 0} active</p>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide">
          {[
            { id: "overview", name: "Overview", icon: <TrendingUp size={16} /> },
            { id: "tickets", name: "My Tickets", icon: <Ticket size={16} /> },
            { id: "bookmarks", name: "Bookmarks", icon: <Bookmark size={16} /> }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-full font-medium text-sm transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              {tab.icon}
              {tab.name}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="space-y-4">
            {/* Analytics Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="glass-card p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-full bg-cyan-400/20 flex items-center justify-center">
                    <Zap size={20} className="text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Total Posts</p>
                    <p className="text-2xl font-bold text-white">{analytics?.totalPosts || 0}</p>
                  </div>
                </div>
              </div>

              <div className="glass-card p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-full bg-green-400/20 flex items-center justify-center">
                    <Calendar size={20} className="text-green-400" />
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Check-ins</p>
                    <p className="text-2xl font-bold text-white">{analytics?.totalCheckins || 0}</p>
                  </div>
                </div>
              </div>

              <div className="glass-card p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-full bg-purple-400/20 flex items-center justify-center">
                    <Trophy size={20} className="text-purple-400" />
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Challenges</p>
                    <p className="text-2xl font-bold text-white">{analytics?.totalChallengesCompleted || 0}</p>
                  </div>
                </div>
              </div>

              <div className="glass-card p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-full bg-yellow-400/20 flex items-center justify-center">
                    <Award size={20} className="text-yellow-400" />
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">VibeRank</p>
                    <p className="text-2xl font-bold text-white">#{analytics?.vibeRank || '--'}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Credits History */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Recent Credits Activity</h3>
              <div className="space-y-3">
                {credits?.history && credits.history.length > 0 ? (
                  credits.history.slice(0, 5).map((txn) => (
                    <div key={txn.id} className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0">
                      <div>
                        <p className="text-white text-sm font-medium">{txn.description || txn.source}</p>
                        <p className="text-gray-400 text-xs">
                          {new Date(txn.createdAt).toLocaleDateString('en-IN')}
                        </p>
                      </div>
                      <span className={`font-bold ${txn.type === 'earn' ? 'text-green-400' : 'text-red-400'}`}>
                        {txn.type === 'earn' ? '+' : '-'}{txn.amount}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-400 text-center py-4">No activity yet</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tickets Tab */}
        {activeTab === "tickets" && (
          <div className="space-y-4">
            {tickets.length > 0 ? (
              tickets.map((ticket) => (
                <div key={ticket.id} className="glass-card p-4">
                  <div className="flex gap-4">
                    <img
                      src={ticket.event?.image || 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=400'}
                      alt={ticket.event?.name}
                      className="w-20 h-20 rounded-xl object-cover"
                    />
                    <div className="flex-1">
                      <h4 className="font-semibold text-white mb-1">{ticket.event?.name || 'Event'}</h4>
                      <p className="text-sm text-gray-400 mb-2">{ticket.event?.location}</p>
                      <div className="flex items-center gap-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          ticket.status === 'active' 
                            ? 'bg-green-500/20 text-green-400 border border-green-400'
                            : 'bg-gray-700 text-gray-400'
                        }`}>
                          {ticket.status.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-400">{ticket.tier}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="glass-card p-12 text-center">
                <Ticket size={48} className="text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-4">No tickets yet</p>
                <button
                  onClick={() => navigate('/events')}
                  className="px-6 py-2 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold"
                >
                  Browse Events
                </button>
              </div>
            )}
          </div>
        )}

        {/* Bookmarks Tab */}
        {activeTab === "bookmarks" && (
          <div className="space-y-4">
            {bookmarks.length > 0 ? (
              bookmarks.map((post) => (
                <div key={post.id} className="glass-card p-4">
                  <div className="flex items-start gap-3">
                    <img
                      src={post.author?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${post.authorId}`}
                      alt={post.author?.name}
                      className="w-10 h-10 rounded-full"
                    />
                    <div className="flex-1">
                      <p className="font-semibold text-white">{post.author?.name || 'User'}</p>
                      <p className="text-sm text-gray-300 mt-1">{post.text}</p>
                      {post.media && (
                        <img src={post.media} alt="Post" className="mt-2 rounded-xl max-h-64 object-cover" />
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="glass-card p-12 text-center">
                <Bookmark size={48} className="text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No bookmarks yet</p>
              </div>
            )}
          </div>
        )}

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="w-full mt-6 py-3 rounded-full border-2 border-red-500/30 text-red-400 font-semibold hover:bg-red-500/10 flex items-center justify-center gap-2"
        >
          <LogOut size={20} />
          Logout
        </button>
      </div>

      <BottomNav active="profile" />
    </div>
  );
};

export default Profile;