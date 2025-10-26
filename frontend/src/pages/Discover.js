import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { MapPin, Calendar, Users, Star, ArrowRight, ShoppingBag, DollarSign, Search, X, UserPlus, Sparkles, MessageCircle, Clock, UserCheck } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import FindYourParallel from "../components/FindYourParallel";
import FriendButton from "../components/FriendButton";

const Discover = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [venues, setVenues] = useState([]);
  const [events, setEvents] = useState([]);
  const [creators, setCreators] = useState([]);
  const [tribes, setTribes] = useState([]);
  const [people, setPeople] = useState([]);
  const [friendRequests, setFriendRequests] = useState([]);
  const [activeTab, setActiveTab] = useState("venues");
  const [loading, setLoading] = useState(true);
  const [showParallels, setShowParallels] = useState(false);
  
  // Wallet states
  const [walletBalance, setWalletBalance] = useState(0);
  const [loopCredits, setLoopCredits] = useState(0);
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState("");
  
  // Search states
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [showSearch, setShowSearch] = useState(false);

  useEffect(() => {
    fetchDiscoverData();
  }, []);

  useEffect(() => {
    if (activeTab === 'people') {
      fetchPeople();
    }
  }, [activeTab]);

  const fetchDiscoverData = async () => {
    try {
      const [venuesRes, eventsRes, creatorsRes, tribesRes] = await Promise.all([
        axios.get(`${API}/venues`),
        axios.get(`${API}/events`),
        axios.get(`${API}/creators`),
        axios.get(`${API}/tribes`)
      ]);
      setVenues(venuesRes.data);
      setEvents(eventsRes.data);
      setCreators(creatorsRes.data);
      setTribes(tribesRes.data);
    } catch (error) {
      toast.error("Failed to load discover data");
    } finally {
      setLoading(false);
    }
  };

  const fetchPeople = async () => {
    try {
      setLoading(true);
      // Get all users and filter out current user and friends
      const usersRes = await axios.get(`${API}/users`);
      const requestsRes = await axios.get(`${API}/users/${currentUser.id}/friend-requests`);
      
      const currentFriends = currentUser.friends || [];
      const pendingSent = requestsRes.data.sent?.map(r => r.id) || [];
      const pendingReceived = requestsRes.data.received?.map(r => r.id) || [];
      
      const suggested = usersRes.data.filter(u => 
        u.id !== currentUser.id && 
        !currentFriends.includes(u.id) &&
        !pendingSent.includes(u.id) &&
        !pendingReceived.includes(u.id)
      );
      
      setPeople(suggested);
      setFriendRequests(requestsRes.data.received || []);
    } catch (error) {
      console.error('Failed to fetch people:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRequest = async (userId) => {
    try {
      await axios.post(`${API}/friends/accept?userId=${currentUser.id}&friendId=${userId}`);
      toast.success('Friend request accepted!');
      fetchPeople();
      // Update currentUser friends list
      currentUser.friends = [...(currentUser.friends || []), userId];
    } catch (error) {
      toast.error('Failed to accept request');
    }
  };

  const handleRejectRequest = async (userId) => {
    try {
      await axios.post(`${API}/friends/reject?userId=${currentUser.id}&friendId=${userId}`);
      toast.success('Friend request rejected');
      fetchPeople();
    } catch (error) {
      toast.error('Failed to reject request');
    }
  };

  const handleMessageClick = async (user) => {
    try {
      // Create or get DM thread
      const res = await axios.post(`${API}/dm/threads`, {
        user1Id: currentUser.id,
        user2Id: user.id
      });
      navigate(`/messenger/${res.data.id}`);
    } catch (error) {
      toast.error('Failed to start conversation');
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    
    if (query.length < 2) {
      setSearchResults(null);
      return;
    }

    setSearching(true);
    try {
      const res = await axios.get(`${API}/search?q=${encodeURIComponent(query)}&currentUserId=${currentUser.id}`);
      setSearchResults(res.data);
    } catch (error) {
      toast.error("Search failed");
    } finally {
      setSearching(false);
    }
  };

  const sendFriendRequest = async (toUserId) => {
    try {
      await axios.post(`${API}/friend-requests?fromUserId=${currentUser.id}&toUserId=${toUserId}`);
      toast.success("Friend request sent!");
      
      // Update search results
      if (searchResults) {
        setSearchResults({
          ...searchResults,
          users: searchResults.users.map(u => 
            u.id === toUserId ? { ...u, requestSent: true } : u
          )
        });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to send request");
    }
  };

  const handleJoinLeave = async (tribeId, isMember) => {
    try {
      const endpoint = isMember ? "leave" : "join";
      const res = await axios.post(`${API}/tribes/${tribeId}/${endpoint}?userId=${currentUser.id}`);
      
      setTribes(tribes.map(t => {
        if (t.id === tribeId) {
          const newMembers = isMember
            ? t.members.filter(m => m !== currentUser.id)
            : [...t.members, currentUser.id];
          return { ...t, members: newMembers, memberCount: res.data.memberCount };
        }
        return t;
      }));
      
      toast.success(isMember ? "Left tribe" : "Joined tribe!");
    } catch (error) {
      toast.error("Action failed");
    }
  };

  const handlePurchaseCourse = (course, creator) => {
    toast.success(`Opening payment for ${course.name}...`);
    // TODO: Implement Razorpay payment for courses
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0f021e' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-6xl mx-auto">
        <div className="sticky top-0 z-10 glass-surface p-4 mb-6">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h1 className="text-2xl font-bold neon-text">Discover</h1>
              <p className="text-sm text-gray-400">Explore venues, events, marketplace & tribes</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowParallels(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold hover:opacity-90 transition-all"
              >
                <Sparkles size={18} />
                Find Your Parallel
              </button>
              <button
                onClick={() => setShowSearch(!showSearch)}
                className="w-10 h-10 rounded-full flex items-center justify-center bg-cyan-400/20 text-cyan-400 hover:bg-cyan-400/30 transition-all"
              >
                {showSearch ? <X size={20} /> : <Search size={20} />}
              </button>
            </div>
          </div>

          {/* Search Bar */}
          {showSearch && (
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="Search people, posts, tribes, venues, events..."
                className="w-full px-4 py-3 pl-12 rounded-full bg-gray-800/50 border-2 border-gray-700 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none"
                autoFocus
              />
              <Search size={20} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
              {searching && (
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                  <div className="animate-spin w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full"></div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Search Results */}
        {searchResults && searchQuery.length >= 2 && (
          <div className="px-4 mb-6 space-y-6">
            {/* Users */}
            {searchResults.users.length > 0 && (
              <div>
                <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                  <Users size={20} className="text-cyan-400" />
                  People ({searchResults.users.length})
                </h3>
                <div className="space-y-2">
                  {searchResults.users.map(user => (
                    <div 
                      key={user.id} 
                      className="glass-card p-4 flex items-center justify-between cursor-pointer hover:bg-cyan-400/5 transition-all"
                      onClick={() => navigate(`/profile/${user.id}`)}
                    >
                      <div className="flex items-center gap-3">
                        <img src={user.avatar} alt={user.name} className="w-12 h-12 rounded-full" />
                        <div>
                          <p className="font-semibold text-white">{user.name}</p>
                          <p className="text-sm text-gray-400">@{user.handle}</p>
                        </div>
                      </div>
                      {!user.isFriend && !user.isBlocked && !user.requestSent && user.id !== currentUser.id && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            sendFriendRequest(user.id);
                          }}
                          className="px-4 py-2 rounded-full bg-cyan-400 text-black font-semibold hover:bg-cyan-500 transition-all flex items-center gap-2"
                        >
                          <UserPlus size={16} />
                          Add Friend
                        </button>
                      )}
                      {user.isFriend && (
                        <span className="px-4 py-2 rounded-full bg-green-500/20 text-green-400 font-semibold">Friends</span>
                      )}
                      {user.requestSent && (
                        <span className="px-4 py-2 rounded-full bg-gray-700 text-gray-400 font-semibold">Requested</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Posts */}
            {searchResults.posts.length > 0 && (
              <div>
                <h3 className="text-lg font-bold text-white mb-3">Posts ({searchResults.posts.length})</h3>
                <div className="space-y-2">
                  {searchResults.posts.slice(0, 3).map(post => (
                    <div key={post.id} className="glass-card p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <img src={post.author?.avatar} alt={post.author?.name} className="w-8 h-8 rounded-full" />
                        <span className="font-semibold text-white">{post.author?.name}</span>
                      </div>
                      <p className="text-gray-300 text-sm">{post.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Other Results */}
            {searchResults.tribes.length === 0 && searchResults.venues.length === 0 && searchResults.events.length === 0 && searchResults.users.length === 0 && searchResults.posts.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-400">No results found for "{searchQuery}"</p>
              </div>
            )}
          </div>
        )}

        {/* Tabs */}
        {!searchResults && (
          <>
            <div className="flex gap-2 px-4 mb-6 overflow-x-auto">
              <button
                onClick={() => setActiveTab("venues")}
                className={`px-4 py-3 rounded-full font-semibold whitespace-nowrap transition-all ${
                  activeTab === "venues" ? 'bg-cyan-400 text-black' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
                data-testid="discover-venues-tab"
              >
                Venues
              </button>
              <button
                onClick={() => setActiveTab("events")}
                className={`px-4 py-3 rounded-full font-semibold whitespace-nowrap transition-all ${
                  activeTab === "events" ? 'bg-cyan-400 text-black' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
                data-testid="discover-events-tab"
              >
                Events
              </button>
              <button
                onClick={() => setActiveTab("marketplace")}
                className={`px-4 py-3 rounded-full font-semibold whitespace-nowrap transition-all ${
                  activeTab === "marketplace" ? 'bg-cyan-400 text-black' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
                data-testid="discover-marketplace-tab"
              >
                Marketplace
              </button>
              <button
                onClick={() => setActiveTab("tribes")}
                className={`px-4 py-3 rounded-full font-semibold whitespace-nowrap transition-all ${
                  activeTab === "tribes" ? 'bg-cyan-400 text-black' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
                data-testid="discover-tribes-tab"
              >
                Tribes
              </button>
              <button
                onClick={() => setActiveTab("people")}
                className={`px-4 py-3 rounded-full font-semibold whitespace-nowrap transition-all ${
                  activeTab === "people" ? 'bg-cyan-400 text-black' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
                data-testid="discover-people-tab"
              >
                <Users size={18} className="inline mr-1" />
                People
              </button>
              <button
                onClick={() => setActiveTab("wallet")}
                className={`px-4 py-3 rounded-full font-semibold whitespace-nowrap transition-all ${
                  activeTab === "wallet" ? 'bg-cyan-400 text-black' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
                data-testid="discover-wallet-tab"
              >
                <DollarSign size={18} className="inline mr-1" />
                Wallet
              </button>

            </div>

            {/* Content */}
            <div className="px-4">
          {activeTab === "venues" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {venues.map(venue => (
                <div 
                  key={venue.id} 
                  className="glass-card p-5 cursor-pointer hover:scale-[1.02] transition-transform" 
                  data-testid="venue-card"
                  onClick={() => navigate(`/venues/${venue.id}`)}
                >
                  <div className="flex items-start gap-4">
                    <img src={venue.avatar} alt={venue.name} className="w-20 h-20 rounded-3xl" />
                    <div className="flex-1">
                      <h3 className="font-bold text-lg mb-1">{venue.name}</h3>
                      <p className="text-sm text-gray-400 mb-2">{venue.description}</p>
                      <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                        <MapPin size={14} />
                        <span>{venue.location}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Star size={14} className="text-yellow-400" />
                        <span className="text-sm font-semibold">{venue.rating}</span>
                      </div>
                    </div>
                  </div>
                  <button className="w-full mt-4 py-2 rounded-full bg-cyan-400 text-black font-semibold hover:bg-cyan-300 flex items-center justify-center gap-2">
                    View Menu <ArrowRight size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {activeTab === "events" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {events.map(event => (
                <div key={event.id} className="glass-card overflow-hidden" data-testid="event-card">
                  {event.image && (
                    <img src={event.image} alt={event.name} className="w-full h-48 object-cover" />
                  )}
                  <div className="p-5">
                    <h3 className="font-bold text-lg mb-2">{event.name}</h3>
                    <p className="text-sm text-gray-400 mb-3">{event.description}</p>
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                      <Calendar size={14} />
                      <span>{event.date}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                      <MapPin size={14} />
                      <span>{event.location}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xs text-gray-400">Vibe Meter</span>
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-cyan-400 to-pink-400" style={{ width: `${event.vibeMeter}%` }}></div>
                          </div>
                          <span className="text-sm font-bold text-cyan-400">{event.vibeMeter}%</span>
                        </div>
                      </div>
                      <button 
                        onClick={() => navigate(`/events/${event.id}`)}
                        className="px-4 py-2 rounded-full bg-cyan-400 text-black font-semibold hover:bg-cyan-300"
                      >
                        Get Tickets
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "marketplace" && (
            <div className="space-y-4">
              {creators.map(creator => (
                <div key={creator.id} className="glass-card overflow-hidden" data-testid="marketplace-creator">
                  <div className="p-5 border-b border-gray-800">
                    <div className="flex items-center gap-4 mb-3">
                      <img src={creator.avatar} alt={creator.displayName} className="w-16 h-16 rounded-full" />
                      <div className="flex-1">
                        <h3 className="font-bold text-lg">{creator.displayName}</h3>
                        <p className="text-sm text-gray-400">{creator.bio}</p>
                        <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                          <Users size={12} />
                          <span>{creator.followers.toLocaleString()} followers</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Courses List */}
                  <div className="p-5 space-y-3">
                    {creator.items?.map(item => (
                      <div key={item.id} className="glass-surface p-4 rounded-2xl hover:bg-cyan-400/5 transition-all">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <ShoppingBag size={16} className="text-cyan-400" />
                              <span className="text-xs font-semibold text-cyan-400 uppercase">{item.type}</span>
                            </div>
                            <h4 className="font-bold text-lg mb-1">{item.name}</h4>
                            <p className="text-sm text-gray-400 mb-2">Learn from expert {creator.displayName}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <DollarSign size={20} className="text-green-400" />
                            <span className="text-2xl font-bold text-green-400">₹{item.price}</span>
                          </div>
                          <button
                            onClick={() => handlePurchaseCourse(item, creator)}
                            className="px-6 py-2 rounded-full bg-gradient-to-r from-cyan-400 to-pink-400 text-black font-bold hover:opacity-90 flex items-center gap-2"
                            data-testid="buy-course-btn"
                          >
                            <ShoppingBag size={16} />
                            Buy Now
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "tribes" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {tribes.map(tribe => {
                const isMember = tribe.members?.includes(currentUser?.id);
                return (
                  <div key={tribe.id} className="glass-card p-5 hover:scale-[1.02] transition-transform" data-testid="tribe-card">
                    <div 
                      className="cursor-pointer"
                      onClick={() => navigate(`/tribes/${tribe.id}`)}
                    >
                      <img
                        src={tribe.avatar}
                        alt={tribe.name}
                        className="w-16 h-16 rounded-3xl mb-3"
                      />
                      <h3 className="font-bold text-lg mb-1">{tribe.name}</h3>
                      <p className="text-xs text-gray-400 mb-3 line-clamp-2">{tribe.description}</p>
                      
                      <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
                        <Users size={14} />
                        <span>{tribe.memberCount || 0} members</span>
                      </div>

                      <div className="flex flex-wrap gap-1 mb-3">
                        {tribe.tags?.slice(0, 3).map((tag, idx) => (
                          <span key={idx} className="px-2 py-1 rounded-full text-xs bg-cyan-400/10 text-cyan-400">
                            #{tag}
                          </span>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleJoinLeave(tribe.id, isMember);
                      }}
                      className={`w-full py-2 rounded-full text-sm font-semibold ${
                        isMember
                          ? 'bg-gray-700 text-white hover:bg-gray-600'
                          : 'bg-cyan-400 text-black hover:bg-cyan-300'
                      }`}
                      data-testid="tribe-join-btn"
                    >
                      {isMember ? 'Leave' : 'Join Tribe'}
                    </button>
                  </div>
                );
              })}
            </div>
          )}


          {activeTab === "people" && (
            <div className="space-y-6">
              {/* Search Box for People Tab */}
              <div className="glass-card p-4">
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => handleSearch(e.target.value)}
                    placeholder="Search people by name, handle, or email..."
                    className="w-full px-4 py-3 pl-12 rounded-full bg-gray-800/50 border-2 border-gray-700 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none"
                  />
                  <Search size={20} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  {searching && (
                    <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                      <div className="animate-spin w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full"></div>
                    </div>
                  )}
                </div>
                {searchQuery.length > 0 && searchQuery.length < 2 && (
                  <p className="text-xs text-gray-500 mt-2">Type at least 2 characters to search</p>
                )}
              </div>

              {/* Search Results for People */}
              {searchResults && searchQuery.length >= 2 && searchResults.users && searchResults.users.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Search size={20} className="text-cyan-400" />
                    Search Results ({searchResults.users.length})
                  </h3>
                  <div className="space-y-3">
                    {searchResults.users.map(user => (
                      <div key={user.id} className="glass-card p-4">
                        <div className="flex items-start gap-3">
                          <img
                            src={user.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`}
                            alt={user.name}
                            className="w-16 h-16 rounded-full cursor-pointer"
                            onClick={() => navigate(`/profile/${user.id}`)}
                          />
                          <div className="flex-1">
                            <h3 
                              className="font-semibold text-white cursor-pointer hover:underline"
                              onClick={() => navigate(`/profile/${user.id}`)}
                            >
                              {user.name}
                            </h3>
                            <p className="text-sm text-gray-400">@{user.handle}</p>
                            {user.bio && <p className="text-sm text-gray-300 mt-1">{user.bio}</p>}
                            {user.email && (
                              <p className="text-xs text-gray-500 mt-1">{user.email}</p>
                            )}
                            
                            <div className="flex items-center gap-2 mt-3">
                              {user.id === currentUser.id ? (
                                <span className="px-4 py-2 rounded-full bg-gray-700 text-gray-400 text-sm">You</span>
                              ) : user.isFriend ? (
                                <span className="px-4 py-2 rounded-full bg-green-500/20 text-green-400 font-semibold text-sm flex items-center gap-1">
                                  <UserCheck size={16} />
                                  Friends
                                </span>
                              ) : (
                                <FriendButton currentUser={currentUser} targetUser={user} />
                              )}
                              {user.id !== currentUser.id && (
                                <button
                                  onClick={() => handleMessageClick(user)}
                                  className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-gray-700 text-white hover:bg-gray-600 transition text-sm"
                                >
                                  <MessageCircle size={16} />
                                  Message
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* No Results Message */}
              {searchResults && searchQuery.length >= 2 && searchResults.users && searchResults.users.length === 0 && (
                <div className="glass-card p-8 text-center">
                  <p className="text-gray-400">No users found matching "{searchQuery}"</p>
                  <p className="text-sm text-gray-500 mt-2">Try searching by name, handle (@username), or email</p>
                </div>
              )}

              {/* Friend Requests Section */}
              {(!searchQuery || searchQuery.length < 2) && friendRequests.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Clock size={20} className="text-cyan-400" />
                    Friend Requests ({friendRequests.length})
                  </h3>
                  <div className="space-y-3">
                    {friendRequests.map(user => (
                      <div key={user.id} className="glass-card p-4">
                        <div className="flex items-start gap-3">
                          <img
                            src={user.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`}
                            alt={user.name}
                            className="w-16 h-16 rounded-full cursor-pointer"
                            onClick={() => navigate(`/profile/${user.id}`)}
                          />
                          <div className="flex-1">
                            <h3 
                              className="font-semibold text-white cursor-pointer hover:underline"
                              onClick={() => navigate(`/profile/${user.id}`)}
                            >
                              {user.name}
                            </h3>
                            <p className="text-sm text-gray-400">@{user.handle}</p>
                            {user.bio && <p className="text-sm text-gray-300 mt-1">{user.bio}</p>}
                            
                            <div className="flex items-center gap-2 mt-3">
                              <button
                                onClick={() => handleAcceptRequest(user.id)}
                                className="flex items-center gap-1 px-4 py-2 rounded-full bg-cyan-400 text-black hover:bg-cyan-300 transition font-medium"
                              >
                                <UserCheck size={18} />
                                Accept
                              </button>
                              <button
                                onClick={() => handleRejectRequest(user.id)}
                                className="flex items-center gap-1 px-4 py-2 rounded-full bg-gray-700 text-white hover:bg-gray-600 transition"
                              >
                                <X size={18} />
                                Reject
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* People You May Know */}
              {(!searchQuery || searchQuery.length < 2) && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <UserPlus size={20} className="text-cyan-400" />
                    People You May Know
                  </h3>
                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
                    </div>
                  ) : people.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {people.slice(0, 12).map(user => (
                      <div key={user.id} className="glass-card p-4 hover:bg-gray-800/50 transition-all">
                        <div className="flex items-start gap-3">
                          <img
                            src={user.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`}
                            alt={user.name}
                            className="w-16 h-16 rounded-full cursor-pointer"
                            onClick={() => navigate(`/profile/${user.id}`)}
                          />
                          <div className="flex-1">
                            <h3 
                              className="font-semibold text-white cursor-pointer hover:underline"
                              onClick={() => navigate(`/profile/${user.id}`)}
                            >
                              {user.name}
                            </h3>
                            <p className="text-sm text-gray-400">@{user.handle}</p>
                            {user.bio && <p className="text-sm text-gray-300 mt-1 line-clamp-2">{user.bio}</p>}
                            {user.location && (
                              <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                                <MapPin size={12} />
                                {user.location}
                              </p>
                            )}
                            
                            <div className="flex items-center gap-2 mt-3">
                              <FriendButton currentUser={currentUser} targetUser={user} />
                              <button
                                onClick={() => handleMessageClick(user)}
                                className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-gray-700 text-white hover:bg-gray-600 transition text-sm"
                              >
                                <MessageCircle size={16} />
                                Message
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="glass-card p-8 text-center">
                    <Users size={48} className="mx-auto text-gray-600 mb-3" />
                    <p className="text-gray-400">No new people to discover</p>
                    <p className="text-sm text-gray-500 mt-2">Check back later for suggestions</p>
                  </div>
                )}
                </div>
              )}
            </div>
          )}

        </div>
        </>
        )}
      </div>

      <BottomNav active="discover" />
      
      {/* Find Your Parallel Modal */}
      {showParallels && (
        <FindYourParallel
          currentUser={currentUser}
          onClose={() => setShowParallels(false)}
        />
      )}
    </div>
  );
};

export default Discover;
