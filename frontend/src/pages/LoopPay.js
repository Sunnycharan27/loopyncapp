import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { 
  ArrowLeft, DollarSign, Zap, TrendingUp, Clock, Download, 
  Upload, QrCode, X, Plus, Send, CreditCard, Smartphone,
  CheckCircle, AlertCircle, Star, Award
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import QRCodeLib from "qrcode";

const LoopPay = () => {
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [walletBalance, setWalletBalance] = useState(0);
  const [loopCredits, setLoopCredits] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [showSendModal, setShowSendModal] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [qrCodeUrl, setQrCodeUrl] = useState("");
  const [topUpAmount, setTopUpAmount] = useState("");
  const [sendAmount, setSendAmount] = useState("");
  const [recipientHandle, setRecipientHandle] = useState("");

  useEffect(() => {
    fetchWalletData();
    generateQRCode();
  }, []);

  const fetchWalletData = async () => {
    try {
      setLoading(true);
      const [walletRes, creditsRes] = await Promise.all([
        axios.get(`${API}/wallet?userId=${currentUser.id}`),
        axios.get(`${API}/credits/${currentUser.id}`)
      ]);
      
      setWalletBalance(walletRes.data?.balance || 0);
      setTransactions(walletRes.data?.transactions || []);
      setLoopCredits(creditsRes.data?.credits || 0);
    } catch (error) {
      console.error('Failed to fetch wallet data:', error);
      toast.error("Failed to load wallet data");
    } finally {
      setLoading(false);
    }
  };

  const generateQRCode = async () => {
    try {
      const paymentData = JSON.stringify({
        userId: currentUser.id,
        handle: currentUser.handle,
        name: currentUser.name,
        type: "looppay"
      });
      
      const qrUrl = await QRCodeLib.toDataURL(paymentData, {
        width: 300,
        margin: 2,
        color: {
          dark: "#000000",
          light: "#FFFFFF"
        }
      });
      
      setQrCodeUrl(qrUrl);
    } catch (error) {
      console.error('Failed to generate QR code:', error);
    }
  };

  const handleTopUp = async () => {
    if (!topUpAmount || parseFloat(topUpAmount) <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    try {
      await axios.post(`${API}/wallet/topup?userId=${currentUser.id}`, {
        amount: parseFloat(topUpAmount)
      });
      
      toast.success(`₹${topUpAmount} added to wallet!`);
      setShowTopUpModal(false);
      setTopUpAmount("");
      fetchWalletData();
    } catch (error) {
      toast.error("Failed to top up wallet");
    }
  };

  const handleSend = async () => {
    if (!sendAmount || parseFloat(sendAmount) <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    if (!recipientHandle) {
      toast.error("Please enter recipient's handle");
      return;
    }

    if (parseFloat(sendAmount) > walletBalance) {
      toast.error("Insufficient balance");
      return;
    }

    try {
      // Mock send money functionality
      toast.success(`₹${sendAmount} sent to @${recipientHandle}`);
      setShowSendModal(false);
      setSendAmount("");
      setRecipientHandle("");
      fetchWalletData();
    } catch (error) {
      toast.error("Failed to send money");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 pb-24">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <ArrowLeft size={24} className="text-white" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white">LoopPay Wallet</h1>
            <p className="text-xs text-gray-400">Your digital wallet</p>
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Balance Card */}
        <div className="bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm opacity-90">Total Balance</p>
              <h2 className="text-4xl font-bold mt-1">₹{walletBalance.toFixed(2)}</h2>
            </div>
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
              <DollarSign size={32} />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm opacity-90">
            <span>{currentUser.name}</span>
            <span>•</span>
            <span>@{currentUser.handle}</span>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-4 gap-3">
          <button
            onClick={() => setShowTopUpModal(true)}
            className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:bg-gray-750 transition-all text-center"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-green-500/20 flex items-center justify-center">
              <Plus size={24} className="text-green-400" />
            </div>
            <p className="text-sm font-semibold text-white">Add Money</p>
          </button>

          <button
            onClick={() => setShowSendModal(true)}
            className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:bg-gray-750 transition-all text-center"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-blue-500/20 flex items-center justify-center">
              <Send size={24} className="text-blue-400" />
            </div>
            <p className="text-sm font-semibold text-white">Send</p>
          </button>

          <button
            onClick={() => setShowQRModal(true)}
            className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:bg-gray-750 transition-all text-center"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-purple-500/20 flex items-center justify-center">
              <QrCode size={24} className="text-purple-400" />
            </div>
            <p className="text-sm font-semibold text-white">Pay QR</p>
          </button>

          <button
            onClick={() => navigate('/wallet/cards')}
            className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:bg-gray-750 transition-all text-center"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-pink-500/20 flex items-center justify-center">
              <CreditCard size={24} className="text-pink-400" />
            </div>
            <p className="text-sm font-semibold text-white">Cards</p>
          </button>
        </div>

        {/* Loop Credits */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                <Zap size={24} className="text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Loop Credits</h3>
                <p className="text-sm text-gray-400">Reward points</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-yellow-400">{loopCredits}</p>
              <p className="text-xs text-gray-500">Credits</p>
            </div>
          </div>
          <div className="mt-4 p-3 bg-gray-900 rounded-lg">
            <p className="text-sm text-gray-300">
              💡 Earn 2% cashback on every transaction as Loop Credits!
            </p>
          </div>
        </div>

        {/* Recent Transactions */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white">Recent Transactions</h3>
            <button className="text-cyan-400 text-sm font-semibold">View All</button>
          </div>

          {transactions.length > 0 ? (
            <div className="space-y-2">
              {transactions.slice(0, 10).map((txn) => (
                <div
                  key={txn.id}
                  className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:bg-gray-750 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        txn.type === 'topup' ? 'bg-green-500/20' : 'bg-red-500/20'
                      }`}>
                        {txn.type === 'topup' ? (
                          <Download size={20} className="text-green-400" />
                        ) : (
                          <Upload size={20} className="text-red-400" />
                        )}
                      </div>
                      <div>
                        <p className="font-semibold text-white capitalize">{txn.type}</p>
                        <p className="text-xs text-gray-400">{txn.description}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${
                        txn.type === 'topup' ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {txn.type === 'topup' ? '+' : '-'}₹{txn.amount.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(txn.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-gray-800 border border-gray-700 rounded-2xl p-12 text-center">
              <Clock size={48} className="mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400">No transactions yet</p>
              <p className="text-sm text-gray-500 mt-2">Your transaction history will appear here</p>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">Why LoopPay?</h3>
          <div className="space-y-4">
            {[
              { icon: CheckCircle, title: "Instant Transfers", desc: "Send money instantly to friends" },
              { icon: Star, title: "Earn Rewards", desc: "Get Loop Credits on every payment" },
              { icon: Award, title: "Exclusive Offers", desc: "Access deals with Loop Credits" },
              { icon: Smartphone, title: "Pay Anywhere", desc: "Use QR code at partner stores" }
            ].map((feature, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                  <feature.icon size={20} className="text-cyan-400" />
                </div>
                <div>
                  <p className="font-semibold text-white">{feature.title}</p>
                  <p className="text-sm text-gray-400">{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Up Modal */}
      {showTopUpModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Add Money</h3>
              <button
                onClick={() => setShowTopUpModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={24} />
              </button>
            </div>

            <div className="mb-6">
              <label className="text-sm text-gray-400 mb-2 block">Enter Amount</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-xl text-white">₹</span>
                <input
                  type="number"
                  value={topUpAmount}
                  onChange={(e) => setTopUpAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full pl-10 pr-4 py-4 bg-gray-900 border border-gray-700 rounded-xl text-white text-xl focus:border-cyan-400 focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 mb-6">
              {[100, 500, 1000, 2000, 5000, 10000].map(amount => (
                <button
                  key={amount}
                  onClick={() => setTopUpAmount(amount.toString())}
                  className="py-3 bg-gray-700 hover:bg-cyan-400 hover:text-black rounded-lg font-semibold text-white transition-all"
                >
                  ₹{amount}
                </button>
              ))}
            </div>

            <button
              onClick={handleTopUp}
              className="w-full py-4 bg-gradient-to-r from-cyan-400 to-blue-500 text-white font-bold rounded-xl hover:opacity-90 transition-all"
            >
              Add Money
            </button>
          </div>
        </div>
      )}

      {/* Send Money Modal */}
      {showSendModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Send Money</h3>
              <button
                onClick={() => setShowSendModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Recipient Handle</label>
                <input
                  type="text"
                  value={recipientHandle}
                  onChange={(e) => setRecipientHandle(e.target.value)}
                  placeholder="@username"
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white focus:border-cyan-400 focus:outline-none"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Amount</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-xl text-white">₹</span>
                  <input
                    type="number"
                    value={sendAmount}
                    onChange={(e) => setSendAmount(e.target.value)}
                    placeholder="0.00"
                    className="w-full pl-10 pr-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white text-xl focus:border-cyan-400 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <button
              onClick={handleSend}
              className="w-full py-4 bg-gradient-to-r from-cyan-400 to-blue-500 text-white font-bold rounded-xl hover:opacity-90 transition-all"
            >
              Send Money
            </button>
          </div>
        </div>
      )}

      {/* QR Code Modal */}
      {showQRModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Pay with QR</h3>
              <button
                onClick={() => setShowQRModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={24} />
              </button>
            </div>

            <div className="text-center">
              <p className="text-gray-400 mb-4">Scan this code to receive payment</p>
              
              {qrCodeUrl ? (
                <div className="bg-white p-6 rounded-2xl inline-block mb-4">
                  <img src={qrCodeUrl} alt="Payment QR Code" className="w-64 h-64" />
                </div>
              ) : (
                <div className="bg-gray-900 p-6 rounded-2xl inline-block mb-4">
                  <div className="w-64 h-64 flex items-center justify-center">
                    <div className="animate-spin w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full"></div>
                  </div>
                </div>
              )}

              <p className="text-sm text-gray-400 mb-2">Your Handle: @{currentUser.handle}</p>
              <p className="text-xs text-gray-500">Anyone can scan this code to send you money</p>
            </div>
          </div>
        </div>
      )}

      <BottomNav active="discover" />
    </div>
  );
};

export default LoopPay;
