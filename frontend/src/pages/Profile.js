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
      const [analyticsRes, creditsRes, ticketsRes, bookmarksRes, walletRes, contentRes] = await Promise.all([
        axios.get(`${API}/analytics/${currentUser.id}`),
        axios.get(`${API}/credits/${currentUser.id}`),
        axios.get(`${API}/tickets/${currentUser.id}`),
        axios.get(`${API}/bookmarks/${currentUser.id}`),
        axios.get(`${API}/wallet?userId=${currentUser.id}`),
        axios.get(`${API}/users/${currentUser.id}/content`)
      ]);

      setAnalytics(analyticsRes.data);
      setCredits(creditsRes.data);
      setTickets(ticketsRes.data);
      setBookmarks(bookmarksRes.data);
      setWalletBalance(walletRes.data.balance || 0);
      setUserContent(contentRes.data);
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
              onClick={() => setShowSettings(true)}
              className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:text-white"
              data-testid="profile-settings-btn"
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
          <div className="grid grid-cols-3 gap-3">
            <button
              onClick={() => navigate('/wallet')}
              className="p-4 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 transition-all text-center group"
            >
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                <CreditCard size={20} className="text-white" />
              </div>
              <p className="text-sm font-medium text-white">Wallet</p>
              <p className="text-xs text-gray-500">Payments</p>
            </button>

            <button
              onClick={() => navigate('/settings')}
              className="p-4 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 transition-all text-center group"
            >
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Settings size={20} className="text-white" />
              </div>
              <p className="text-sm font-medium text-white">Settings</p>
              <p className="text-xs text-gray-500">Account</p>
            </button>

            <button
              onClick={() => setActiveTab('tickets')}
              className="p-4 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 transition-all text-center group"
            >
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Ticket size={20} className="text-white" />
              </div>
              <p className="text-sm font-medium text-white">Tickets</p>
              <p className="text-xs text-gray-500">{tickets?.length || 0} active</p>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide">
          {[
            { id: "overview", name: "Overview", icon: <TrendingUp size={16} /> },
            { id: "posts", name: "Posts", icon: <FileText size={16} /> },
            { id: "reels", name: "Reels", icon: <Film size={16} /> },
            { id: "products", name: "Products", icon: <ShoppingBag size={16} /> },
            { id: "analytics", name: "Analytics", icon: <BarChart3 size={16} /> }
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
                <TicketCard key={ticket.id} ticket={ticket} />
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

        {/* Posts Tab */}
        {activeTab === "posts" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">My Posts ({userContent.posts?.length || 0})</h3>
            </div>
            {userContent.posts && userContent.posts.length > 0 ? (
              userContent.posts.map((post) => (
                <div key={post.id} className="glass-card p-4">
                  <div className="mb-3">
                    <p className="text-gray-300">{post.content}</p>
                    <p className="text-xs text-gray-500 mt-2">{new Date(post.createdAt).toLocaleDateString()}</p>
                  </div>
                  {post.media && post.media.length > 0 && (
                    <div className="grid grid-cols-2 gap-2">
                      {post.media.map((url, idx) => (
                        <img key={idx} src={url} alt="Post" className="rounded-lg w-full h-32 object-cover" />
                      ))}
                    </div>
                  )}
                  <div className="flex items-center gap-4 mt-3 text-sm text-gray-400">
                    <span>{post.likes?.length || 0} likes</span>
                    <span>{post.comments?.length || 0} comments</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="glass-card p-12 text-center">
                <FileText size={48} className="text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No posts yet</p>
              </div>
            )}
          </div>
        )}

        {/* Reels Tab */}
        {activeTab === "reels" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">My Reels ({userContent.reels?.length || 0})</h3>
            </div>
            {userContent.reels && userContent.reels.length > 0 ? (
              <div className="grid grid-cols-2 gap-4">
                {userContent.reels.map((reel) => (
                  <div key={reel.id} className="glass-card p-3">
                    <div className="relative rounded-lg overflow-hidden mb-2" style={{ paddingTop: '177.78%' }}>
                      <video
                        src={reel.videoUrl}
                        className="absolute top-0 left-0 w-full h-full object-cover"
                        poster={reel.thumbnail}
                      />
                      <div className="absolute top-2 right-2 px-2 py-1 rounded bg-black/50 text-white text-xs">
                        <Film size={12} className="inline mr-1" />
                        Reel
                      </div>
                    </div>
                    <p className="text-sm text-gray-300 line-clamp-2">{reel.caption}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                      <span>{reel.likes?.length || 0} likes</span>
                      <span>{reel.views || 0} views</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{new Date(reel.createdAt).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="glass-card p-12 text-center">
                <Film size={48} className="text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-4">No reels yet</p>
                <button
                  onClick={() => navigate('/vibezone')}
                  className="px-6 py-2 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold"
                >
                  Create Reel
                </button>
              </div>
            )}
          </div>
        )}

        {/* Products Tab */}
        {activeTab === "products" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">My Products ({userContent.products?.length || 0})</h3>
            </div>
            {userContent.products && userContent.products.length > 0 ? (
              <div className="grid grid-cols-2 gap-4">
                {userContent.products.map((product) => (
                  <div key={product.id} className="glass-card p-3">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-32 object-cover rounded-lg mb-2"
                    />
                    <h4 className="font-semibold text-white text-sm">{product.name}</h4>
                    <p className="text-cyan-400 font-bold">₹{product.price}</p>
                    <p className="text-xs text-gray-500 mt-1">{new Date(product.createdAt).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="glass-card p-12 text-center">
                <ShoppingBag size={48} className="text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-4">No products listed</p>
                <button
                  onClick={() => navigate('/marketplace')}
                  className="px-6 py-2 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold"
                >
                  Visit Marketplace
                </button>
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === "analytics" && (
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">Quick Analytics</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Total Content</span>
                <span className="text-white font-bold">
                  {(userContent.posts?.length || 0) + (userContent.reels?.length || 0) + (userContent.products?.length || 0)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Posts</span>
                <span className="text-white font-bold">{userContent.posts?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Reels</span>
                <span className="text-white font-bold">{userContent.reels?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Products</span>
                <span className="text-white font-bold">{userContent.products?.length || 0}</span>
              </div>
            </div>
            <button
              onClick={() => navigate('/analytics')}
              className="w-full mt-6 py-3 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold"
            >
              View Full Analytics
            </button>
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

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal
          currentUser={currentUser}
          onClose={() => setShowSettings(false)}
          onSave={() => {
            setShowSettings(false);
            fetchProfileData();
          }}
        />
      )}

      <BottomNav active="profile" />
    </div>
  );
};

const SettingsModal = ({ currentUser, onClose, onSave }) => {
  const [name, setName] = useState(currentUser.name || "");
  const [bio, setBio] = useState(currentUser.bio || "");
  const [location, setLocation] = useState(currentUser.location || "");
  const [website, setWebsite] = useState(currentUser.website || "");
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/users/${currentUser.id}/settings`, {
        name,
        bio,
        location,
        website
      });
      toast.success("Profile updated successfully!");
      onSave();
    } catch (error) {
      toast.error("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold neon-text">Edit Profile</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            ✕
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900/50 border-2 border-cyan-400/30 rounded-xl focus:border-cyan-400 focus:outline-none text-white"
              placeholder="Your name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Bio</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900/50 border-2 border-cyan-400/30 rounded-xl focus:border-cyan-400 focus:outline-none text-white resize-none"
              rows={3}
              placeholder="Tell us about yourself"
              maxLength={150}
            />
            <p className="text-xs text-gray-500 mt-1">{bio.length}/150 characters</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Location</label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900/50 border-2 border-cyan-400/30 rounded-xl focus:border-cyan-400 focus:outline-none text-white"
              placeholder="City, Country"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Website</label>
            <input
              type="url"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900/50 border-2 border-cyan-400/30 rounded-xl focus:border-cyan-400 focus:outline-none text-white"
              placeholder="https://yourwebsite.com"
            />
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-full border-2 border-gray-600 text-gray-300 font-semibold hover:bg-gray-800/50"
            disabled={saving}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 py-3 rounded-full text-white font-semibold bg-gradient-to-r from-cyan-400 to-purple-500 hover:opacity-90 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;