import React, { useState, useContext } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { AuthContext, API } from "../App";
import axios from "axios";
import { ArrowLeft, CreditCard, Wallet, QrCode, CheckCircle, Shield } from "lucide-react";
import { toast } from "sonner";

const Payment = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser } = useContext(AuthContext);
  const [paymentMethod, setPaymentMethod] = useState("upi");
  const [processing, setProcessing] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [ticketData, setTicketData] = useState(null);

  const { event, tier, seats, ticketCount, totalAmount } = location.state || {};

  if (!event) {
    navigate('/events');
    return null;
  }

  const handlePayment = async () => {
    setProcessing(true);

    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Create ticket(s) on backend
      const response = await axios.post(`${API}/events/${event.id}/tickets`, null, {
        params: {
          userId: currentUser.id,
          tier: tier.name
        }
      });

      // Award credits for booking
      await axios.post(`${API}/credits/earn`, null, {
        params: {
          userId: currentUser.id,
          amount: 20,
          source: 'ticket_booking',
          description: `Booked tickets for ${event.name}`
        }
      });

      setTicketData({
        ...response.data.ticket,
        event,
        seats,
        tier
      });
      setPaymentSuccess(true);
      toast.success("Payment successful! 🎉");
    } catch (error) {
      toast.error("Payment failed. Please try again.");
      setProcessing(false);
    }
  };

  if (paymentSuccess && ticketData) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="w-full max-w-md">
          {/* Success Animation */}
          <div className="text-center mb-8">
            <div className="inline-block p-6 rounded-full bg-green-500/20 mb-4">
              <CheckCircle size={64} className="text-green-400" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">Booking Confirmed!</h1>
            <p className="text-gray-400">Your tickets have been sent to your email</p>
          </div>

          {/* Ticket Card */}
          <div className="glass-card p-6 mb-6">
            <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-700">
              <div>
                <p className="text-gray-400 text-sm">Booking ID</p>
                <p className="text-white font-mono font-semibold">#{ticketData.id.substring(0, 8).toUpperCase()}</p>
              </div>
              <div className="px-3 py-1 rounded-full bg-green-500/20 border border-green-400">
                <span className="text-green-400 text-sm font-semibold">CONFIRMED</span>
              </div>
            </div>

            <div className="mb-4">
              <h3 className="text-xl font-bold text-white mb-1">{event.name}</h3>
              <p className="text-gray-400 text-sm">{event.location}</p>
              <p className="text-gray-400 text-sm">
                {new Date(event.date).toLocaleDateString('en-IN', { 
                  day: 'numeric', 
                  month: 'short', 
                  year: 'numeric' 
                })} • 6:00 PM
              </p>
            </div>

            <div className="py-4 border-y border-gray-700 mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400">Ticket Type</span>
                <span className="text-white font-semibold">{tier.name}</span>
              </div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400">Seats</span>
                <span className="text-white font-semibold">{seats.map(s => s.id).join(', ')}</span>
              </div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400">Quantity</span>
                <span className="text-white font-semibold">{ticketCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Total Paid</span>
                <span className="text-2xl font-bold text-cyan-400">₹{totalAmount}</span>
              </div>
            </div>

            {/* QR Code */}
            <div className="bg-white p-6 rounded-xl mb-4">
              <div className="text-center">
                <div className="w-48 h-48 mx-auto mb-2 bg-gray-100 flex items-center justify-center rounded-lg">
                  <QrCode size={180} className="text-gray-800" />
                </div>
                <p className="text-gray-600 text-xs font-mono">{ticketData.qrCode}</p>
                <p className="text-gray-500 text-xs mt-2">Show this QR at the venue entrance</p>
              </div>
            </div>

            <div className="flex items-center justify-center gap-2 text-gray-400 text-xs">
              <Shield size={14} />
              <span>Your ticket is secure and verified</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => navigate('/profile')}
              className="w-full py-3 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold"
            >
              View My Tickets
            </button>
            <button
              onClick={() => navigate('/events')}
              className="w-full py-3 rounded-full border-2 border-gray-700 text-white font-semibold hover:bg-gray-800/50"
            >
              Events
            </button>
          </div>

          {/* Credits Earned */}
          <div className="mt-6 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-500/20 border border-yellow-400">
              <span className="text-2xl">🎁</span>
              <span className="text-yellow-400 font-semibold">+20 Loop Credits earned!</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      {/* Header */}
      <div className="sticky top-0 z-10 glass-surface px-4 py-3 flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="text-cyan-400">
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-xl font-bold text-white">Payment</h1>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Booking Summary */}
        <div className="glass-card p-6 mb-6">
          <h3 className="text-lg font-bold text-white mb-4">Booking Summary</h3>
          
          <div className="flex gap-4 mb-4 pb-4 border-b border-gray-700">
            <img
              src={event.image}
              alt={event.name}
              className="w-24 h-24 rounded-xl object-cover"
            />
            <div className="flex-1">
              <h4 className="font-semibold text-white mb-1">{event.name}</h4>
              <p className="text-sm text-gray-400 mb-1">{event.location}</p>
              <p className="text-sm text-gray-400">
                {new Date(event.date).toLocaleDateString('en-IN', { 
                  day: 'numeric', 
                  month: 'short', 
                  year: 'numeric' 
                })}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Ticket Type</span>
              <span className="text-white font-semibold">{tier.name}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Selected Seats</span>
              <span className="text-white font-semibold">{seats.map(s => s.id).join(', ')}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Tickets</span>
              <span className="text-white font-semibold">{ticketCount} x ₹{tier.price}</span>
            </div>
            <div className="flex items-center justify-between pt-3 border-t border-gray-700">
              <span className="text-lg font-semibold text-white">Total Amount</span>
              <span className="text-3xl font-bold text-cyan-400">₹{totalAmount}</span>
            </div>
          </div>
        </div>

        {/* Payment Methods */}
        <div className="glass-card p-6 mb-6">
          <h3 className="text-lg font-bold text-white mb-4">Select Payment Method</h3>
          
          <div className="space-y-3">
            {/* UPI */}
            <div
              onClick={() => setPaymentMethod("upi")}
              className={`p-4 rounded-xl cursor-pointer transition-all ${
                paymentMethod === "upi"
                  ? 'bg-gradient-to-r from-cyan-400/20 to-purple-400/20 border-2 border-cyan-400'
                  : 'bg-gray-800/50 border-2 border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <QrCode size={24} className="text-purple-400" />
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-white">UPI</p>
                  <p className="text-sm text-gray-400">Google Pay, PhonePe, Paytm</p>
                </div>
                {paymentMethod === "upi" && (
                  <div className="w-6 h-6 rounded-full bg-cyan-400 flex items-center justify-center">
                    <CheckCircle size={16} className="text-black" />
                  </div>
                )}
              </div>
            </div>

            {/* Cards */}
            <div
              onClick={() => setPaymentMethod("card")}
              className={`p-4 rounded-xl cursor-pointer transition-all ${
                paymentMethod === "card"
                  ? 'bg-gradient-to-r from-cyan-400/20 to-purple-400/20 border-2 border-cyan-400'
                  : 'bg-gray-800/50 border-2 border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <CreditCard size={24} className="text-blue-400" />
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-white">Debit/Credit Card</p>
                  <p className="text-sm text-gray-400">Visa, Mastercard, RuPay</p>
                </div>
                {paymentMethod === "card" && (
                  <div className="w-6 h-6 rounded-full bg-cyan-400 flex items-center justify-center">
                    <CheckCircle size={16} className="text-black" />
                  </div>
                )}
              </div>
            </div>

            {/* Loop Credits */}
            <div
              onClick={() => setPaymentMethod("credits")}
              className={`p-4 rounded-xl cursor-pointer transition-all ${
                paymentMethod === "credits"
                  ? 'bg-gradient-to-r from-cyan-400/20 to-purple-400/20 border-2 border-cyan-400'
                  : 'bg-gray-800/50 border-2 border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-yellow-500/20 flex items-center justify-center">
                  <Wallet size={24} className="text-yellow-400" />
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-white">Loop Credits</p>
                  <p className="text-sm text-gray-400">Use your earned credits</p>
                </div>
                {paymentMethod === "credits" && (
                  <div className="w-6 h-6 rounded-full bg-cyan-400 flex items-center justify-center">
                    <CheckCircle size={16} className="text-black" />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Offers */}
        <div className="glass-card p-4 mb-6">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎁</span>
            <div className="flex-1">
              <p className="text-white font-semibold">Earn 20 Loop Credits</p>
              <p className="text-sm text-gray-400">Complete this booking to earn credits</p>
            </div>
          </div>
        </div>

        {/* Pay Button */}
        <button
          onClick={handlePayment}
          disabled={processing}
          className="w-full py-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold text-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {processing ? (
            <div className="flex items-center justify-center gap-2">
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
              Processing...
            </div>
          ) : (
            `Pay ₹${totalAmount}`
          )}
        </button>

        {/* Security Info */}
        <div className="mt-6 flex items-center justify-center gap-2 text-gray-400 text-sm">
          <Shield size={16} />
          <span>Secured by Razorpay • PCI DSS Compliant</span>
        </div>
      </div>
    </div>
  );
};

export default Payment;
