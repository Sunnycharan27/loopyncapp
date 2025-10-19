import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import { API, AuthContext } from "../App";
import { ArrowLeft, Plus, Minus, ShoppingCart } from "lucide-react";
import { toast } from "sonner";

const VenueDetail = () => {
  const { venueId } = useParams();
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [venue, setVenue] = useState(null);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchVenue();
  }, [venueId]);

  const fetchVenue = async () => {
    try {
      const res = await axios.get(`${API}/venues/${venueId}`);
      setVenue(res.data);
    } catch (error) {
      toast.error("Failed to load venue");
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (item) => {
    const existingItem = cart.find(i => i.id === item.id);
    if (existingItem) {
      setCart(cart.map(i => i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i));
    } else {
      setCart([...cart, { ...item, quantity: 1 }]);
    }
    toast.success(`${item.name} added to cart`);
  };

  const removeFromCart = (itemId) => {
    const existingItem = cart.find(i => i.id === itemId);
    if (existingItem.quantity > 1) {
      setCart(cart.map(i => i.id === itemId ? { ...i, quantity: i.quantity - 1 } : i));
    } else {
      setCart(cart.filter(i => i.id !== itemId));
    }
  };

  const getCartTotal = () => {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  const handleCreateOrder = async () => {
    if (cart.length === 0) {
      toast.error("Cart is empty");
      return;
    }

    setCreating(true);
    try {
      const res = await axios.post(`${API}/orders?userId=${currentUser.id}`, {
        venueId,
        items: cart.map(item => ({ id: item.id, name: item.name, price: item.price, quantity: item.quantity })),
        total: getCartTotal(),
        split: []
      });

      if (res.data.paymentLink) {
        toast.success("Order created! Opening payment link...");
        // Open Razorpay payment link in new tab
        window.open(res.data.paymentLink, '_blank');
        setTimeout(() => {
          navigate('/discover');
        }, 1000);
      }
    } catch (error) {
      toast.error("Failed to create order");
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0f021e' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full\"></div>
      </div>
    );
  }

  if (!venue) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0f021e' }}>
        <p className="text-gray-400">Venue not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-32" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="glass-surface p-4 mb-6">
          <button onClick={() => navigate('/discover')} className="flex items-center gap-2 text-cyan-400 mb-4">
            <ArrowLeft size={20} />
            Back to Discover
          </button>
          
          <div className="flex items-start gap-4">
            <img src={venue.avatar} alt={venue.name} className="w-20 h-20 rounded-3xl" />
            <div>
              <h1 className="text-2xl font-bold neon-text">{venue.name}</h1>
              <p className="text-sm text-gray-400 mb-2">{venue.description}</p>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-yellow-400">★ {venue.rating}</span>
                <span className="text-gray-500">• {venue.location}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Menu Items */}
        <div className="px-4 mb-6">
          <h2 className="text-xl font-bold mb-4">Menu</h2>
          <div className="space-y-3">
            {venue.menuItems?.map(item => {
              const cartItem = cart.find(i => i.id === item.id);
              return (
                <div key={item.id} className="glass-card p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold">{item.name}</h3>
                      <p className="text-cyan-400 font-bold mt-1">₹{item.price}</p>
                    </div>
                    {cartItem ? (
                      <div className="flex items-center gap-3">
                        <button onClick={() => removeFromCart(item.id)} className="w-8 h-8 rounded-full bg-red-400/20 text-red-400 flex items-center justify-center">
                          <Minus size={16} />
                        </button>
                        <span className="font-bold w-8 text-center">{cartItem.quantity}</span>
                        <button onClick={() => addToCart(item)} className="w-8 h-8 rounded-full bg-cyan-400 text-black flex items-center justify-center">
                          <Plus size={16} />
                        </button>
                      </div>
                    ) : (
                      <button onClick={() => addToCart(item)} className="px-4 py-2 rounded-full bg-cyan-400 text-black font-semibold hover:bg-cyan-300">
                        Add
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Cart Summary (Fixed Bottom) */}
      {cart.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 glass-surface border-t border-cyan-400/20 p-4">
          <div className="max-w-2xl mx-auto">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-sm text-gray-400">{cart.reduce((sum, i) => sum + i.quantity, 0)} items</p>
                <p className="text-2xl font-bold text-cyan-400">₹{getCartTotal()}</p>
              </div>
              <button 
                onClick={handleCreateOrder}
                disabled={creating}
                className="flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-cyan-400 to-pink-400 text-black font-bold hover:opacity-90 disabled:opacity-50"
              >
                <ShoppingCart size={20} />
                {creating ? 'Creating Order...' : 'Proceed to Pay'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VenueDetail;
