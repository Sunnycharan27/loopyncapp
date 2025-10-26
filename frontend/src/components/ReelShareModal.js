import React, { useState } from "react";
import { X, Copy, Check, Download, Facebook, Twitter, Instagram, MessageCircle } from "lucide-react";
import { toast } from "sonner";

const ReelShareModal = ({ reel, onClose }) => {
  const [copied, setCopied] = useState(false);
  
  const shareUrl = `${window.location.origin}/reels/${reel.id}`;

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

  const handleDownload = async () => {
    try {
      toast.info("Downloading video...");
      
      // Fetch the video
      const response = await fetch(reel.videoUrl);
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `reel_${reel.id}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success("Video downloaded!");
    } catch (error) {
      console.error("Download failed:", error);
      toast.error("Failed to download video");
    }
  };

  const handleShare = (platform) => {
    const text = encodeURIComponent(`Check out this awesome reel: ${reel.caption || ''}`);
    const url = encodeURIComponent(shareUrl);
    
    const shareUrls = {
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
      twitter: `https://twitter.com/intent/tweet?text=${text}&url=${url}`,
      whatsapp: `https://wa.me/?text=${text}%20${url}`,
    };
    
    if (shareUrls[platform]) {
      window.open(shareUrls[platform], '_blank', 'width=600,height=400');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-end justify-center">
      <div className="bg-gray-900 w-full max-w-lg rounded-t-3xl p-6 animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-white">Share Reel</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition"
          >
            <X size={24} />
          </button>
        </div>

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
              <div className="w-12 h-12 rounded-full bg-cyan-400/20 flex items-center justify-center">
                <Copy size={24} className="text-cyan-400" />
              </div>
            )}
            <div className="flex-1 text-left">
              <p className="text-white font-semibold">
                {copied ? "Link Copied!" : "Copy Link"}
              </p>
              <p className="text-sm text-gray-400">Share via clipboard</p>
            </div>
          </button>

          {/* Download */}
          <button
            onClick={handleDownload}
            className="w-full flex items-center gap-4 p-4 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
          >
            <div className="w-12 h-12 rounded-full bg-purple-400/20 flex items-center justify-center">
              <Download size={24} className="text-purple-400" />
            </div>
            <div className="flex-1 text-left">
              <p className="text-white font-semibold">Download Video</p>
              <p className="text-sm text-gray-400">Save to your device</p>
            </div>
          </button>

          {/* Social Media */}
          <div className="grid grid-cols-4 gap-3 pt-4">
            <button
              onClick={() => handleShare('whatsapp')}
              className="flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
            >
              <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                <MessageCircle size={24} className="text-green-400" />
              </div>
              <span className="text-xs text-gray-400">WhatsApp</span>
            </button>

            <button
              onClick={() => handleShare('facebook')}
              className="flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
            >
              <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                <Facebook size={24} className="text-blue-400" />
              </div>
              <span className="text-xs text-gray-400">Facebook</span>
            </button>

            <button
              onClick={() => handleShare('twitter')}
              className="flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
            >
              <div className="w-12 h-12 rounded-full bg-sky-500/20 flex items-center justify-center">
                <Twitter size={24} className="text-sky-400" />
              </div>
              <span className="text-xs text-gray-400">Twitter</span>
            </button>

            <button
              className="flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-800 hover:bg-gray-700 transition"
            >
              <div className="w-12 h-12 rounded-full bg-pink-500/20 flex items-center justify-center">
                <Instagram size={24} className="text-pink-400" />
              </div>
              <span className="text-xs text-gray-400">Instagram</span>
            </button>
          </div>
        </div>

        {/* Reel Preview */}
        <div className="mt-6 p-4 rounded-2xl bg-gray-800 flex items-center gap-3">
          <video
            src={reel.videoUrl}
            className="w-16 h-16 rounded-lg object-cover"
            poster={reel.thumb}
          />
          <div className="flex-1 min-w-0">
            <p className="text-white font-semibold text-sm truncate">
              {reel.author?.name || 'Unknown'}
            </p>
            <p className="text-gray-400 text-xs truncate">
              {reel.caption || 'Amazing reel!'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReelShareModal;
