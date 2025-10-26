import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { Settings, Grid, Film, Bookmark, UserPlus, MessageCircle, Sun, Moon, LogOut } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const ProfileNew = () => {
  const { currentUser, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("posts");
  const [userPosts, setUserPosts] = useState([]);
  const [userReels, setUserReels] = useState([]);
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [stats, setStats] = useState({ posts: 0, followers: 0, following: 0 });

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      setIsDarkMode(false);
      document.documentElement.classList.remove('dark');
    } else {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    }
    
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      
      // Fetch user's posts
      const postsRes = await axios.get(`${API}/posts`);
      const myPosts = postsRes.data.filter(post => post.authorId === currentUser.id);
      
      // Fetch user's reels
      const reelsRes = await axios.get(`${API}/reels`);
      const myReels = reelsRes.data.filter(reel => reel.authorId === currentUser.id);
      
      // Fetch bookmarks
      try {
        const bookmarksRes = await axios.get(`${API}/bookmarks/${currentUser.id}`);
        setBookmarks(bookmarksRes.data || []);
      } catch (err) {
        setBookmarks([]);
      }

      // Get user data for follower counts
      const userRes = await axios.get(`${API}/users/${currentUser.id}`);
      const userData = userRes.data;
      
      setUserPosts(myPosts);
      setUserReels(myReels);
      setStats({
        posts: myPosts.length,
        followers: userData.friends?.length || 0,
        following: userData.friends?.length || 0
      });
      
    } catch (error) {
      console.error("Failed to fetch profile data:", error);
      toast.error("Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    
    if (newMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
    
    toast.success(`${newMode ? 'Dark' : 'Light'} mode enabled`);
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-black dark:text-white transition-colors duration-300">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <h1 className="text-xl font-semibold">{currentUser.handle}</h1>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {isDarkMode ? <Sun size={24} /> : <Moon size={24} />}
            </button>
            <button
              onClick={() => navigate("/settings")}
              className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <Settings size={24} />
            </button>
            <button
              onClick={handleLogout}
              className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <LogOut size={24} />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Profile Info */}
        <div className="flex items-start gap-6 mb-8">
          {/* Profile Picture */}
          <div className="w-20 h-20 sm:w-32 sm:h-32 rounded-full overflow-hidden flex-shrink-0 border-2 border-gray-200 dark:border-gray-700">
            <img
              src={currentUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser.name}`}
              alt={currentUser.name}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Stats and Actions */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-semibold">{currentUser.name}</h2>
            </div>

            {/* Stats */}
            <div className="flex gap-8 mb-4">
              <div className="text-center">
                <div className="text-xl font-semibold">{stats.posts}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">posts</div>
              </div>
              <div className="text-center cursor-pointer" onClick={() => navigate("/followers")}>
                <div className="text-xl font-semibold">{stats.followers}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">followers</div>
              </div>
              <div className="text-center cursor-pointer" onClick={() => navigate("/following")}>
                <div className="text-xl font-semibold">{stats.following}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">following</div>
              </div>
            </div>

            {/* Bio */}
            {currentUser.bio && (
              <p className="text-sm mb-4 text-gray-700 dark:text-gray-300">{currentUser.bio}</p>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => navigate("/settings")}
                className="flex-1 px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 font-semibold text-sm transition-colors"
              >
                Edit Profile
              </button>
              <button
                onClick={() => navigate("/discover?tab=people")}
                className="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                <UserPlus size={20} />
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-t border-gray-200 dark:border-gray-700">
          <div className="flex justify-around">
            <button
              onClick={() => setActiveTab("posts")}
              className={`flex items-center gap-2 py-3 px-4 border-t-2 transition-colors ${
                activeTab === "posts"
                  ? "border-black dark:border-white"
                  : "border-transparent text-gray-500 dark:text-gray-400"
              }`}
            >
              <Grid size={20} />
              <span className="hidden sm:inline font-semibold">POSTS</span>
            </button>
            <button
              onClick={() => setActiveTab("reels")}
              className={`flex items-center gap-2 py-3 px-4 border-t-2 transition-colors ${
                activeTab === "reels"
                  ? "border-black dark:border-white"
                  : "border-transparent text-gray-500 dark:text-gray-400"
              }`}
            >
              <Film size={20} />
              <span className="hidden sm:inline font-semibold">REELS</span>
            </button>
            <button
              onClick={() => setActiveTab("saved")}
              className={`flex items-center gap-2 py-3 px-4 border-t-2 transition-colors ${
                activeTab === "saved"
                  ? "border-black dark:border-white"
                  : "border-transparent text-gray-500 dark:text-gray-400"
              }`}
            >
              <Bookmark size={20} />
              <span className="hidden sm:inline font-semibold">SAVED</span>
            </button>
          </div>
        </div>

        {/* Content Grid */}
        <div className="mt-4">
          {activeTab === "posts" && (
            <div className="grid grid-cols-3 gap-1">
              {userPosts.length > 0 ? (
                userPosts.map((post) => (
                  <div
                    key={post.id}
                    className="aspect-square bg-gray-200 dark:bg-gray-800 cursor-pointer hover:opacity-75 transition-opacity overflow-hidden"
                    onClick={() => navigate(`/post/${post.id}`)}
                  >
                    {post.mediaUrl ? (
                      <img
                        src={post.mediaUrl}
                        alt="Post"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center p-4 text-center text-sm text-gray-600 dark:text-gray-400">
                        {post.text?.substring(0, 100)}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="col-span-3 text-center py-12 text-gray-500 dark:text-gray-400">
                  <Grid size={48} className="mx-auto mb-3 opacity-50" />
                  <p>No posts yet</p>
                </div>
              )}
            </div>
          )}

          {activeTab === "reels" && (
            <div className="grid grid-cols-3 gap-1">
              {userReels.length > 0 ? (
                userReels.map((reel) => (
                  <div
                    key={reel.id}
                    className="aspect-[9/16] bg-gray-200 dark:bg-gray-800 cursor-pointer hover:opacity-75 transition-opacity overflow-hidden relative"
                    onClick={() => navigate(`/vibezone?reel=${reel.id}`)}
                  >
                    <video
                      src={reel.videoUrl}
                      className="w-full h-full object-cover"
                      poster={reel.thumbnailUrl}
                    />
                    <div className="absolute bottom-2 left-2 text-white text-sm font-semibold bg-black/50 px-2 py-1 rounded">
                      <Film size={16} className="inline mr-1" />
                      {reel.views || 0}
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-3 text-center py-12 text-gray-500 dark:text-gray-400">
                  <Film size={48} className="mx-auto mb-3 opacity-50" />
                  <p>No reels yet</p>
                </div>
              )}
            </div>
          )}

          {activeTab === "saved" && (
            <div className="grid grid-cols-3 gap-1">
              {bookmarks.length > 0 ? (
                bookmarks.map((item) => (
                  <div
                    key={item.id}
                    className="aspect-square bg-gray-200 dark:bg-gray-800 cursor-pointer hover:opacity-75 transition-opacity overflow-hidden"
                    onClick={() => navigate(`/post/${item.postId}`)}
                  >
                    {item.mediaUrl && (
                      <img
                        src={item.mediaUrl}
                        alt="Saved"
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                ))
              ) : (
                <div className="col-span-3 text-center py-12 text-gray-500 dark:text-gray-400">
                  <Bookmark size={48} className="mx-auto mb-3 opacity-50" />
                  <p>No saved posts yet</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <BottomNav active="profile" />
    </div>
  );
};

export default ProfileNew;
