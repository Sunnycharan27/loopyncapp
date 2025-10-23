import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import TopHeader from "../components/TopHeader";
import { TrendingUp, Users, Activity, Wallet, Shield, Heart, MessageCircle, Eye, Share2, Award, BarChart3 } from "lucide-react";
import { toast } from "sonner";

const Analytics = () => {
  const { currentUser } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState("user");
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState({});

  const tabs = [
    { id: "user", name: "My Analytics", icon: <Activity size={16} /> },
    { id: "creator", name: "Creator", icon: <TrendingUp size={16} /> },
    { id: "wallet", name: "Wallet", icon: <Wallet size={16} /> },
    { id: "admin", name: "Platform", icon: <Shield size={16} /> },
  ];

  useEffect(() => {
    fetchAnalytics();
  }, [activeTab]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      let endpoint = "";
      switch (activeTab) {
        case "user":
          endpoint = `/analytics/${currentUser.id}`;
          break;
        case "creator":
          endpoint = `/analytics/creator/${currentUser.id}`;
          break;
        case "wallet":
          endpoint = `/analytics/wallet/${currentUser.id}`;
          break;
        case "admin":
          endpoint = `/analytics/admin?adminUserId=${currentUser.id}`;
          break;
        default:
          endpoint = `/analytics/${currentUser.id}`;
      }
      const res = await axios.get(`${API}${endpoint}`);
      setAnalytics(res.data);
    } catch (error) {
      toast.error("Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <TopHeader title="Analytics" subtitle="Track your performance" />

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-full font-medium text-sm transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                  : 'glass-card text-gray-400 hover:bg-gray-800/50'
              }`}
            >
              {tab.icon}
              {tab.name}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full mx-auto"></div>
          </div>
        ) : (
          <>
            {activeTab === "user" && <UserAnalytics data={analytics} />}
            {activeTab === "creator" && <CreatorDashboard data={analytics} />}
            {activeTab === "wallet" && <WalletAnalytics data={analytics} />}
            {activeTab === "admin" && <AdminDashboard data={analytics} />}
          </>
        )}
      </div>

      <BottomNav active="profile" />
    </div>
  );
};

const UserAnalytics = ({ data }) => (
  <div className="space-y-4">
    {/* Overview Stats */}
    <div className="grid grid-cols-2 gap-4">
      <StatCard icon={<Activity />} label="Total Posts" value={data.totalPosts || 0} color="cyan" />
      <StatCard icon={<Eye />} label="Total Reels" value={data.totalReels || 0} color="purple" />
      <StatCard icon={<Heart />} label="Total Likes" value={data.totalLikes || 0} color="red" />
      <StatCard icon={<MessageCircle />} label="Total Comments" value={data.totalComments || 0} color="blue" />
    </div>

    {/* Engagement */}
    <div className="glass-card p-6">
      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <TrendingUp size={20} className="text-cyan-400" />
        Engagement Overview
      </h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Followers</span>
          <span className="text-white font-bold">{data.followersCount || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Following</span>
          <span className="text-white font-bold">{data.followingCount || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Engagement Rate</span>
          <span className="text-cyan-400 font-bold">{data.engagementRate || 0}%</span>
        </div>
      </div>
    </div>

    {/* Weekly Activity */}
    <div className="glass-card p-6">
      <h3 className="text-lg font-bold text-white mb-4">Weekly Activity</h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 rounded-xl bg-cyan-400/10 border border-cyan-400/30">
          <p className="text-gray-400 text-sm mb-1">Posts This Week</p>
          <p className="text-2xl font-bold text-cyan-400">{data.weeklyEngagement?.posts || 0}</p>
        </div>
        <div className="p-4 rounded-xl bg-purple-400/10 border border-purple-400/30">
          <p className="text-gray-400 text-sm mb-1">Reels This Week</p>
          <p className="text-2xl font-bold text-purple-400">{data.weeklyEngagement?.reels || 0}</p>
        </div>
        <div className="p-4 rounded-xl bg-green-400/10 border border-green-400/30">
          <p className="text-gray-400 text-sm mb-1">Likes This Week</p>
          <p className="text-2xl font-bold text-green-400">{data.weeklyEngagement?.likes || 0}</p>
        </div>
        <div className="p-4 rounded-xl bg-orange-400/10 border border-orange-400/30">
          <p className="text-gray-400 text-sm mb-1">Comments This Week</p>
          <p className="text-2xl font-bold text-orange-400">{data.weeklyEngagement?.comments || 0}</p>
        </div>
      </div>
    </div>
  </div>
);

const CreatorDashboard = ({ data }) => (
  <div className="space-y-4">
    {/* Reach Stats */}
    <div className="grid grid-cols-2 gap-4">
      <StatCard icon={<Users />} label="Followers" value={data.followersCount || 0} color="cyan" trend={data.followersGrowth} />
      <StatCard icon={<Eye />} label="Total Reach" value={data.totalReach || 0} color="purple" />
    </div>

    {/* Content Performance */}
    <div className="glass-card p-6">
      <h3 className="text-lg font-bold text-white mb-4">Content Breakdown</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Posts</span>
          <span className="text-white font-bold">{data.contentBreakdown?.posts || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Reels</span>
          <span className="text-white font-bold">{data.contentBreakdown?.reels || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Total Engagement</span>
          <span className="text-cyan-400 font-bold">{data.contentBreakdown?.totalEngagement || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Avg Engagement Rate</span>
          <span className="text-cyan-400 font-bold">{data.avgEngagementRate || "0%"}</span>
        </div>
      </div>
    </div>

    {/* Top Content */}
    <div className="glass-card p-6">
      <h3 className="text-lg font-bold text-white mb-4">Top Performing Posts</h3>
      {data.topPosts && data.topPosts.length > 0 ? (
        <div className="space-y-2">
          {data.topPosts.slice(0, 3).map((post, idx) => (
            <div key={idx} className="p-3 rounded-lg bg-gray-800/50 flex items-center justify-between">
              <p className="text-gray-300 text-sm truncate flex-1">{post.content?.substring(0, 50)}...</p>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-red-400 flex items-center gap-1">
                  <Heart size={12} />
                  {post.likes?.length || 0}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-400 py-4">No posts yet</p>
      )}
    </div>
  </div>
);

const WalletAnalytics = ({ data }) => (
  <div className="space-y-4">
    {/* Balance Overview */}
    <div className="glass-card p-6 bg-gradient-to-br from-green-400/10 to-emerald-400/10 border-green-400/30">
      <h3 className="text-sm text-gray-400 mb-2">Current Balance</h3>
      <p className="text-4xl font-bold text-green-400 mb-4">₹{data.currentBalance?.toFixed(2) || "0.00"}</p>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-400 mb-1">Total Added</p>
          <p className="text-white font-bold">₹{data.totalAdded?.toFixed(2) || "0.00"}</p>
        </div>
        <div>
          <p className="text-gray-400 mb-1">Total Spent</p>
          <p className="text-white font-bold">₹{data.totalSpent?.toFixed(2) || "0.00"}</p>
        </div>
      </div>
    </div>

    {/* Credits */}
    <div className="glass-card p-6">
      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <Award size={20} className="text-cyan-400" />
        Loop Credits Earned
      </h3>
      <p className="text-3xl font-bold text-cyan-400">{data.totalCreditsEarned || 0}</p>
      <p className="text-sm text-gray-400 mt-2">From cashbacks and rewards</p>
    </div>

    {/* Spending Breakdown */}
    <div className="glass-card p-6">
      <h3 className="text-lg font-bold text-white mb-4">Spending Breakdown</h3>
      <div className="space-y-3">
        {data.spendingBreakdown && Object.entries(data.spendingBreakdown).map(([category, amount]) => (
          <div key={category} className="flex items-center justify-between">
            <span className="text-gray-400 capitalize">{category}</span>
            <span className="text-white font-bold">₹{amount.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>

    {/* Transaction Stats */}
    <div className="grid grid-cols-2 gap-4">
      <StatCard icon={<BarChart3 />} label="Transactions" value={data.transactionCount || 0} color="blue" />
      <StatCard icon={<TrendingUp />} label="Avg Amount" value={`₹${data.avgTransactionAmount?.toFixed(0) || 0}`} color="purple" />
    </div>
  </div>
);

const AdminDashboard = ({ data }) => (
  <div className="space-y-4">
    {/* Platform Stats */}
    <div className="grid grid-cols-2 gap-4">
      <StatCard icon={<Users />} label="Total Users" value={data.totalUsers || 0} color="cyan" />
      <StatCard icon={<Activity />} label="Active Users" value={data.activeUsers || 0} color="green" />
      <StatCard icon={<MessageCircle />} label="Total Posts" value={data.totalPosts || 0} color="purple" />
      <StatCard icon={<Eye />} label="Total Reels" value={data.totalReels || 0} color="orange" />
    </div>

    {/* Engagement Overview */}
    <div className="glass-card p-6">
      <h3 className="text-lg font-bold text-white mb-4">Platform Engagement</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Total Likes</span>
          <span className="text-white font-bold">{data.totalLikes || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Total Comments</span>
          <span className="text-white font-bold">{data.totalComments || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Engagement Rate</span>
          <span className="text-cyan-400 font-bold">{data.platformEngagementRate || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Growth Rate</span>
          <span className="text-green-400 font-bold">{data.growthRate || "0%"}</span>
        </div>
      </div>
    </div>

    {/* Community Stats */}
    <div className="grid grid-cols-2 gap-4">
      <StatCard icon={<Users />} label="Total Tribes" value={data.totalTribes || 0} color="purple" />
      <StatCard icon={<Activity />} label="Total Rooms" value={data.totalRooms || 0} color="cyan" />
    </div>
  </div>
);

const StatCard = ({ icon, label, value, color, trend }) => {
  const colors = {
    cyan: "from-cyan-400/10 to-cyan-400/5 border-cyan-400/30 text-cyan-400",
    purple: "from-purple-400/10 to-purple-400/5 border-purple-400/30 text-purple-400",
    red: "from-red-400/10 to-red-400/5 border-red-400/30 text-red-400",
    blue: "from-blue-400/10 to-blue-400/5 border-blue-400/30 text-blue-400",
    green: "from-green-400/10 to-green-400/5 border-green-400/30 text-green-400",
    orange: "from-orange-400/10 to-orange-400/5 border-orange-400/30 text-orange-400",
  };

  return (
    <div className={`p-4 rounded-xl bg-gradient-to-br border ${colors[color] || colors.cyan}`}>
      <div className="flex items-center gap-2 mb-2">
        {React.cloneElement(icon, { size: 16 })}
        <p className="text-gray-400 text-xs">{label}</p>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      {trend && <p className="text-xs text-green-400 mt-1">{trend}</p>}
    </div>
  );
};

export default Analytics;
