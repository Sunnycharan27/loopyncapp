import React, { useState } from "react";
import { X, Copy, Check, Link2, Facebook, Twitter, MessageCircle, Mail, Users } from "lucide-react";
import { toast } from "sonner";
import ShareToFriendsModal from "./ShareToFriendsModal";

const UniversalShareModal = ({ item, type, onClose, currentUser }) => {
  const [copied, setCopied] = useState(false);
  const [showFriendsModal, setShowFriendsModal] = useState(false);
  
  // Generate appropriate URL based on type
  const getShareUrl = () => {
    const baseUrl = window.location.origin;
    switch (type) {
      case 'post':
        return `${baseUrl}/posts/${item.id}`;
      case 'reel':
        return `${baseUrl}/reels/${item.id}`;
      case 'room':
        return `${baseUrl}/viberooms/${item.id}`;
      case 'tribe':
        return `${baseUrl}/tribes/${item.id}`;
      case 'event':
        return `${baseUrl}/events/${item.id}`;
      case 'venue':
        return `${baseUrl}/venues/${item.id}`;
      case 'profile':
        return `${baseUrl}/profile/${item.id}`;
      case 'product':
        return `${baseUrl}/marketplace/${item.id}`;
      default:
        return baseUrl;
    }
  };

  const shareUrl = getShareUrl();

  // Generate share text based on type
  const getShareText = () => {
    switch (type) {
      case 'post':
        return `Check out this post by ${item.author?.name || 'someone'}: ${item.caption || ''}`;
      case 'reel':
        return `Watch this amazing reel by ${item.author?.name || 'someone'}! ${item.caption || ''}`;
      case 'room':
        return `Join me in "${item.name}" on Loopync! Live audio conversation happening now 🎙️`;
      case 'tribe':
        return `Join the "${item.name}" tribe on Loopync! ${item.description || ''}`;
      case 'event':
        return `Check out this event: ${item.name} 🎉`;
      case 'venue':
        return `Discover ${item.name} on Loopync! ${item.description || ''}`;
      case 'profile':
        return `Check out ${item.name}'s profile on Loopync!`;
      case 'product':
        return `Check out ${item.name} on Loopync Marketplace! Only ₹${item.price}`;
      default:
        return 'Check this out on Loopync!';
    }
  };

  const handleCopy = async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(shareUrl);
      } else {
        // Fallback for non-secure contexts
        const textArea = document.createElement("textarea");
        textArea.value = shareUrl;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      setCopied(true);
      toast.success("Link copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error("Failed to copy link");
    }
  };

  const handleShare = (platform) => {
    const text = encodeURIComponent(getShareText());
    const url = encodeURIComponent(shareUrl);
    
    const shareUrls = {
      whatsapp: `https://wa.me/?text=${text}%20${url}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${text}`,
      twitter: `https://twitter.com/intent/tweet?text=${text}&url=${url}`,
      email: `mailto:?subject=${encodeURIComponent('Check this out on Loopync')}&body=${text}%20${url}`,
    };
    
    if (shareUrls[platform]) {
      window.open(shareUrls[platform], '_blank', 'width=600,height=400');
    }
  };

  // Use native share API if available (mobile)
  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Loopync',
          text: getShareText(),
          url: shareUrl,
        });
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('Error sharing:', error);
        }
      }
    }
  };

  const getItemTitle = () => {
    switch (type) {
      case 'post':
      case 'reel':
        return item.author?.name || 'User';
      case 'room':
      case 'tribe':
      case 'event':
      case 'venue':
      case 'product':
        return item.name || 'Item';
      case 'profile':
        return item.name || 'Profile';
      default:
        return 'Share';
    }
  };

  const getItemDescription = () => {
    return item.caption || item.description || item.bio || '';
  };

  return (
    <>
      {showFriendsModal ? (
        <ShareToFriendsModal
          currentUser={currentUser}
          item={item}
          type={type}
          onClose={() => {
            setShowFriendsModal(false);
            onClose();
          }}
        />
      ) : (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center">
          <div className="bg-gradient-to-b from-gray-900 to-black w-full max-w-lg rounded-t-3xl sm:rounded-3xl p-6 animate-slide-up border border-gray-800">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Share {type}</h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition"
              >
                <X size={24} />
              </button>
            </div>

            {/* Share to Friends (In-App) */}
            {currentUser && (
              <button
                onClick={() => setShowFriendsModal(true)}
                className="w-full flex items-center gap-4 p-4 rounded-2xl bg-gradient-to-r from-cyan-500/20 to-purple-500/20 hover:from-cyan-500/30 hover:to-purple-500/30 transition mb-3 border border-cyan-500/30"
              >
                <div className="w-12 h-12 rounded-full bg-cyan-400/20 flex items-center justify-center">
                  <Users size={24} className="text-cyan-400" />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-white font-semibold">Share with Friends</p>
                  <p className="text-sm text-gray-400">Send directly to your friends on Loopync</p>
                </div>
              </button>
            )}

        {/* Native Share (Mobile) */}
        {navigator.share && (
          <button
            onClick={handleNativeShare}
            className="w-full flex items-center gap-4 p-4 rounded-2xl bg-gradient-to-r from-cyan-500/20 to-purple-500/20 hover:from-cyan-500/30 hover:to-purple-500/30 transition mb-3 border border-cyan-500/30"
          >
            <div className="w-12 h-12 rounded-full bg-cyan-400/20 flex items-center justify-center">
              <Link2 size={24} className="text-cyan-400" />
            </div>
            <div className="flex-1 text-left">
              <p className="text-white font-semibold">Share via...</p>
              <p className="text-sm text-gray-400">Use your device's share menu</p>
            </div>
          </button>
        )}

        {/* Share Options */}
        <div className="space-y-3">
          {/* Copy Link */}
          <button
            onClick={handleCopy}
            className="w-full flex items-center gap-4 p-4 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
          >
            {copied ? (
              <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                <Check size={24} className="text-green-400" />
              </div>
            ) : (
              <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                <Copy size={24} className="text-blue-400" />
              </div>
            )}
            <div className="flex-1 text-left">
              <p className="text-white font-semibold">
                {copied ? "Link Copied!" : "Copy Link"}
              </p>
              <p className="text-sm text-gray-400 truncate">{shareUrl}</p>
            </div>
          </button>

          {/* Social Media Grid */}
          <div className="grid grid-cols-4 gap-3 pt-2">
            <button
              onClick={() => handleShare('whatsapp')}
              className="flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
            >
              <div className="w-14 h-14 rounded-full bg-green-500/20 flex items-center justify-center">
                <MessageCircle size={28} className="text-green-400" />
              </div>
              <span className="text-xs text-gray-400">WhatsApp</span>
            </button>

            <button
              onClick={() => handleShare('facebook')}
              className="flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
            >
              <div className="w-14 h-14 rounded-full bg-blue-500/20 flex items-center justify-center">
                <Facebook size={28} className="text-blue-400" />
              </div>
              <span className="text-xs text-gray-400">Facebook</span>
            </button>

            <button
              onClick={() => handleShare('twitter')}
              className="flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
            >
              <div className="w-14 h-14 rounded-full bg-sky-500/20 flex items-center justify-center">
                <Twitter size={28} className="text-sky-400" />
              </div>
              <span className="text-xs text-gray-400">Twitter</span>
            </button>

            <button
              onClick={() => handleShare('email')}
              className="flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
            >
              <div className="w-14 h-14 rounded-full bg-purple-500/20 flex items-center justify-center">
                <Mail size={28} className="text-purple-400" />
              </div>
              <span className="text-xs text-gray-400">Email</span>
            </button>
          </div>
        </div>

        {/* Preview */}
        <div className="mt-6 p-4 rounded-2xl bg-gray-800/50 border border-gray-700">
          <p className="text-sm text-gray-400 mb-2">Preview</p>
          <div className="flex items-start gap-3">
            <img
              src={item.author?.avatar || item.image || item.avatar || 'https://api.dicebear.com/7.x/shapes/svg?seed=default'}
              alt={getItemTitle()}
              className="w-12 h-12 rounded-lg object-cover"
            />
            <div className="flex-1 min-w-0">
              <p className="text-white font-semibold text-sm truncate">
                {getItemTitle()}
              </p>
              <p className="text-gray-400 text-xs truncate line-clamp-2">
                {getItemDescription() || 'Check this out on Loopync!'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UniversalShareModal;
