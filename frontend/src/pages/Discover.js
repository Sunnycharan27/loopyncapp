import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { MapPin, Calendar, Users, Star, ArrowRight, ShoppingBag, DollarSign } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const Discover = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [venues, setVenues] = useState([]);
  const [events, setEvents] = useState([]);
  const [creators, setCreators] = useState([]);
  const [tribes, setTribes] = useState([]);
  const [activeTab, setActiveTab] = useState("venues");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDiscoverData();
  }, []);

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
          <h1 className="text-2xl font-bold neon-text">Discover</h1>
          <p className="text-sm text-gray-400">Explore venues, events, marketplace & tribes</p>
        </div>

        {/* Tabs */}
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
                      <button className="px-4 py-2 rounded-full bg-cyan-400 text-black font-semibold hover:bg-cyan-300">
                        Get Tickets
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "creators" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {creators.map(creator => (
                <div key={creator.id} className="glass-card p-5 text-center" data-testid="creator-card">
                  <img src={creator.avatar} alt={creator.displayName} className="w-20 h-20 rounded-full mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-1">{creator.displayName}</h3>
                  <p className="text-sm text-gray-400 mb-3">{creator.bio}</p>
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-500 mb-4">
                    <Users size={14} />
                    <span>{creator.followers.toLocaleString()} followers</span>
                  </div>
                  <button className="w-full py-2 rounded-full bg-gradient-to-r from-cyan-400 to-pink-400 text-black font-semibold hover:opacity-90">
                    View Profile
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <BottomNav active="discover" />
    </div>
  );
};

export default Discover;