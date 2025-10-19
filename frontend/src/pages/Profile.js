import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import TopHeader from "../components/TopHeader";
import { LogOut, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

const Profile = () => {
  const { currentUser, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [myPosts, setMyPosts] = useState([]);
  const [myTribes, setMyTribes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const [postsRes, tribesRes] = await Promise.all([
        axios.get(`${API}/posts`),
        axios.get(`${API}/tribes`)
      ]);
      
      const userPosts = postsRes.data.filter(p => p.authorId === currentUser.id);
      const userTribes = tribesRes.data.filter(t => t.members.includes(currentUser.id));
      
      setMyPosts(userPosts);
      setMyTribes(userTribes);
    } catch (error) {
      toast.error("Failed to load profile data");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/auth");
    toast.success("Logged out successfully");
  };

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-2xl mx-auto">
        <TopHeader title="Profile" subtitle="Your digital identity" />
        {/* Profile Header */}
        <div className="glass-surface p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-4">
              <img
                src={currentUser.avatar}
                alt={currentUser.name}
                className="w-20 h-20 rounded-full"
              />
              <div>
                <h1 className="text-2xl font-bold neon-text">{currentUser.name}</h1>
                <p className="text-gray-400">@{currentUser.handle}</p>
                <p className="text-sm text-gray-500 mt-1">{currentUser.bio || "No bio yet"}</p>
              </div>
            </div>
            <button
              data-testid="logout-btn"
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 text-red-400 hover:bg-red-500/20"
            >
              <LogOut size={18} />
              Logout
            </button>
          </div>

          <div className="flex gap-6 text-sm">
            <div>
              <span className="font-bold text-cyan-400">{myPosts.length}</span>
              <span className="text-gray-400 ml-1">Posts</span>
            </div>
            <div>
              <span className="font-bold text-cyan-400">{myTribes.length}</span>
              <span className="text-gray-400 ml-1">Tribes</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="px-4">
          <div className="mb-6">
            <h2 className="text-xl font-bold mb-4">Your Tribes</h2>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mx-auto"></div>
              </div>
            ) : myTribes.length === 0 ? (
              <div className="text-center py-8 glass-card p-6">
                <p className="text-gray-400">You haven't joined any tribes yet</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {myTribes.map(tribe => (
                  <div
                    key={tribe.id}
                    onClick={() => navigate(`/tribes/${tribe.id}`)}
                    className="glass-card p-4 cursor-pointer hover:scale-105 transition-transform"
                  >
                    <img src={tribe.avatar} alt={tribe.name} className="w-12 h-12 rounded-2xl mb-2" />
                    <h3 className="font-semibold text-sm">{tribe.name}</h3>
                    <p className="text-xs text-gray-400">{tribe.memberCount} members</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <h2 className="text-xl font-bold mb-4">Your Posts</h2>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mx-auto"></div>
              </div>
            ) : myPosts.length === 0 ? (
              <div className="text-center py-8 glass-card p-6">
                <p className="text-gray-400">You haven't posted anything yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {myPosts.map(post => (
                  <div key={post.id} className="glass-card p-4">
                    <p className="text-sm mb-2">{post.text}</p>
                    {post.media && (
                      <img src={post.media} alt="Post" className="rounded-2xl w-full" />
                    )}
                    <div className="flex gap-4 mt-3 text-xs text-gray-400">
                      <span>{post.stats.likes} likes</span>
                      <span>{post.stats.reposts} reposts</span>
                      <span>{post.stats.replies} replies</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <BottomNav active="profile" />
    </div>
  );
};

export default Profile;