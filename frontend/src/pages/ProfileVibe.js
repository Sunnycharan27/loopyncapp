import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { 
  Settings, Grid, Film, Users, MapPin, ShoppingBag, Award, TrendingUp,
  MessageCircle, Video, Plus, DollarSign, Star, Zap, Target, Trophy,
  Calendar, Heart, Share2, Edit3, Camera, Map, Store, Gift
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const ProfileVibe = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  
  // State management
  const [activeTab, setActiveTab] = useState("posts");
  const [userPosts, setUserPosts] = useState([]);
  const [userReels, setUserReels] = useState([]);
  const [userTribes, setUserTribes] = useState([]);
  const [venueCheckins, setVenueCheckins] = useState([]);
  const [marketplaceItems, setMarketplaceItems] = useState([]);
  const [vibeScore, setVibeScore] = useState(75);
  const [vibeRank, setVibeRank] = useState("Aurora");
  const [loopCredits, setLoopCredits] = useState(0);
  const [achievements, setAchievements] = useState([]);
  const [mutualFriends, setMutualFriends] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Vibe Matrix Stats
  const [vibeMatrix, setVibeMatrix] = useState({
    posts: 0,
    tribes: 0,
    venues: 0,
    events: 0,
    marketplace: 0
  });

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      
      // Fetch all data in parallel
      const [postsRes, reelsRes, tribesRes, creditsRes] = await Promise.all([
        axios.get(`${API}/posts`),
        axios.get(`${API}/reels`),
        axios.get(`${API}/tribes`),
        axios.get(`${API}/credits/${currentUser.id}`)
      ]);

      const myPosts = postsRes.data.filter(p => p.authorId === currentUser.id);
      const myReels = reelsRes.data.filter(r => r.authorId === currentUser.id);
      const myTribes = tribesRes.data.filter(t => 
        t.members?.includes(currentUser.id) || t.creatorId === currentUser.id
      );

      setUserPosts(myPosts);
      setUserReels(myReels);
      setUserTribes(myTribes);
      setLoopCredits(creditsRes.data?.credits || 0);

      // Calculate Vibe Matrix
      setVibeMatrix({
        posts: myPosts.length,
        tribes: myTribes.length,
        venues: 12, // Mock data
        events: 8,  // Mock data
        marketplace: 3 // Mock data
      });

      // Mock achievements
      setAchievements([
        { id: 1, name: "Top Tribe Creator", icon: "👑", unlocked: true },
        { id: 2, name: "Venue Hopper", icon: "🗺️", unlocked: true },
        { id: 3, name: "Trendsetter", icon: "⚡", unlocked: false },
        { id: 4, name: "Social Butterfly", icon: "🦋", unlocked: true }
      ]);

      // Get mutual friends
      const userData = await axios.get(`${API}/users/${currentUser.id}`);
      if (userData.data.friends) {
        const friendsData = await Promise.all(
          userData.data.friends.slice(0, 6).map(friendId =>
            axios.get(`${API}/users/${friendId}`)
          )
        );
        setMutualFriends(friendsData.map(res => res.data));
      }

    } catch (error) {
      console.error("Failed to fetch profile data:", error);
      toast.error("Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0F021E] via-purple-900 to-blue-900 flex items-center justify-center">
        <div className="relative">
          <div className="w-20 h-20 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <div className="absolute inset-0 w-20 h-20 border-4 border-pink-400 border-b-transparent rounded-full animate-spin" style={{ animationDirection: 'reverse' }}></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F021E] via-purple-900 to-blue-900 text-white overflow-hidden relative">
      {/* Animated Background Particles */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-cyan-400 rounded-full animate-float opacity-30"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${5 + Math.random() * 10}s`
            }}
          />
        ))}
      </div>

      <div className="relative z-10 pb-24">
        {/* 1. Header - Vibe Identity Capsule */}
        <div className="relative h-80 overflow-hidden">
          {/* Gradient Background with Aurora Effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/30 via-purple-500/30 to-pink-500/30 animate-gradient"></div>
          
          {/* Glass Card Container */}
          <div className="relative h-full flex flex-col items-center justify-center p-6">
            {/* Top Right Actions */}
            <div className="absolute top-4 right-4 flex gap-2">
              <button
                onClick={() => navigate("/settings")}
                className="p-3 rounded-full bg-white/10 backdrop-blur-xl border border-white/20 hover:bg-white/20 transition-all"
              >
                <Settings size={20} />
              </button>
              <button
                onClick={() => navigate("/edit-profile")}
                className="p-3 rounded-full bg-white/10 backdrop-blur-xl border border-white/20 hover:bg-white/20 transition-all"
              >
                <Edit3 size={20} />
              </button>
            </div>

            {/* Loop Credits Badge */}
            <div className="absolute top-4 left-4 px-4 py-2 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center gap-2 shadow-lg">
              <Zap size={16} className="text-white" />
              <span className="font-bold text-white">{loopCredits}</span>
              <span className="text-xs text-white/80">Credits</span>
            </div>

            {/* Avatar with Holographic Ring */}
            <div className="relative mb-4">
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-400 via-pink-400 to-purple-400 animate-spin-slow p-1"></div>
              <div className="relative w-32 h-32 rounded-full border-4 border-white/20 overflow-hidden bg-gray-800">
                <img
                  src={currentUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser.name}`}
                  alt={currentUser.name}
                  className="w-full h-full object-cover"
                />
              </div>
              {/* Activity Pulse */}
              <div className="absolute -bottom-2 -right-2 w-10 h-10 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 flex items-center justify-center border-4 border-[#0F021E] animate-pulse">
                <Zap size={16} className="text-white" />
              </div>
            </div>

            {/* User Info */}
            <h1 className="text-3xl font-bold mb-1">{currentUser.name}</h1>
            <p className="text-cyan-400 mb-2">@{currentUser.handle}</p>
            {currentUser.bio && (
              <p className="text-white/80 text-sm max-w-md text-center mb-3">{currentUser.bio}</p>
            )}

            {/* Vibe Rank Badge */}
            <div className="px-6 py-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 shadow-lg">
              <span className="font-bold text-white">{vibeRank} Rank</span>
            </div>
          </div>
        </div>

        {/* 2. Vibe Matrix - AI Activity Map */}
        <div className="px-4 py-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Target className="text-cyan-400" />
            Vibe Matrix
          </h2>
          <div className="glass-card p-6 rounded-[32px] backdrop-blur-xl bg-white/5 border border-white/10">
            <div className="grid grid-cols-5 gap-4">
              {[
                { label: "Posts", value: vibeMatrix.posts, icon: Grid, color: "from-cyan-400 to-blue-500" },
                { label: "Tribes", value: vibeMatrix.tribes, icon: Users, color: "from-purple-400 to-pink-500" },
                { label: "Venues", value: vibeMatrix.venues, icon: MapPin, color: "from-green-400 to-emerald-500" },
                { label: "Events", value: vibeMatrix.events, icon: Calendar, color: "from-yellow-400 to-orange-500" },
                { label: "Market", value: vibeMatrix.marketplace, icon: ShoppingBag, color: "from-pink-400 to-rose-500" }
              ].map((item, idx) => (
                <button
                  key={idx}
                  className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-white/5 hover:bg-white/10 transition-all border border-white/10 hover:border-white/20"
                >
                  <div className={`w-12 h-12 rounded-full bg-gradient-to-r ${item.color} flex items-center justify-center shadow-lg`}>
                    <item.icon size={20} className="text-white" />
                  </div>
                  <span className="text-2xl font-bold">{item.value}</span>
                  <span className="text-xs text-white/60">{item.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 3. Scroll Tabs - Four Dimensions */}
        <div className="px-4 mb-4">
          <div className="flex gap-2 overflow-x-auto hide-scrollbar">
            {[
              { id: "posts", label: "Posts", icon: Grid },
              { id: "tribes", label: "Tribes", icon: Users },
              { id: "venues", label: "Venues", icon: Map },
              { id: "marketplace", label: "Market", icon: Store }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 rounded-full font-semibold whitespace-nowrap transition-all ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-cyan-400 to-blue-500 text-white shadow-lg'
                    : 'bg-white/10 text-white/60 hover:bg-white/20'
                }`}
              >
                <tab.icon size={18} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="px-4">
          {/* Posts Tab */}
          {activeTab === "posts" && (
            <div className="grid grid-cols-3 gap-1">
              {userPosts.length > 0 ? (
                userPosts.map((post) => (
                  <div
                    key={post.id}
                    className="aspect-square rounded-lg overflow-hidden cursor-pointer hover:opacity-75 transition-all border border-white/10 hover:border-cyan-400"
                    onClick={() => navigate(`/post/${post.id}`)}
                  >
                    {post.mediaUrl ? (
                      <img
                        src={post.mediaUrl}
                        alt="Post"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center p-3">
                        <p className="text-xs text-center text-white/80 line-clamp-4">
                          {post.text}
                        </p>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="col-span-3 glass-card p-12 rounded-2xl text-center">
                  <Grid size={48} className="mx-auto mb-4 text-white/30" />
                  <p className="text-white/60">No posts yet</p>
                  <button className="mt-4 px-6 py-2 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full font-semibold">
                    Create Post
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Tribes Tab */}
          {activeTab === "tribes" && (
            <div className="grid grid-cols-1 gap-4">
              {userTribes.length > 0 ? (
                userTribes.map(tribe => (
                  <div
                    key={tribe.id}
                    className="glass-card p-4 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 hover:border-cyan-400 transition-all cursor-pointer"
                    onClick={() => navigate(`/tribe/${tribe.id}`)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-r from-purple-400 to-pink-500 flex items-center justify-center">
                        <Users size={24} className="text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-bold text-white">{tribe.name}</h3>
                        <p className="text-sm text-white/60">{tribe.members?.length || 0} members</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="glass-card p-12 rounded-2xl text-center">
                  <Users size={48} className="mx-auto mb-4 text-white/30" />
                  <p className="text-white/60">No tribes joined yet</p>
                </div>
              )}
            </div>
          )}

          {/* Venues Tab */}
          {activeTab === "venues" && (
            <div className="glass-card p-6 rounded-2xl text-center">
              <Map size={48} className="mx-auto mb-4 text-cyan-400" />
              <h3 className="text-xl font-bold mb-2">Venue Check-ins</h3>
              <p className="text-white/60 mb-4">Interactive heatmap coming soon!</p>
              <div className="w-full h-64 bg-white/5 rounded-xl border border-white/10"></div>
            </div>
          )}

          {/* Marketplace Tab */}
          {activeTab === "marketplace" && (
            <div className="glass-card p-12 rounded-2xl text-center">
              <Store size={48} className="mx-auto mb-4 text-pink-400" />
              <p className="text-white/60">No marketplace items yet</p>
            </div>
          )}
        </div>

        {/* 4. Social Layer - Vibe Circle */}
        {mutualFriends.length > 0 && (
          <div className="px-4 py-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Heart className="text-pink-400" />
              Vibe Circle
            </h2>
            <div className="flex gap-3 overflow-x-auto hide-scrollbar">
              {mutualFriends.map(friend => (
                <div
                  key={friend.id}
                  className="flex flex-col items-center gap-2 cursor-pointer hover:scale-105 transition-transform"
                  onClick={() => navigate(`/profile/${friend.id}`)}
                >
                  <div className="w-16 h-16 rounded-full border-2 border-cyan-400 overflow-hidden">
                    <img
                      src={friend.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${friend.name}`}
                      alt={friend.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <span className="text-xs text-white/80">{friend.name.split(' ')[0]}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 5. Achievements & Gamification */}
        <div className="px-4 py-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Trophy className="text-yellow-400" />
            Loop Badges
          </h2>
          <div className="grid grid-cols-2 gap-4">
            {achievements.map(achievement => (
              <div
                key={achievement.id}
                className={`glass-card p-4 rounded-2xl text-center ${
                  achievement.unlocked
                    ? 'bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border-yellow-400/50'
                    : 'bg-white/5 border-white/10 opacity-50'
                } border backdrop-blur-xl`}
              >
                <div className="text-4xl mb-2">{achievement.icon}</div>
                <p className="text-sm font-semibold">{achievement.name}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 7. Floating Action Bar */}
      <div className="fixed bottom-20 right-4 flex flex-col gap-3 z-50">
        {[
          { icon: Camera, color: "from-pink-400 to-rose-500", label: "Capsule" },
          { icon: Plus, color: "from-cyan-400 to-blue-500", label: "Post" },
          { icon: MessageCircle, color: "from-purple-400 to-pink-500", label: "Message" },
          { icon: MapPin, color: "from-green-400 to-emerald-500", label: "Check-in" },
          { icon: Gift, color: "from-yellow-400 to-orange-500", label: "Redeem" }
        ].map((action, idx) => (
          <button
            key={idx}
            className={`w-14 h-14 rounded-full bg-gradient-to-r ${action.color} flex items-center justify-center shadow-2xl hover:scale-110 transition-all active:scale-95`}
            onClick={() => toast.info(`${action.label} coming soon!`)}
          >
            <action.icon size={24} className="text-white" />
          </button>
        ))}
      </div>

      <BottomNav active="profile" />

      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-float {
          animation: float linear infinite;
        }
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 10s ease infinite;
        }
        .animate-spin-slow {
          animation: spin-slow 3s linear infinite;
        }
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        .glass-card {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
      `}</style>
    </div>
  );
};

export default ProfileVibe;
