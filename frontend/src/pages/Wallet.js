import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { Plus, Settings, RefreshCw, ArrowUpRight, ArrowDownLeft, Shield, Scan } from "lucide-react";
import { toast } from "sonner";
import { QRCodeSVG } from "qrcode.react";

const Wallet = () => {
  const { currentUser } = useContext(AuthContext);
  const [walletData, setWalletData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("pay");
  const [showTopUp, setShowTopUp] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState("");
  const [paymentAmount, setPaymentAmount] = useState("");
  const [paymentDescription, setPaymentDescription] = useState("");

  useEffect(() => {
    fetchWalletData();
  }, []);

  const fetchWalletData = async () => {
    try {
      const res = await axios.get(`${API}/wallet?userId=${currentUser.id}`);
      setWalletData(res.data);
    } catch (error) {
      toast.error("Failed to load wallet");
    } finally {
      setLoading(false);
    }
  };

  const handleTopUp = async () => {
    const amount = parseFloat(topUpAmount);
    if (!amount || amount <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    try {
      const res = await axios.post(`${API}/wallet/topup?userId=${currentUser.id}`, {
        amount
      });
      toast.success(`₹${amount} added to wallet!`);
      setWalletData({ ...walletData, balance: res.data.balance });
      setShowTopUp(false);
      setTopUpAmount("");
      fetchWalletData();
    } catch (error) {
      toast.error("Top-up failed");
    }
  };

  const handlePayment = async () => {
    const amount = parseFloat(paymentAmount);
    if (!amount || amount <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    if (!paymentDescription) {
      toast.error("Please enter payment description");
      return;
    }

    try {
      const res = await axios.post(`${API}/wallet/payment?userId=${currentUser.id}`, {
        amount,
        description: paymentDescription,
        venueName: paymentDescription
      });
      
      toast.success(`₹${amount} paid successfully! ${res.data.creditsEarned > 0 ? `Earned ${res.data.creditsEarned} Loop Credits!` : ''}`);
      setWalletData({ ...walletData, balance: res.data.balance });
      setShowPayment(false);
      setPaymentAmount("");
      setPaymentDescription("");
      fetchWalletData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Payment failed");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
        <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  const kycTierBadge = walletData?.kycTier === 3 ? "Premium" : walletData?.kycTier === 2 ? "Verified" : "Basic";
  const kycColor = walletData?.kycTier === 3 ? "text-yellow-400" : walletData?.kycTier === 2 ? "text-green-400" : "text-gray-400";

  return (
    <div className="min-h-screen pb-24" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      {/* Header - Cyber Theme */}
      <div className="sticky top-0 z-10 glass-surface px-4 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold neon-text">LoopPay</h1>
          <p className="text-xs text-gray-400">Your digital wallet</p>
        </div>
        <button
          data-testid="wallet-settings-btn"
          className="w-10 h-10 rounded-full flex items-center justify-center bg-cyan-400/10 text-cyan-400 hover:bg-cyan-400/20"
        >
          <Settings size={20} />
        </button>
      </div>

      <div className="max-w-2xl mx-auto px-4">
        {/* Wallet Card - Cyber Aurora Theme */}
        <div 
          className="relative overflow-hidden mt-6 rounded-3xl shadow-2xl neon-glow"
          style={{
            background: 'linear-gradient(135deg, #00E0FF 0%, #7928CA 50%, #FF0080 100%)',
          }}
        >
          {/* Decorative Elements */}
          <div className="absolute top-0 right-0 w-48 h-48 opacity-20" style={{
            background: 'radial-gradient(circle, white 0%, transparent 70%)'
          }}></div>
          <div className="absolute bottom-0 left-0 w-32 h-32 opacity-20" style={{
            background: 'radial-gradient(circle, white 0%, transparent 70%)'
          }}></div>

          {/* Glass Card Content */}
          <div className="relative z-10 m-4 glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 flex items-center justify-center">
                  <span className="text-xl font-bold text-white">L</span>
                </div>
                <div>
                  <p className="text-white font-semibold text-base">{currentUser.name}</p>
                  <p className="text-gray-400 text-xs">@{currentUser.handle}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={fetchWalletData}
                  className="w-8 h-8 flex items-center justify-center text-cyan-400 hover:bg-cyan-400/10 rounded-full"
                >
                  <RefreshCw size={16} />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs mb-1">Available Balance</p>
                <h2 className="text-4xl font-bold text-white">₹{walletData?.balance?.toFixed(2) || '0.00'}</h2>
                <p className="text-xs text-gray-500 mt-1">
                  Updated at {new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
              <button
                data-testid="wallet-topup-btn"
                onClick={() => setShowTopUp(true)}
                className="px-6 py-3 rounded-full font-semibold text-white text-sm bg-gradient-to-r from-cyan-400 to-purple-500 hover:opacity-90"
              >
                <Plus size={16} className="inline mr-1" />
                Load Card
              </button>
            </div>
          </div>
        </div>

        {/* Tabs - Cyber Theme */}
        <div className="flex gap-2 mt-6">
          <button
            onClick={() => setActiveTab("pay")}
            className={`flex-1 py-3 px-4 rounded-full font-medium text-sm transition-all ${
              activeTab === "pay"
                ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                : 'glass-card text-gray-400 hover:bg-gray-800/50'
            }`}
            data-testid="wallet-pay-tab"
          >
            Pay at Venue
          </button>
          <button
            onClick={() => setActiveTab("transactions")}
            className={`flex-1 py-3 px-4 rounded-full font-medium text-sm transition-all ${
              activeTab === "transactions"
                ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white'
                : 'glass-card text-gray-400 hover:bg-gray-800/50'
            }`}
            data-testid="wallet-transactions-tab"
          >
            Past Transactions
          </button>
        </div>

        {/* Content */}
        {activeTab === "pay" ? (
          <div className="glass-card mt-6 p-6">
            <h3 className="text-center text-white font-semibold text-base mb-2 neon-text">
              Scan QR Code at Venue
            </h3>
            <p className="text-center text-gray-400 text-sm mb-6">
              Show this QR code at Loopync partner venues to pay
            </p>
            
            <div className="bg-white flex flex-col items-center justify-center py-8 px-4 rounded-2xl">
              <div className="bg-white p-4 rounded-lg">
                <QRCodeSVG
                  value={JSON.stringify({
                    userId: currentUser.id,
                    userName: currentUser.name,
                    handle: currentUser.handle,
                    balance: walletData?.balance || 0,
                    type: "loopync_wallet"
                  })}
                  size={200}
                  level="H"
                  includeMargin={true}
                  imageSettings={{
                    src: "/logo.jpg",
                    height: 40,
                    width: 40,
                    excavate: true,
                  }}
                />
              </div>
              <p className="mt-4 text-sm text-gray-700 font-semibold">@{currentUser.handle}</p>
              <p className="text-xs text-gray-500">Balance: ₹{walletData?.balance?.toFixed(2)}</p>
            </div>

            {/* Test Payment Button */}
            <button
              onClick={() => setShowPayment(true)}
              className="w-full mt-6 py-3 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold hover:opacity-90 flex items-center justify-center gap-2"
              data-testid="make-payment-btn"
            >
              <Scan size={18} />
              Make Test Payment
            </button>

            <div className="mt-6 pt-6 border-t border-gray-700">
              <div className="flex gap-3 justify-center flex-wrap">
                <div className="px-4 py-2 rounded-full bg-cyan-400/10 text-cyan-400 text-xs font-medium">
                  <Shield size={12} className="inline mr-1" />
                  UPI Linked
                </div>
                <div className="px-4 py-2 rounded-full bg-green-400/10 text-green-400 text-xs font-medium">
                  RBI Compliant
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-semibold ${kycColor}`}>
                  <Shield size={12} className="inline mr-1" />
                  {kycTierBadge}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-6">
            {walletData?.transactions && walletData.transactions.length > 0 ? (
              <div className="space-y-3">
                {walletData.transactions.map((txn) => (
                  <div key={txn.id} className="glass-card p-4" data-testid="transaction-item">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          txn.type === 'topup' ? 'bg-green-400/10 text-green-400' :
                          txn.type === 'withdraw' ? 'bg-red-400/10 text-red-400' :
                          'bg-cyan-400/10 text-cyan-400'
                        }`}>
                          {txn.type === 'topup' ? <ArrowDownLeft size={18} /> :
                           txn.type === 'withdraw' ? <ArrowUpRight size={18} /> :
                           <ArrowUpRight size={18} />}
                        </div>
                        <div>
                          <p className="font-semibold text-sm text-white">
                            {txn.type === 'topup' ? 'Money Added' :
                             txn.type === 'withdraw' ? 'Withdrawal' :
                             txn.description || 'Payment'}
                          </p>
                          <p className="text-xs text-gray-400">
                            {new Date(txn.createdAt).toLocaleDateString('en-IN')} • {txn.status}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold text-base ${
                          txn.type === 'topup' ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {txn.type === 'topup' ? '+' : '-'}₹{txn.amount.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 glass-card">
                <p className="text-gray-400">No transactions yet</p>
              </div>
            )}
          </div>
        )}
      </div>

      <BottomNav active="wallet" />

      {/* Top-Up Modal - Cyber Theme */}
      {showTopUp && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card p-6 w-full max-w-md">
            <h2 className="text-xl font-bold neon-text mb-4">Add Money to Wallet</h2>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">Enter Amount</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-2xl text-cyan-400">₹</span>
                <input
                  type="number"
                  value={topUpAmount}
                  onChange={(e) => setTopUpAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full pl-12 pr-4 py-4 text-3xl font-bold bg-gray-900/50 border-2 border-cyan-400/30 rounded-xl focus:border-cyan-400 focus:outline-none text-white"
                  autoFocus
                  data-testid="topup-amount-input"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 mb-6">
              {[100, 500, 1000, 2000, 5000, 10000].map((amt) => (
                <button
                  key={amt}
                  onClick={() => setTopUpAmount(amt.toString())}
                  className="py-3 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 text-sm font-semibold text-white border border-cyan-400/20"
                >
                  ₹{amt}
                </button>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowTopUp(false)}
                className="flex-1 py-3 rounded-full border-2 border-gray-600 text-gray-300 font-semibold hover:bg-gray-800/50"
              >
                Cancel
              </button>
              <button
                onClick={handleTopUp}
                className="flex-1 py-3 rounded-full text-white font-semibold bg-gradient-to-r from-cyan-400 to-purple-500 hover:opacity-90"
                data-testid="topup-confirm-btn"
              >
                Add Money
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Wallet;
