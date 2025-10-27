import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { API, AuthContext } from '../App';
import { Search, Users, UserPlus, UserCheck, Clock, X, MessageCircle } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import FriendButton from '../components/FriendButton';

const People = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('suggestions'); // suggestions, all, friends, requests
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [friends, setFriends] = useState([]);
  const [friendRequests, setFriendRequests] = useState([]);
  const [sentRequests, setSentRequests] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'suggestions') {
      fetchSuggestions();
    } else if (activeTab === 'friends') {
      fetchFriends();
    } else if (activeTab === 'requests') {
      fetchFriendRequests();
    }
  }, [activeTab]);

  const fetchSuggestions = async () => {
    try {
      setLoading(true);
      // Get all users and filter out friends
      const usersRes = await axios.get(`${API}/users`);
      const friendsRes = await axios.get(`${API}/users/${currentUser.id}/friend-requests`);
      
      const currentFriends = currentUser.friends || [];
      const pendingSent = friendsRes.data.sent?.map(r => r.id) || [];
      const pendingReceived = friendsRes.data.received?.map(r => r.id) || [];
      
      const suggested = usersRes.data.filter(u => 
        u.id !== currentUser.id && 
        !currentFriends.includes(u.id) &&
        !pendingSent.includes(u.id) &&
        !pendingReceived.includes(u.id)
      ).slice(0, 20);
      
      setSuggestions(suggested);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFriends = async () => {
    try {
      setLoading(true);
      const friendIds = currentUser.friends || [];
      
      if (friendIds.length === 0) {
        setFriends([]);
        setLoading(false);
        return;
      }
      
      // Fetch friend details
      const friendPromises = friendIds.map(id => axios.get(`${API}/users/${id}`).catch(() => null));
      const friendResponses = await Promise.all(friendPromises);
      const friendsData = friendResponses.filter(r => r !== null).map(r => r.data);
      
      setFriends(friendsData);
    } catch (error) {
      console.error('Failed to fetch friends:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFriendRequests = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/users/${currentUser.id}/friend-requests`);
      setFriendRequests(res.data.received || []);
      setSentRequests(res.data.sent || []);
    } catch (error) {
      console.error('Failed to fetch friend requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const res = await axios.get(`${API}/users/search?q=${encodeURIComponent(query)}`);
      setSearchResults(res.data.filter(u => u.id !== currentUser.id));
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleAcceptRequest = async (userId) => {
    try {
      await axios.post(`${API}/friends/accept?userId=${currentUser.id}&friendId=${userId}`);
      toast.success('Friend request accepted!');
      fetchFriendRequests();
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
      fetchFriendRequests();
    } catch (error) {
      toast.error('Failed to reject request');
    }
  };

  const handleMessageClick = async (user) => {
    try {
      // Create or get DM thread
      const res = await axios.post(`${API}/dm/thread?userId=${currentUser.id}&peerUserId=${user.id}`);
      navigate(`/messenger/${res.data.id}`);
    } catch (error) {
      console.error('Failed to start conversation:', error);
      toast.error('Failed to start conversation');
    }
  };

  const UserCard = ({ user, showActions = true }) => (
    <div className="glass-card p-4 hover:bg-gray-800/50 transition-all">
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
          {user.location && (
            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
              <span>📍</span> {user.location}
            </p>
          )}
          
          {showActions && (
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
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-4xl mx-auto px-4 py-6 pb-24">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold neon-text mb-2">People</h1>
          <p className="text-gray-400">Find and connect with people on Loopync</p>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search people by name or handle..."
              className="w-full pl-12 pr-4 py-3 rounded-full bg-gray-900 border border-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-400"
            />
          </div>
        </div>

        {/* Search Results */}
        {searchQuery.trim().length >= 2 && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-white mb-3">Search Results</h2>
            {searchResults.length > 0 ? (
              <div className="space-y-3">
                {searchResults.map(user => (
                  <UserCard key={user.id} user={user} />
                ))}
              </div>
            ) : (
              <div className="glass-card p-6 text-center text-gray-400">
                No users found matching "{searchQuery}"
              </div>
            )}
          </div>
        )}

        {/* Tabs */}
        {searchQuery.trim().length < 2 && (
          <>
            <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide">
              <button
                onClick={() => setActiveTab('suggestions')}
                className={`flex-shrink-0 px-4 py-2 rounded-full font-medium transition-all ${
                  activeTab === 'suggestions'
                    ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                <UserPlus size={18} className="inline mr-2" />
                Suggestions
              </button>
              <button
                onClick={() => setActiveTab('friends')}
                className={`flex-shrink-0 px-4 py-2 rounded-full font-medium transition-all ${
                  activeTab === 'friends'
                    ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                <Users size={18} className="inline mr-2" />
                Friends ({(currentUser.friends || []).length})
              </button>
              <button
                onClick={() => setActiveTab('requests')}
                className={`flex-shrink-0 px-4 py-2 rounded-full font-medium transition-all ${
                  activeTab === 'requests'
                    ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                <Clock size={18} className="inline mr-2" />
                Requests ({friendRequests.length})
              </button>
            </div>

            {/* Tab Content */}
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
              </div>
            ) : (
              <>
                {/* Suggestions Tab */}
                {activeTab === 'suggestions' && (
                  <div className="space-y-3">
                    {suggestions.length > 0 ? (
                      suggestions.map(user => (
                        <UserCard key={user.id} user={user} />
                      ))
                    ) : (
                      <div className="glass-card p-8 text-center">
                        <Users size={48} className="mx-auto text-gray-600 mb-3" />
                        <p className="text-gray-400">No suggestions available</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Friends Tab */}
                {activeTab === 'friends' && (
                  <div className="space-y-3">
                    {friends.length > 0 ? (
                      friends.map(user => (
                        <UserCard key={user.id} user={user} showActions={false} />
                      ))
                    ) : (
                      <div className="glass-card p-8 text-center">
                        <Users size={48} className="mx-auto text-gray-600 mb-3" />
                        <p className="text-gray-400 mb-4">You don't have any friends yet</p>
                        <button
                          onClick={() => setActiveTab('suggestions')}
                          className="px-6 py-2 bg-cyan-400 text-black rounded-full hover:bg-cyan-300 transition"
                        >
                          Find People
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Requests Tab */}
                {activeTab === 'requests' && (
                  <div className="space-y-6">
                    {/* Received Requests */}
                    {friendRequests.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-3">
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

                    {/* Sent Requests */}
                    {sentRequests.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-3">
                          Sent Requests ({sentRequests.length})
                        </h3>
                        <div className="space-y-3">
                          {sentRequests.map(user => (
                            <UserCard key={user.id} user={user} showActions={false} />
                          ))}
                        </div>
                      </div>
                    )}

                    {friendRequests.length === 0 && sentRequests.length === 0 && (
                      <div className="glass-card p-8 text-center">
                        <Clock size={48} className="mx-auto text-gray-600 mb-3" />
                        <p className="text-gray-400">No pending friend requests</p>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default People;
