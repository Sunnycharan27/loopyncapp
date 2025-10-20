import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, AuthContext } from "../App";
import { toast } from "sonner";
import { CheckCircle, Music, Dumbbell, Coffee, Code, Palette, BookOpen, Heart, MapPin, Shield, Lock, Eye, Bell, Mail, FileText, CreditCard } from "lucide-react";

const Onboarding = () => {
  const { currentUser, login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [selectedInterests, setSelectedInterests] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // eKYC state
  const [aadhaarNumber, setAadhaarNumber] = useState("");
  const [kycVerified, setKycVerified] = useState(false);
  const [verifyingKyc, setVerifyingKyc] = useState(false);
  
  // Consent state
  const [consents, setConsents] = useState({
    dataCollection: false,
    personalizedAds: false,
    locationTracking: false,
    emailNotifications: false,
    pushNotifications: false,
    dataSharing: false
  });

  const languages = [
    { code: "en", name: "English", nativeName: "English" },
    { code: "hi", name: "Hindi", nativeName: "हिंदी" },
    { code: "te", name: "Telugu", nativeName: "తెలుగు" }
  ];

  const interests = [
    { id: "music", name: "Music", icon: <Music size={24} />, color: "from-purple-400 to-pink-500" },
    { id: "fitness", name: "Fitness", icon: <Dumbbell size={24} />, color: "from-green-400 to-teal-500" },
    { id: "food", name: "Food & Dining", icon: <Coffee size={24} />, color: "from-orange-400 to-red-500" },
    { id: "tech", name: "Technology", icon: <Code size={24} />, color: "from-blue-400 to-cyan-500" },
    { id: "art", name: "Art & Design", icon: <Palette size={24} />, color: "from-pink-400 to-purple-500" },
    { id: "books", name: "Books & Learning", icon: <BookOpen size={24} />, color: "from-yellow-400 to-orange-500" },
    { id: "wellness", name: "Health & Wellness", icon: <Heart size={24} />, color: "from-red-400 to-pink-500" },
    { id: "travel", name: "Travel & Adventure", icon: <MapPin size={24} />, color: "from-teal-400 to-blue-500" }
  ];

  const toggleInterest = (interestId) => {
    if (selectedInterests.includes(interestId)) {
      setSelectedInterests(selectedInterests.filter(id => id !== interestId));
    } else {
      if (selectedInterests.length < 5) {
        setSelectedInterests([...selectedInterests, interestId]);
      } else {
        toast.error("You can select maximum 5 interests");
      }
    }
  };

  const handleComplete = async () => {
    if (selectedInterests.length < 2) {
      toast.error("Please select at least 2 interests");
      return;
    }

    setLoading(true);
    try {
      // Save user interests and language - send as comma-separated string
      const interestsString = selectedInterests.join(',');
      const url = `${API}/users/${currentUser.id}/interests?interests=${encodeURIComponent(interestsString)}&language=${selectedLanguage}`;
      
      await axios.post(url);

      // Award onboarding credits
      const creditsUrl = `${API}/credits/earn?userId=${currentUser.id}&amount=100&source=onboarding&description=${encodeURIComponent('Welcome bonus for completing onboarding')}`;
      await axios.post(creditsUrl);

      toast.success("Welcome to Loopync! 🎉 +100 Loop Credits earned!");
      
      // Redirect to home
      window.location.href = '/';
    } catch (error) {
      console.error("Onboarding error:", error);
      toast.error("Failed to save preferences. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: 'linear-gradient(180deg, #0f021e 0%, #1a0b2e 100%)' }}>
      <div className="w-full max-w-2xl">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Step {step} of 2</span>
            <span className="text-gray-400 text-sm">{step === 1 ? '50%' : '100%'}</span>
          </div>
          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-cyan-400 to-purple-500 transition-all duration-300"
              style={{ width: step === 1 ? '50%' : '100%' }}
            ></div>
          </div>
        </div>

        {/* Step 1: Language Selection */}
        {step === 1 && (
          <div className="glass-card p-8">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-white mb-2 neon-text">Welcome to Loopync!</h1>
              <p className="text-gray-400">Let's personalize your experience</p>
            </div>

            <h2 className="text-xl font-bold text-white mb-6">Choose Your Preferred Language</h2>
            
            <div className="grid grid-cols-1 gap-4 mb-8">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setSelectedLanguage(lang.code)}
                  className={`p-6 rounded-2xl transition-all flex items-center justify-between ${
                    selectedLanguage === lang.code
                      ? 'bg-gradient-to-r from-cyan-400/20 to-purple-400/20 border-2 border-cyan-400'
                      : 'bg-gray-800/50 border-2 border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="text-left">
                    <p className="text-2xl font-bold text-white mb-1">{lang.nativeName}</p>
                    <p className="text-gray-400 text-sm">{lang.name}</p>
                  </div>
                  {selectedLanguage === lang.code && (
                    <CheckCircle size={32} className="text-cyan-400" />
                  )}
                </button>
              ))}
            </div>

            <button
              onClick={() => setStep(2)}
              className="w-full py-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold text-lg hover:opacity-90"
            >
              Continue
            </button>
          </div>
        )}

        {/* Step 2: Interest Selection */}
        {step === 2 && (
          <div className="glass-card p-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-white mb-2">What are you interested in?</h2>
              <p className="text-gray-400">Select 2-5 interests to personalize your feed</p>
              <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-400/10 border border-cyan-400/30">
                <span className="text-cyan-400 font-semibold">
                  {selectedInterests.length} / 5 selected
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-8">
              {interests.map((interest) => {
                const isSelected = selectedInterests.includes(interest.id);
                return (
                  <button
                    key={interest.id}
                    onClick={() => toggleInterest(interest.id)}
                    className={`p-6 rounded-2xl transition-all relative overflow-hidden ${
                      isSelected
                        ? 'border-2 border-cyan-400'
                        : 'bg-gray-800/50 border-2 border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    {isSelected && (
                      <div className={`absolute inset-0 bg-gradient-to-br ${interest.color} opacity-10`}></div>
                    )}
                    <div className="relative z-10 text-center">
                      <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full mb-3 ${
                        isSelected ? `bg-gradient-to-br ${interest.color}` : 'bg-gray-700'
                      }`}>
                        <div className="text-white">{interest.icon}</div>
                      </div>
                      <p className={`font-semibold ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                        {interest.name}
                      </p>
                    </div>
                    {isSelected && (
                      <div className="absolute top-3 right-3">
                        <CheckCircle size={24} className="text-cyan-400" />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-4 rounded-full border-2 border-gray-700 text-white font-semibold hover:bg-gray-800/50"
              >
                Back
              </button>
              <button
                onClick={handleComplete}
                disabled={selectedInterests.length < 2 || loading}
                className={`flex-1 py-4 rounded-full font-bold text-lg ${
                  selectedInterests.length >= 2 && !loading
                    ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white hover:opacity-90'
                    : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                }`}
              >
                {loading ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
                    Setting up...
                  </div>
                ) : (
                  'Complete Setup'
                )}
              </button>
            </div>

            {/* Reward Preview */}
            <div className="mt-6 text-center">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-500/20 border border-yellow-400">
                <span className="text-2xl">🎁</span>
                <span className="text-yellow-400 font-semibold">Earn 100 Loop Credits on completion!</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Onboarding;
