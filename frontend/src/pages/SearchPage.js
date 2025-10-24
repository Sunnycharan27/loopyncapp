import React, { useState } from "react";
import axios from "axios";
import { API } from "../App";
import { Search, User, Hash, Calendar, MapPin } from "lucide-react";
import { useNavigate } from "react-router-dom";
import TopHeader from "../components/TopHeader";
import BottomNav from "../components/BottomNav";

const SearchPage = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState({});
  const [activeTab, setActiveTab] = useState("all");
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await axios.get(`${API}/search/all?q=${encodeURIComponent(query)}&type=${activeTab}`);
      setResults(res.data);
    } catch (error) {
      console.error("Search failed");
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: "all", label: "All", icon: <Search size={16} /> },
    { id: "users", label: "Users", icon: <User size={16} /> },
    { id: "posts", label: "Posts", icon: <Hash size={16} /> },
    { id: "events", label: "Events", icon: <Calendar size={16} /> },
    { id: "venues", label: "Venues", icon: <MapPin size={16} /> }
  ];

  return (
    <div className="min-h-screen pb-24 dark:bg-gradient-to-b dark:from-gray-900 dark:to-black light:bg-gray-50">
      <TopHeader title="Search" subtitle="Find anything on Loopync" />

      <div className="p-4">
        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-4">
          <div className="relative">
            <Search className="absolute left-4 top-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search users, posts, events..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700 text-white focus:outline-none focus:border-cyan-400 dark:bg-gray-800/50 dark:border-gray-700 light:bg-white light:border-gray-300 light:text-black"
            />
          </div>
        </form>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? "bg-cyan-400 text-black"
                  : "bg-gray-800/50 text-gray-400 hover:bg-gray-700/50 dark:bg-gray-800/50 light:bg-gray-200"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Results */}
        {loading ? (
          <div className="text-center py-12 text-gray-400">Searching...</div>
        ) : (
          <div className="space-y-6">
            {/* Users */}
            {results.users && results.users.length > 0 && (
              <div>
                <h3 className="text-white font-semibold mb-3 dark:text-white light:text-black">Users</h3>
                <div className="space-y-2">
                  {results.users.map(user => (
                    <div
                      key={user.id}
                      onClick={() => navigate(`/profile/${user.id}`)}
                      className="flex items-center gap-3 p-3 rounded-xl bg-gray-800/30 hover:bg-gray-700/50 cursor-pointer transition-all dark:bg-gray-800/30 light:bg-white"
                    >
                      <img src={user.avatar} alt={user.name} className="w-12 h-12 rounded-full" />
                      <div>
                        <p className="font-semibold text-white dark:text-white light:text-black">{user.name}</p>
                        <p className="text-sm text-gray-400">@{user.handle}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Posts */}
            {results.posts && results.posts.length > 0 && (
              <div>
                <h3 className="text-white font-semibold mb-3 dark:text-white light:text-black">Posts</h3>
                <div className="space-y-3">
                  {results.posts.map(post => (
                    <div key={post.id} className="glass-card p-4 dark:bg-gray-800/30 light:bg-white">
                      <div className="flex items-center gap-2 mb-2">
                        <img src={post.author?.avatar} alt={post.author?.name} className="w-8 h-8 rounded-full" />
                        <span className="font-semibold text-white dark:text-white light:text-black">{post.author?.name}</span>
                      </div>
                      <p className="text-gray-300 dark:text-gray-300 light:text-gray-700">{post.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Events */}
            {results.events && results.events.length > 0 && (
              <div>
                <h3 className="text-white font-semibold mb-3 dark:text-white light:text-black">Events</h3>
                <div className="space-y-2">
                  {results.events.map(event => (
                    <div
                      key={event.id}
                      onClick={() => navigate(`/events/${event.id}`)}
                      className="flex gap-3 p-3 rounded-xl bg-gray-800/30 hover:bg-gray-700/50 cursor-pointer transition-all dark:bg-gray-800/30 light:bg-white"
                    >
                      <img src={event.image} alt={event.name} className="w-16 h-16 rounded-xl object-cover" />
                      <div>
                        <p className="font-semibold text-white dark:text-white light:text-black">{event.name}</p>
                        <p className="text-sm text-gray-400">{event.location}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <BottomNav active="discover" />
    </div>
  );
};

export default SearchPage;