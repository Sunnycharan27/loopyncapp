import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useNavigate } from "react-router-dom";
import BottomNav from "../components/BottomNav";
import TopHeader from "../components/TopHeader";
import { Calendar, MapPin, Users, Ticket, Clock, TrendingUp } from "lucide-react";
import { toast } from "sonner";

const Events = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState("all");

  const tabs = [
    { id: "all", name: "All Events", icon: <Calendar size={16} /> },
    { id: "trending", name: "Trending", icon: <TrendingUp size={16} /> },
    { id: "upcoming", name: "Upcoming", icon: <Clock size={16} /> },
  ];

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const res = await axios.get(`${API}/events`);
      setEvents(res.data);
    } catch (error) {
      toast.error("Failed to load events");
    } finally {
      setLoading(false);
    }
  };

  const handleBookTicket = async (eventId) => {
    // Navigate to event detail page for booking
    navigate(`/events/${eventId}`);
  };

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <TopHeader title="Events & Experiences" subtitle="Book tickets for amazing events" />

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-full font-medium text-sm transition-all ${
                selectedTab === tab.id
                  ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              {tab.icon}
              {tab.name}
            </button>
          ))}
        </div>

        {/* Events List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full mx-auto"></div>
          </div>
        ) : events.length === 0 ? (
          <div className="text-center py-12 glass-card">
            <Calendar size={48} className="text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 mb-2">No events available</p>
            <p className="text-gray-500 text-sm">Check back soon for exciting events!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {events.map((event) => (
              <div
                key={event.id}
                onClick={() => navigate(`/events/${event.id}`)}
                className="glass-card p-4 cursor-pointer hover:scale-[1.01] transition-transform"
              >
                <div className="flex gap-4">
                  {/* Event Image */}
                  <div className="relative w-32 h-32 flex-shrink-0 rounded-xl overflow-hidden">
                    <img
                      src={event.image || 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=400'}
                      alt={event.name}
                      className="w-full h-full object-cover"
                    />
                    {event.vibeMeter && (
                      <div className="absolute bottom-2 left-2 px-2 py-1 rounded-full bg-black/50 backdrop-blur-sm">
                        <span className="text-xs text-white font-semibold">🔥 {event.vibeMeter}%</span>
                      </div>
                    )}
                  </div>

                  {/* Event Details */}
                  <div className="flex-1">
                    <h3 className="font-bold text-lg text-white mb-2 neon-text">{event.name}</h3>
                    
                    <div className="space-y-1 mb-3">
                      {event.date && (
                        <div className="flex items-center gap-2 text-gray-400 text-xs">
                          <Calendar size={12} />
                          <span>{new Date(event.date).toLocaleDateString('en-IN', { 
                            day: 'numeric', 
                            month: 'short', 
                            year: 'numeric' 
                          })}</span>
                        </div>
                      )}
                      
                      {event.location && (
                        <div className="flex items-center gap-2 text-gray-400 text-xs">
                          <MapPin size={12} />
                          <span className="line-clamp-1">{event.location}</span>
                        </div>
                      )}

                      {event.tiers && event.tiers.length > 0 && (
                        <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold">
                          <Ticket size={12} />
                          <span>From ₹{Math.min(...event.tiers.map(t => t.price))}</span>
                        </div>
                      )}
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/events/${event.id}`);
                      }}
                      className="w-full py-2 px-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white text-sm font-semibold hover:opacity-90"
                    >
                      Book Tickets
                    </button>
                  </div>
                </div>

                {/* Description */}
                {event.description && (
                  <p className="text-gray-400 text-sm mt-3 line-clamp-2">
                    {event.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <BottomNav active="discover" />
    </div>
  );
};

export default Events;
