import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "../App";
import BottomNav from "../components/BottomNav";
import { 
  ArrowLeft, DollarSign, Zap, TrendingUp, Clock, Download, 
  Upload, QrCode, X, Plus, Send, CreditCard, Smartphone,
  CheckCircle, AlertCircle, Star, Award, Scan, Phone, Tv,
  Lightbulb, Droplet, Wifi, ShoppingCart, Gift, Users,
  FileText, Building, ArrowUpRight, ArrowDownLeft, Copy,
  Share2, RefreshCw, Shield, ChevronRight, Wallet
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
  const [kycStatus, setKycStatus] = useState("basic"); // basic, intermediate, full
  
  // Modals
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [showSendModal, setShowSendModal] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [showRechargeModal, setShowRechargeModal] = useState(false);
  const [showBillPayModal, setShowBillPayModal] = useState(false);
  const [showBankModal, setShowBankModal] = useState(false);
  const [showUpiModal, setShowUpiModal] = useState(false);
  
  // Form states
  const [qrCodeUrl, setQrCodeUrl] = useState("");
  const [topUpAmount, setTopUpAmount] = useState("");
  const [sendAmount, setSendAmount] = useState("");
  const [recipientUpi, setRecipientUpi] = useState("");
  const [rechargeNumber, setRechargeNumber] = useState("");
  const [rechargeAmount, setRechargeAmount] = useState("");
  const [rechargeType, setRechargeType] = useState("mobile"); // mobile, dth, electricity
  const [paymentMethod, setPaymentMethod] = useState("wallet"); // wallet, upi, card, netbanking
  
  // Indian payment features
  const [linkedBanks, setLinkedBanks] = useState([]);
  const [upiId, setUpiId] = useState(`${currentUser.handle}@looppay`);
  const [transactionLimits, setTransactionLimits] = useState({
    perTransaction: 10000,
    perDay: 50000,
    perMonth: 100000
  });

  useEffect(() => {
    fetchWalletData();
    generateQRCode();
    loadLinkedBanks();
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
      
      // Set KYC status based on user data
      const kycTier = currentUser.kycTier || 1;
      if (kycTier === 3) setKycStatus("full");
      else if (kycTier === 2) setKycStatus("intermediate");
      else setKycStatus("basic");
      
      // Set limits based on KYC
      if (kycTier === 3) {
        setTransactionLimits({ perTransaction: 100000, perDay: 200000, perMonth: 1000000 });
      } else if (kycTier === 2) {
        setTransactionLimits({ perTransaction: 50000, perDay: 100000, perMonth: 500000 });
      }
    } catch (error) {
      console.error('Failed to fetch wallet data:', error);
      toast.error("Failed to load wallet data");
    } finally {
      setLoading(false);
    }
  };

  const loadLinkedBanks = () => {
    // Mock linked banks - in production, fetch from backend
    setLinkedBanks([
      { id: 1, name: "HDFC Bank", accountNumber: "****1234", primary: true },
      { id: 2, name: "SBI", accountNumber: "****5678", primary: false }
    ]);
  };

  const generateQRCode = async () => {
    try {
      const paymentData = JSON.stringify({
        userId: currentUser.id,
        handle: currentUser.handle,
        name: currentUser.name,
        upiId: `${currentUser.handle}@looppay`,
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

    if (parseFloat(topUpAmount) > transactionLimits.perTransaction) {
      toast.error(`Maximum ₹${transactionLimits.perTransaction} per transaction`);
      return;
    }

    try {
      // Simulate payment gateway
      toast.loading("Processing payment...");
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      await axios.post(`${API}/wallet/topup?userId=${currentUser.id}`, {
        amount: parseFloat(topUpAmount)
      });
      
      toast.dismiss();
      toast.success(`₹${topUpAmount} added successfully!`);
      setShowTopUpModal(false);
      setTopUpAmount("");
      fetchWalletData();
    } catch (error) {
      toast.dismiss();
      toast.error("Payment failed. Please try again.");
    }
  };

  const handleSendMoney = async () => {
    if (!sendAmount || parseFloat(sendAmount) <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    if (!recipientUpi) {
      toast.error("Please enter recipient's UPI ID");
      return;
    }

    if (parseFloat(sendAmount) > walletBalance) {
      toast.error("Insufficient balance");
      return;
    }

    if (parseFloat(sendAmount) > transactionLimits.perTransaction) {
      toast.error(`Maximum ₹${transactionLimits.perTransaction} per transaction`);
      return;
    }

    try {
      toast.loading("Processing transfer...");
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Create transaction
      await axios.post(`${API}/wallet/payment?userId=${currentUser.id}`, {
        amount: parseFloat(sendAmount),
        description: `Sent to ${recipientUpi}`,
        venueName: "UPI Transfer"
      });
      
      toast.dismiss();
      toast.success(`₹${sendAmount} sent to ${recipientUpi}`);
      setShowSendModal(false);
      setSendAmount("");
      setRecipientUpi("");
      fetchWalletData();
    } catch (error) {
      toast.dismiss();
      toast.error("Transfer failed");
    }
  };

  const handleRecharge = async () => {
    if (!rechargeNumber || !rechargeAmount) {
      toast.error("Please fill all fields");
      return;
    }

    if (parseFloat(rechargeAmount) > walletBalance) {
      toast.error("Insufficient balance");
      return;
    }

    try {
      toast.loading("Processing recharge...");
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      await axios.post(`${API}/wallet/payment?userId=${currentUser.id}`, {
        amount: parseFloat(rechargeAmount),
        description: `${rechargeType.toUpperCase()} Recharge - ${rechargeNumber}`,
        venueName: "Recharge"
      });
      
      toast.dismiss();
      toast.success("Recharge successful!");
      setShowRechargeModal(false);
      setRechargeNumber("");
      setRechargeAmount("");
      fetchWalletData();
    } catch (error) {
      toast.dismiss();
      toast.error("Recharge failed");
    }
  };

  const copyUpiId = () => {
    navigator.clipboard.writeText(upiId);
    toast.success("UPI ID copied!");
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
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft size={24} className="text-white" />
            </button>
            <div>
              <h1 className="text-xl font-bold text-white">LoopPay</h1>
              <p className="text-xs text-gray-400">India's payment app</p>
            </div>
          </div>
          <button
            onClick={() => setShowQRModal(true)}
            className="p-2 bg-cyan-400 rounded-lg hover:bg-cyan-500 transition-colors"
          >
            <Scan size={24} className="text-black" />
          </button>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-4">
        {/* Balance Card */}
        <div className="bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm opacity-90">Wallet Balance</p>
              <h2 className="text-4xl font-bold mt-1">₹{walletBalance.toFixed(2)}</h2>
            </div>
            <div className="text-right">
              <div className="px-3 py-1 bg-white/20 rounded-full text-xs mb-2">
                KYC: {kycStatus.toUpperCase()}
              </div>
              <button 
                onClick={() => toast.info("KYC upgrade available")}
                className="text-xs underline"
              >
                Upgrade Limits
              </button>
            </div>
          </div>
          
          {/* UPI ID */}
          <div className="flex items-center gap-2 bg-white/10 rounded-lg p-3">
            <span className="text-sm flex-1">{upiId}</span>
            <button onClick={copyUpiId} className="p-1 hover:bg-white/20 rounded">
              <Copy size={16} />
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-4 gap-3">
          <button
            onClick={() => setShowSendModal(true)}
            className="bg-gray-800 border border-gray-700 rounded-xl p-3 hover:bg-gray-750 transition-all text-center"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-blue-500/20 flex items-center justify-center">
              <Send size={20} className="text-blue-400" />
            </div>
            <p className="text-xs font-semibold text-white">Send</p>
          </button>

          <button
            onClick={() => setShowTopUpModal(true)}
            className="bg-gray-800 border border-gray-700 rounded-xl p-3 hover:bg-gray-750 transition-all text-center"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-green-500/20 flex items-center justify-center">
              <Plus size={20} className="text-green-400" />
            </div>
            <p className="text-xs font-semibold text-white">Add Money</p>
          </button>

          <button
            onClick={() => setShowRechargeModal(true)}
            className="bg-gray-800 border border-gray-700 rounded-xl p-3 hover:bg-gray-750 transition-all text-center"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-purple-500/20 flex items-center justify-center">
              <Phone size={20} className="text-purple-400" />
            </div>
            <p className="text-xs font-semibold text-white">Recharge</p>
          </button>

          <button
            onClick={() => setShowBillPayModal(true)}
            className="bg-gray-800 border border-gray-700 rounded-xl p-3 hover:bg-gray-750 transition-all text-center"
          >
            <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-orange-500/20 flex items-center justify-center">
              <FileText size={20} className="text-orange-400" />
            </div>
            <p className="text-xs font-semibold text-white">Bill Pay</p>
          </button>
        </div>

        {/* Services Grid */}
        <div>
          <h3 className="text-sm font-bold text-gray-400 mb-3 px-2">SERVICES</h3>
          <div className="grid grid-cols-4 gap-3">
            {[
              { icon: Tv, label: "DTH", color: "cyan" },
              { icon: Lightbulb, label: "Electricity", color: "yellow" },
              { icon: Droplet, label: "Water", color: "blue" },
              { icon: Wifi, label: "Broadband", color: "purple" },
              { icon: Building, label: "Rent", color: "green" },
              { icon: CreditCard, label: "Credit Card", color: "pink" },
              { icon: ShoppingCart, label: "Shopping", color: "orange" },
              { icon: Gift, label: "Offers", color: "red" }
            ].map((service, idx) => (
              <button
                key={idx}
                onClick={() => toast.info(`${service.label} coming soon!`)}
                className="bg-gray-800 border border-gray-700 rounded-xl p-3 hover:bg-gray-750 transition-all text-center"
              >
                <div className={`w-10 h-10 mx-auto mb-2 rounded-full bg-${service.color}-500/20 flex items-center justify-center`}>
                  <service.icon size={18} className={`text-${service.color}-400`} />
                </div>
                <p className="text-xs text-white">{service.label}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Loop Credits */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                <Zap size={20} className="text-white" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Loop Credits</h3>
                <p className="text-xs text-gray-400">Earn 2% cashback</p>
              </div>
            </div>
            <p className="text-2xl font-bold text-yellow-400">{loopCredits}</p>
          </div>
        </div>

        {/* Transaction Limits */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-white">Transaction Limits</h3>
            <Shield size={16} className="text-cyan-400" />
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-400">Per Transaction</span>
              <span className="text-white font-semibold">₹{transactionLimits.perTransaction.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Per Day</span>
              <span className="text-white font-semibold">₹{transactionLimits.perDay.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Per Month</span>
              <span className="text-white font-semibold">₹{transactionLimits.perMonth.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Recent Transactions */}
        <div>
          <div className="flex items-center justify-between mb-3 px-2">
            <h3 className="text-sm font-bold text-white">Recent Transactions</h3>
            <button className="text-cyan-400 text-xs font-semibold">View All</button>
          </div>

          {transactions.length > 0 ? (
            <div className="space-y-2">
              {transactions.slice(0, 5).map((txn) => (
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
                          <ArrowDownLeft size={18} className="text-green-400" />
                        ) : (
                          <ArrowUpRight size={18} className="text-red-400" />
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-white">{txn.description}</p>
                        <p className="text-xs text-gray-400">
                          {new Date(txn.createdAt).toLocaleDateString('en-IN', {
                            day: 'numeric',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-bold ${
                        txn.type === 'topup' ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {txn.type === 'topup' ? '+' : '-'}₹{txn.amount.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500">{txn.status}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-gray-800 border border-gray-700 rounded-2xl p-8 text-center">
              <Clock size={40} className="mx-auto mb-3 text-gray-600" />
              <p className="text-gray-400 text-sm">No transactions yet</p>
            </div>
          )}
        </div>
      </div>

      {/* Send Money Modal */}
      {showSendModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Send Money</h3>
              <button onClick={() => setShowSendModal(false)} className="text-gray-400">
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">UPI ID / Mobile / @Handle</label>
                <input
                  type="text"
                  value={recipientUpi}
                  onChange={(e) => setRecipientUpi(e.target.value)}
                  placeholder="someone@upi or 9876543210"
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
                <p className="text-xs text-gray-500 mt-1">
                  Available: ₹{walletBalance.toFixed(2)}
                </p>
              </div>

              <div className="grid grid-cols-3 gap-2">
                {[100, 500, 1000].map(amt => (
                  <button
                    key={amt}
                    onClick={() => setSendAmount(amt.toString())}
                    className="py-2 bg-gray-700 hover:bg-cyan-400 hover:text-black rounded-lg text-white text-sm transition-all"
                  >
                    ₹{amt}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleSendMoney}
              className="w-full mt-6 py-4 bg-gradient-to-r from-cyan-400 to-blue-500 text-white font-bold rounded-xl hover:opacity-90 transition-all"
            >
              Send ₹{sendAmount || '0'}
            </button>
          </div>
        </div>
      )}

      {/* Add Money Modal */}
      {showTopUpModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Add Money</h3>
              <button onClick={() => setShowTopUpModal(false)} className="text-gray-400">
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
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

              <div className="grid grid-cols-3 gap-2">
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

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Payment Method</label>
                <div className="space-y-2">
                  {[
                    { id: 'upi', label: 'UPI', icon: Smartphone },
                    { id: 'card', label: 'Debit/Credit Card', icon: CreditCard },
                    { id: 'netbanking', label: 'Net Banking', icon: Building }
                  ].map(method => (
                    <button
                      key={method.id}
                      onClick={() => setPaymentMethod(method.id)}
                      className={`w-full p-3 rounded-lg border flex items-center gap-3 transition-all ${
                        paymentMethod === method.id
                          ? 'border-cyan-400 bg-cyan-400/10'
                          : 'border-gray-700 bg-gray-900'
                      }`}
                    >
                      <method.icon size={20} className="text-cyan-400" />
                      <span className="text-white text-sm">{method.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={handleTopUp}
              className="w-full mt-6 py-4 bg-gradient-to-r from-green-400 to-emerald-500 text-white font-bold rounded-xl hover:opacity-90 transition-all"
            >
              Add ₹{topUpAmount || '0'}
            </button>
          </div>
        </div>
      )}

      {/* Recharge Modal */}
      {showRechargeModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Recharge & Bill Payment</h3>
              <button onClick={() => setShowRechargeModal(false)} className="text-gray-400">
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex gap-2">
                {[
                  { id: 'mobile', label: 'Mobile' },
                  { id: 'dth', label: 'DTH' },
                  { id: 'electricity', label: 'Electricity' }
                ].map(type => (
                  <button
                    key={type.id}
                    onClick={() => setRechargeType(type.id)}
                    className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
                      rechargeType === type.id
                        ? 'bg-cyan-400 text-black'
                        : 'bg-gray-700 text-white'
                    }`}
                  >
                    {type.label}
                  </button>
                ))}
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">
                  {rechargeType === 'mobile' ? 'Mobile Number' : rechargeType === 'dth' ? 'Customer ID' : 'Consumer Number'}
                </label>
                <input
                  type="text"
                  value={rechargeNumber}
                  onChange={(e) => setRechargeNumber(e.target.value)}
                  placeholder={rechargeType === 'mobile' ? '10 digit mobile number' : 'Enter number'}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white focus:border-cyan-400 focus:outline-none"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Amount</label>
                <input
                  type="number"
                  value={rechargeAmount}
                  onChange={(e) => setRechargeAmount(e.target.value)}
                  placeholder="Enter amount"
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white focus:border-cyan-400 focus:outline-none"
                />
              </div>

              {rechargeType === 'mobile' && (
                <div className="grid grid-cols-3 gap-2">
                  {[99, 199, 299].map(amt => (
                    <button
                      key={amt}
                      onClick={() => setRechargeAmount(amt.toString())}
                      className="py-2 bg-gray-700 hover:bg-cyan-400 hover:text-black rounded-lg text-white text-sm transition-all"
                    >
                      ₹{amt}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <button
              onClick={handleRecharge}
              className="w-full mt-6 py-4 bg-gradient-to-r from-purple-400 to-pink-500 text-white font-bold rounded-xl hover:opacity-90 transition-all"
            >
              Proceed to Pay
            </button>
          </div>
        </div>
      )}

      {/* QR Code Modal */}
      {showQRModal && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">My Payment QR</h3>
              <button onClick={() => setShowQRModal(false)} className="text-gray-400">
                <X size={24} />
              </button>
            </div>

            <div className="text-center">
              <p className="text-gray-400 mb-4 text-sm">Scan to send money to me</p>
              
              {qrCodeUrl && (
                <div className="bg-white p-6 rounded-2xl inline-block mb-4">
                  <img src={qrCodeUrl} alt="Payment QR Code" className="w-64 h-64" />
                </div>
              )}

              <div className="bg-gray-900 rounded-xl p-4 mb-4">
                <p className="text-xs text-gray-400 mb-1">UPI ID</p>
                <div className="flex items-center justify-center gap-2">
                  <p className="text-white font-semibold">{upiId}</p>
                  <button onClick={copyUpiId} className="p-1 hover:bg-gray-800 rounded">
                    <Copy size={16} className="text-cyan-400" />
                  </button>
                </div>
              </div>

              <button
                onClick={() => toast.info("Share feature coming soon")}
                className="w-full py-3 bg-cyan-400 text-black font-semibold rounded-xl hover:bg-cyan-500 transition-all flex items-center justify-center gap-2"
              >
                <Share2 size={20} />
                Share QR Code
              </button>
            </div>
          </div>
        </div>
      )}

      <BottomNav active="discover" />
    </div>
  );
};

export default LoopPay;

export default LoopPay;
