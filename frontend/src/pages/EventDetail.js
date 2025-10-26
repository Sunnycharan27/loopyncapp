import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import { useParams, useNavigate } from "react-router-dom";
import { Calendar, MapPin, Users, Star, Clock, Ticket, ArrowLeft, Info, Share2 } from "lucide-react";
import { toast } from "sonner";
import BottomNav from "../components/BottomNav";
import UniversalShareModal from "../components/UniversalShareModal";

const EventDetail = () => {
  const { eventId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTier, setSelectedTier] = useState(null);
  const [ticketCount, setTicketCount] = useState(1);
  const [showSeats, setShowSeats] = useState(false);
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [showShareModal, setShowShareModal] = useState(false);

  useEffect(() => {
    fetchEventDetails();
  }, [eventId]);

  const fetchEventDetails = async () => {
    try {
      const res = await axios.get(`${API}/events/${eventId}`);
      setEvent(res.data);
      if (res.data.tiers && res.data.tiers.length > 0) {
        setSelectedTier(res.data.tiers[0]);
      }
    } catch (error) {
      toast.error("Failed to load event details");
    } finally {
      setLoading(false);
    }
  };

  const generateSeats = () => {
    // Generate theater-style seats (10 rows x 12 seats)
    const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
    const seatsPerRow = 12;
    const allSeats = [];
    
    // Randomly mark some seats as booked (30% occupancy)
    const bookedSeats = new Set();
    const totalSeats = rows.length * seatsPerRow;
    const bookedCount = Math.floor(totalSeats * 0.3);
    
    while (bookedSeats.size < bookedCount) {
      const randomRow = rows[Math.floor(Math.random() * rows.length)];
      const randomSeat = Math.floor(Math.random() * seatsPerRow) + 1;
      bookedSeats.add(`${randomRow}${randomSeat}`);
    }

    rows.forEach(row => {
      const rowSeats = [];
      for (let i = 1; i <= seatsPerRow; i++) {
        const seatId = `${row}${i}`;
        rowSeats.push({
          id: seatId,
          row,
          number: i,
          status: bookedSeats.has(seatId) ? 'booked' : 'available'
        });
      }
      allSeats.push({ row, seats: rowSeats });
    });

    return allSeats;
  };

  const [seats] = useState(generateSeats());

  const handleSeatClick = (seat) => {
    if (seat.status === 'booked') return;

    const isSelected = selectedSeats.find(s => s.id === seat.id);
    
    if (isSelected) {
      setSelectedSeats(selectedSeats.filter(s => s.id !== seat.id));
    } else {
      if (selectedSeats.length < ticketCount) {
        setSelectedSeats([...selectedSeats, seat]);
      } else {
        toast.error(`You can select maximum ${ticketCount} seats`);
      }
    }
  };

  const handleProceedToPayment = async () => {
    if (selectedSeats.length !== ticketCount) {
      toast.error(`Please select ${ticketCount} seat(s)`);
      return;
    }

    try {
      setLoading(true);
      const totalAmount = selectedTier.price * ticketCount;
      
      // Book tickets using wallet
      const res = await axios.post(
        `${API}/events/${eventId}/book?userId=${currentUser.id}&tier=${selectedTier.name}&quantity=${ticketCount}`
      );

      toast.success(`🎉 ${res.data.message}\n💰 New Balance: ₹${res.data.balance}\n⭐ Earned ${res.data.creditsEarned} Loop Credits!`, {
        duration: 5000
      });

      // Navigate to profile tickets tab
      setTimeout(() => {
        navigate('/profile');
      }, 2000);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to book tickets");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <p className="text-gray-400">Event not found</p>
      </div>
    );
  }

  const totalPrice = selectedTier ? selectedTier.price * ticketCount : 0;

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      {/* Header with Back Button */}
      <div className="sticky top-0 z-10 glass-surface px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-cyan-400">
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-xl font-bold text-white">Book Tickets</h1>
        </div>
        <button onClick={() => setShowShareModal(true)} className="text-cyan-400 hover:text-cyan-300 transition">
          <Share2 size={22} />
        </button>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Event Banner */}
        <div className="relative h-64 rounded-2xl overflow-hidden mb-6">
          <img
            src={event.image || 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800'}
            alt={event.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
          <div className="absolute bottom-4 left-4 right-4">
            <h1 className="text-3xl font-bold text-white mb-2 neon-text">{event.name}</h1>
            {event.vibeMeter && (
              <div className="flex items-center gap-2">
                <div className="px-3 py-1 rounded-full bg-orange-500/20 backdrop-blur-sm border border-orange-400">
                  <span className="text-orange-400 text-sm font-semibold">🔥 {event.vibeMeter}% Vibe</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Event Details */}
        <div className="glass-card p-6 mb-6">
          <div className="space-y-4">
            {event.date && (
              <div className="flex items-start gap-3">
                <Calendar size={20} className="text-cyan-400 mt-1" />
                <div>
                  <p className="text-gray-400 text-sm">Date & Time</p>
                  <p className="text-white font-semibold">
                    {new Date(event.date).toLocaleDateString('en-IN', { 
                      weekday: 'long',
                      day: 'numeric', 
                      month: 'long', 
                      year: 'numeric' 
                    })}
                  </p>
                  <p className="text-gray-400 text-sm">6:00 PM onwards</p>
                </div>
              </div>
            )}

            {event.location && (
              <div className="flex items-start gap-3">
                <MapPin size={20} className="text-cyan-400 mt-1" />
                <div>
                  <p className="text-gray-400 text-sm">Venue</p>
                  <p className="text-white font-semibold">{event.location}</p>
                </div>
              </div>
            )}

            {event.description && (
              <div className="pt-4 border-t border-gray-700">
                <p className="text-gray-300">{event.description}</p>
              </div>
            )}
          </div>
        </div>

        {/* Ticket Selection */}
        {!showSeats ? (
          <div className="space-y-4">
            {/* Tier Selection */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Select Ticket Type</h3>
              <div className="space-y-3">
                {event.tiers && event.tiers.map((tier) => (
                  <div
                    key={tier.name}
                    onClick={() => setSelectedTier(tier)}
                    className={`p-4 rounded-xl cursor-pointer transition-all ${
                      selectedTier?.name === tier.name
                        ? 'bg-gradient-to-r from-cyan-400/20 to-purple-400/20 border-2 border-cyan-400'
                        : 'bg-gray-800/50 border-2 border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-white">{tier.name}</p>
                        <p className="text-sm text-gray-400">Available</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-cyan-400">₹{tier.price}</p>
                        <p className="text-xs text-gray-400">per ticket</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Ticket Count */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Number of Tickets</h3>
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setTicketCount(Math.max(1, ticketCount - 1))}
                  className="w-12 h-12 rounded-full bg-gray-800 text-white font-bold hover:bg-gray-700"
                >
                  −
                </button>
                <span className="text-3xl font-bold text-white">{ticketCount}</span>
                <button
                  onClick={() => setTicketCount(Math.min(10, ticketCount + 1))}
                  className="w-12 h-12 rounded-full bg-gray-800 text-white font-bold hover:bg-gray-700"
                >
                  +
                </button>
              </div>
              <p className="text-center text-gray-400 text-sm mt-4">Maximum 10 tickets per booking</p>
            </div>

            {/* Proceed to Seat Selection */}
            <button
              onClick={() => setShowSeats(true)}
              className="w-full py-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold text-lg hover:opacity-90"
            >
              Select Seats
            </button>
          </div>
        ) : (
          <>
            {/* Seat Selection UI */}
            <div className="glass-card p-6 mb-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white">Select Your Seats</h3>
                <button
                  onClick={() => {
                    setShowSeats(false);
                    setSelectedSeats([]);
                  }}
                  className="text-cyan-400 text-sm"
                >
                  ← Back
                </button>
              </div>

              {/* Screen */}
              <div className="mb-8">
                <div className="h-2 bg-gradient-to-r from-transparent via-cyan-400 to-transparent rounded-full mb-2"></div>
                <p className="text-center text-gray-400 text-sm">Screen this way</p>
              </div>

              {/* Seats Grid */}
              <div className="space-y-2 mb-6">
                {seats.map((rowData) => (
                  <div key={rowData.row} className="flex items-center gap-2">
                    <span className="text-gray-400 text-sm w-6">{rowData.row}</span>
                    <div className="flex gap-2 flex-1 justify-center">
                      {rowData.seats.map((seat) => {
                        const isSelected = selectedSeats.find(s => s.id === seat.id);
                        const isBooked = seat.status === 'booked';
                        
                        return (
                          <button
                            key={seat.id}
                            onClick={() => handleSeatClick(seat)}
                            disabled={isBooked}
                            className={`w-8 h-8 rounded-t-lg text-xs font-semibold transition-all ${
                              isSelected
                                ? 'bg-green-500 text-white'
                                : isBooked
                                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                            }`}
                          >
                            {seat.number}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>

              {/* Legend */}
              <div className="flex items-center justify-center gap-6 py-4 border-t border-gray-700">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-t-lg bg-gray-800"></div>
                  <span className="text-sm text-gray-400">Available</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-t-lg bg-green-500"></div>
                  <span className="text-sm text-gray-400">Selected</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-t-lg bg-gray-700"></div>
                  <span className="text-sm text-gray-400">Booked</span>
                </div>
              </div>
            </div>

            {/* Selected Seats Summary */}
            {selectedSeats.length > 0 && (
              <div className="glass-card p-4 mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400">Selected Seats:</span>
                  <span className="text-white font-semibold">
                    {selectedSeats.map(s => s.id).join(', ')}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Total Amount:</span>
                  <span className="text-2xl font-bold text-cyan-400">₹{totalPrice}</span>
                </div>
              </div>
            )}

            {/* Proceed to Payment */}
            <button
              onClick={handleProceedToPayment}
              disabled={selectedSeats.length !== ticketCount}
              className={`w-full py-4 rounded-full font-bold text-lg ${
                selectedSeats.length === ticketCount
                  ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white hover:opacity-90'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              {selectedSeats.length === ticketCount
                ? `Proceed to Payment - ₹${totalPrice}`
                : `Select ${ticketCount - selectedSeats.length} more seat(s)`}
            </button>
          </>
        )}

        {/* Important Info */}
        <div className="glass-card p-4 mt-6">
          <div className="flex items-start gap-3">
            <Info size={20} className="text-cyan-400 mt-0.5" />
            <div>
              <p className="text-sm text-gray-300 mb-2">
                • Your tickets will be sent via email and SMS
              </p>
              <p className="text-sm text-gray-300 mb-2">
                • Carry a valid ID proof to the venue
              </p>
              <p className="text-sm text-gray-300">
                • Gates open 1 hour before the event
              </p>
            </div>
          </div>
        </div>
      </div>

      <BottomNav active="discover" />
    </div>
  );
};

export default EventDetail;
