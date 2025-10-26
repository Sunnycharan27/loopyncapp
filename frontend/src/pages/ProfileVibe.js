import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { 
  Settings, Grid, Film, Users, MapPin, ShoppingBag, Award, TrendingUp,
  MessageCircle, Video, Plus, DollarSign, Star, Zap, Target, Trophy,
  Calendar, Heart, Share2, Edit3, Camera, Map, Store, Gift, ArrowRight, X, Check, Ticket
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const ProfileVibe = () => {
  const { currentUser, setCurrentUser } = useContext(AuthContext);
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
  
  // Edit states
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState("");
  const [isEditingHandle, setIsEditingHandle] = useState(false);
  const [editedHandle, setEditedHandle] = useState("");
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [uploadingCover, setUploadingCover] = useState(false);
  
  // Refs for file inputs
  const avatarInputRef = useRef(null);
  const coverInputRef = useRef(null);
  
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

  // Handle avatar upload
  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error("Please upload an image file");
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error("Image size should be less than 5MB");
      return;
    }

    setUploadingAvatar(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      // Upload file
      const uploadRes = await axios.post(`${API}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      const avatarUrl = `${API}${uploadRes.data.url}`;

      // Update user profile
      const updateRes = await axios.patch(`${API}/users/${currentUser.id}/profile`, {
        avatar: avatarUrl
      });

      // Update current user in context
      setCurrentUser({ ...currentUser, avatar: avatarUrl });
      toast.success("Profile picture updated!");
    } catch (error) {
      console.error("Failed to upload avatar:", error);
      toast.error("Failed to upload profile picture");
    } finally {
      setUploadingAvatar(false);
    }
  };

  // Handle cover photo upload
  const handleCoverUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error("Please upload an image file");
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Image size should be less than 10MB");
      return;
    }

    setUploadingCover(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      // Upload file
      const uploadRes = await axios.post(`${API}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      const coverUrl = `${API}${uploadRes.data.url}`;

      // Update user profile
      await axios.patch(`${API}/users/${currentUser.id}/profile`, {
        coverPhoto: coverUrl
      });

      // Update current user in context
      setCurrentUser({ ...currentUser, coverPhoto: coverUrl });
      toast.success("Cover photo updated!");
    } catch (error) {
      console.error("Failed to upload cover:", error);
      toast.error("Failed to upload cover photo");
    } finally {
      setUploadingCover(false);
    }
  };

  // Handle name edit
  const handleNameEdit = async () => {
    if (!editedName.trim()) {
      toast.error("Name cannot be empty");
      return;
    }

    try {
      await axios.patch(`${API}/users/${currentUser.id}/profile`, {
        name: editedName
      });

      setCurrentUser({ ...currentUser, name: editedName });
      setIsEditingName(false);
      toast.success("Name updated!");
    } catch (error) {
      console.error("Failed to update name:", error);
      toast.error("Failed to update name");
    }
  };

  // Handle handle edit
  const handleHandleEdit = async () => {
    if (!editedHandle.trim()) {
      toast.error("Handle cannot be empty");
      return;
    }

    // Validate handle format (only alphanumeric and underscore)
    if (!/^[a-zA-Z0-9_]+$/.test(editedHandle)) {
      toast.error("Handle can only contain letters, numbers, and underscores");
      return;
    }

    try {
      await axios.patch(`${API}/users/${currentUser.id}/profile`, {
        handle: editedHandle
      });

      setCurrentUser({ ...currentUser, handle: editedHandle });
      setIsEditingHandle(false);
      toast.success("Handle updated!");
    } catch (error) {
      console.error("Failed to update handle:", error);
      toast.error(error.response?.data?.detail || "Failed to update handle");
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
    <div className="min-h-screen text-white overflow-hidden relative pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="relative z-10">
        {/* 1. Header - Vibe Identity Capsule */}
        <div className="relative overflow-hidden">
          {/* Modern Cover Photo Area */}
          <div className="h-48 bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 relative group">
            {currentUser.coverPhoto ? (
              <img 
                src={currentUser.coverPhoto} 
                alt="Cover" 
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-blue-500/10"></div>
            )}
            
            {/* Cover Photo Upload Button */}
            <input
              type="file"
              ref={coverInputRef}
              onChange={handleCoverUpload}
              accept="image/*"
              className="hidden"
            />
            <button
              onClick={() => coverInputRef.current?.click()}
              disabled={uploadingCover}
              className="absolute inset-0 w-full h-full bg-black/0 group-hover:bg-black/50 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100"
            >
              {uploadingCover ? (
                <div className="animate-spin w-8 h-8 border-4 border-white border-t-transparent rounded-full"></div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <Camera size={32} className="text-white" />
                  <span className="text-white text-sm font-semibold">Change Cover</span>
                </div>
              )}
            </button>
            
            {/* Top Actions */}
            <div className="absolute top-4 right-4 flex gap-2 z-10">
              <button
                onClick={() => navigate("/settings")}
                className="p-2.5 rounded-xl glass-surface hover:bg-cyan-400/10 transition-all"
              >
                <Settings size={20} />
              </button>
            </div>

            {/* Loop Credits Badge */}
            <div className="absolute top-4 left-4 px-4 py-2 rounded-xl glass-surface flex items-center gap-2">
              <Zap size={16} className="text-yellow-400" />
              <span className="font-bold text-white">{loopCredits}</span>
              <span className="text-xs text-gray-400">Credits</span>
            </div>
          </div>

          {/* Profile Info Card */}
          <div className="px-4 -mt-16 relative z-20">
            <div className="glass-card p-6 shadow-xl">
              <div className="flex items-start gap-4">
                {/* Avatar with Upload */}
                <div className="relative flex-shrink-0 group">
                  <div className="w-28 h-28 rounded-2xl border-4 border-gray-800 overflow-hidden bg-gray-700 shadow-lg relative">
                    <img
                      src={currentUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser.name}`}
                      alt={currentUser.name}
                      className="w-full h-full object-cover"
                    />
                    {/* Online Status */}
                    <div className="absolute bottom-2 right-2 w-4 h-4 rounded-full bg-green-400 border-2 border-gray-800"></div>
                    
                    {/* Avatar Upload Overlay */}
                    <input
                      type="file"
                      ref={avatarInputRef}
                      onChange={handleAvatarUpload}
                      accept="image/*"
                      className="hidden"
                    />
                    <button
                      onClick={() => avatarInputRef.current?.click()}
                      disabled={uploadingAvatar}
                      className="absolute inset-0 bg-black/0 group-hover:bg-black/60 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100"
                    >
                      {uploadingAvatar ? (
                        <div className="animate-spin w-6 h-6 border-4 border-white border-t-transparent rounded-full"></div>
                      ) : (
                        <Camera size={24} className="text-white" />
                      )}
                    </button>
                  </div>
                  {/* Vibe Rank Badge */}
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 text-xs font-bold text-white shadow-lg whitespace-nowrap">
                    {vibeRank}
                  </div>
                </div>

                {/* User Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      {/* Editable Name */}
                      {isEditingName ? (
                        <div className="flex items-center gap-2 mb-1">
                          <input
                            type="text"
                            value={editedName}
                            onChange={(e) => setEditedName(e.target.value)}
                            className="text-2xl font-bold text-white bg-gray-800 border border-cyan-400 rounded-lg px-2 py-1 focus:outline-none"
                            autoFocus
                          />
                          <button onClick={handleNameEdit} className="p-1 rounded bg-green-500 hover:bg-green-600">
                            <Check size={20} />
                          </button>
                          <button onClick={() => setIsEditingName(false)} className="p-1 rounded bg-red-500 hover:bg-red-600">
                            <X size={20} />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 mb-1">
                          <h1 className="text-2xl font-bold text-white">{currentUser.name}</h1>
                          <button 
                            onClick={() => {
                              setEditedName(currentUser.name);
                              setIsEditingName(true);
                            }}
                            className="p-1 hover:bg-cyan-400/10 rounded transition-all"
                          >
                            <Edit3 size={16} className="text-cyan-400" />
                          </button>
                        </div>
                      )}
                      
                      {/* Editable Handle */}
                      {isEditingHandle ? (
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-cyan-400">@</span>
                          <input
                            type="text"
                            value={editedHandle}
                            onChange={(e) => setEditedHandle(e.target.value)}
                            className="text-sm text-cyan-400 bg-gray-800 border border-cyan-400 rounded-lg px-2 py-1 focus:outline-none"
                            autoFocus
                          />
                          <button onClick={handleHandleEdit} className="p-1 rounded bg-green-500 hover:bg-green-600">
                            <Check size={16} />
                          </button>
                          <button onClick={() => setIsEditingHandle(false)} className="p-1 rounded bg-red-500 hover:bg-red-600">
                            <X size={16} />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 mb-3">
                          <p className="text-cyan-400 text-sm">@{currentUser.handle}</p>
                          <button 
                            onClick={() => {
                              setEditedHandle(currentUser.handle);
                              setIsEditingHandle(true);
                            }}
                            className="p-1 hover:bg-cyan-400/10 rounded transition-all"
                          >
                            <Edit3 size={12} className="text-cyan-400" />
                          </button>
                        </div>
                      )}
                      
                      {currentUser.bio && (
                        <p className="text-gray-300 text-sm leading-relaxed">{currentUser.bio}</p>
                      )}
                    </div>
                  </div>

                  {/* Stats Row */}
                  <div className="flex items-center gap-6 mt-4">
                    <div className="text-center">
                      <div className="text-xl font-bold text-white">{vibeMatrix.posts}</div>
                      <div className="text-xs text-gray-400">Posts</div>
                    </div>
                    <div className="text-center cursor-pointer hover:text-cyan-400 transition-colors">
                      <div className="text-xl font-bold text-white">{currentUser.friends?.length || 0}</div>
                      <div className="text-xs text-gray-400">Friends</div>
                    </div>
                    <div className="text-center cursor-pointer hover:text-cyan-400 transition-colors">
                      <div className="text-xl font-bold text-white">{vibeMatrix.tribes}</div>
                      <div className="text-xs text-gray-400">Tribes</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold text-cyan-400">{vibeScore}</div>
                      <div className="text-xs text-gray-400">Vibe Score</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 2. Vibe Matrix - AI Activity Map */}
        <div className="px-4 py-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center justify-center">
              <Target size={18} className="text-white" />
            </div>
            Activity Overview
          </h2>
          <div className="grid grid-cols-5 gap-3">
            {[
              { label: "Posts", value: vibeMatrix.posts, icon: Grid, gradient: "from-cyan-400 to-blue-500" },
              { label: "Tribes", value: vibeMatrix.tribes, icon: Users, gradient: "from-purple-400 to-pink-500" },
              { label: "Venues", value: vibeMatrix.venues, icon: MapPin, gradient: "from-green-400 to-emerald-500" },
              { label: "Events", value: vibeMatrix.events, icon: Calendar, gradient: "from-yellow-400 to-orange-500" },
              { label: "Market", value: vibeMatrix.marketplace, icon: ShoppingBag, gradient: "from-pink-400 to-rose-500" }
            ].map((item, idx) => (
              <button
                key={idx}
                className="flex flex-col items-center gap-2 p-4 rounded-xl glass-card hover:bg-cyan-400/5 transition-all"
              >
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-r ${item.gradient} flex items-center justify-center shadow-lg`}>
                  <item.icon size={18} className="text-white" />
                </div>
                <span className="text-2xl font-bold text-white">{item.value}</span>
                <span className="text-xs text-gray-400">{item.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 3. Scroll Tabs - Four Dimensions */}
        <div className="px-4 mb-4">
          <div className="glass-surface rounded-xl p-1 inline-flex gap-1">
            {[
              { id: "posts", label: "Posts", icon: Grid },
              { id: "tribes", label: "Tribes", icon: Users },
              { id: "venues", label: "Venues", icon: Map },
              { id: "marketplace", label: "Market", icon: Store }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-semibold whitespace-nowrap transition-all ${
                  activeTab === tab.id
                    ? 'bg-cyan-400 text-black shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
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
            <div className="grid grid-cols-3 gap-2">
              {userPosts.length > 0 ? (
                userPosts.map((post) => (
                  <div
                    key={post.id}
                    className="aspect-square rounded-xl overflow-hidden cursor-pointer hover:opacity-80 transition-all border border-gray-800 hover:border-cyan-400 group relative"
                    onClick={() => navigate(`/post/${post.id}`)}
                  >
                    {post.mediaUrl ? (
                      <img
                        src={post.mediaUrl}
                        alt="Post"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full glass-card flex items-center justify-center p-3">
                        <p className="text-xs text-center text-gray-400 line-clamp-4">
                          {post.text}
                        </p>
                      </div>
                    )}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-all"></div>
                  </div>
                ))
              ) : (
                <div className="col-span-3 glass-card p-12 text-center">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
                    <Grid size={32} className="text-gray-500" />
                  </div>
                  <p className="text-gray-400 mb-4">No posts yet</p>
                  <button 
                    onClick={() => toast.info("Create post feature coming soon!")}
                    className="px-6 py-2.5 bg-cyan-400 hover:bg-cyan-500 text-black rounded-xl font-semibold transition-all"
                  >
                    Create Your First Post
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Tribes Tab */}
          {activeTab === "tribes" && (
            <div className="grid grid-cols-1 gap-3">
              {userTribes.length > 0 ? (
                userTribes.map(tribe => (
                  <div
                    key={tribe.id}
                    className="glass-card p-4 rounded-xl hover:bg-cyan-400/5 transition-all cursor-pointer group"
                    onClick={() => navigate(`/tribe/${tribe.id}`)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-xl bg-gradient-to-r from-purple-400 to-pink-500 flex items-center justify-center flex-shrink-0">
                        <Users size={24} className="text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-bold text-white group-hover:text-cyan-400 transition-colors">{tribe.name}</h3>
                        <p className="text-sm text-gray-400">{tribe.members?.length || 0} members</p>
                      </div>
                      <div className="text-gray-500 group-hover:text-cyan-400 transition-colors">
                        <ArrowRight size={20} />
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="glass-card p-12 text-center">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
                    <Users size={32} className="text-gray-500" />
                  </div>
                  <p className="text-gray-400">No tribes joined yet</p>
                </div>
              )}
            </div>
          )}

          {/* Venues Tab */}
          {activeTab === "venues" && (
            <div className="glass-card p-8 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-r from-green-400 to-emerald-500 flex items-center justify-center">
                <Map size={32} className="text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-white">Venue Check-ins</h3>
              <p className="text-gray-400 mb-6">Interactive heatmap showing your visited places</p>
              <div className="w-full h-64 bg-gray-900/50 rounded-xl border border-gray-800 flex items-center justify-center">
                <p className="text-gray-500">Map visualization coming soon</p>
              </div>
            </div>
          )}

          {/* Marketplace Tab */}
          {activeTab === "marketplace" && (
            <div className="glass-card p-12 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-r from-pink-400 to-rose-500 flex items-center justify-center">
                <Store size={32} className="text-white" />
              </div>
              <p className="text-gray-400">No marketplace items yet</p>
            </div>
          )}
        </div>

        {/* 4. Social Layer - Vibe Circle */}
        {mutualFriends.length > 0 && (
          <div className="px-4 py-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-pink-400 to-rose-500 flex items-center justify-center">
                <Heart size={18} className="text-white" />
              </div>
              Close Friends
            </h2>
            <div className="flex gap-4 overflow-x-auto hide-scrollbar pb-2">
              {mutualFriends.map(friend => (
                <div
                  key={friend.id}
                  className="flex flex-col items-center gap-2 cursor-pointer hover:scale-105 transition-transform flex-shrink-0"
                  onClick={() => navigate(`/profile/${friend.id}`)}
                >
                  <div className="w-16 h-16 rounded-full border-2 border-cyan-400 overflow-hidden bg-gray-800">
                    <img
                      src={friend.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${friend.name}`}
                      alt={friend.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <span className="text-xs text-gray-400">{friend.name.split(' ')[0]}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 5. Achievements & Gamification */}
        <div className="px-4 py-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center">
              <Trophy size={18} className="text-white" />
            </div>
            Achievements
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {achievements.map(achievement => (
              <div
                key={achievement.id}
                className={`p-4 rounded-xl text-center transition-all ${
                  achievement.unlocked
                    ? 'glass-card border-2 border-yellow-400/30'
                    : 'glass-card opacity-50'
                }`}
              >
                <div className="text-4xl mb-2">{achievement.icon}</div>
                <p className="text-sm font-semibold text-white">{achievement.name}</p>
                {achievement.unlocked && (
                  <p className="text-xs text-yellow-400 mt-1">Unlocked</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 7. Floating Action Bar */}
      <div className="fixed bottom-24 right-4 flex flex-col gap-2 z-40">
        {[
          { icon: Camera, color: "from-pink-400 to-rose-500", label: "Story", action: () => toast.info("Vibe Capsules coming soon!") },
          { icon: Plus, color: "from-cyan-400 to-blue-500", label: "Post", action: () => toast.info("Create post coming soon!") },
          { icon: MessageCircle, color: "from-purple-400 to-pink-500", label: "Chat", action: () => navigate("/messenger") },
          { icon: MapPin, color: "from-green-400 to-emerald-500", label: "Check-in", action: () => navigate("/venues") }
        ].map((action, idx) => (
          <button
            key={idx}
            onClick={action.action}
            className={`w-12 h-12 rounded-full bg-gradient-to-r ${action.color} flex items-center justify-center shadow-lg hover:scale-110 transition-all active:scale-95`}
            title={action.label}
          >
            <action.icon size={20} className="text-white" />
          </button>
        ))}
      </div>

      <BottomNav active="profile" />
    </div>
  );
};

export default ProfileVibe;