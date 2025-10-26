import React, { useState } from 'react';
import { Share2 } from 'lucide-react';
import UniversalShareModal from './UniversalShareModal';

const ShareButton = ({ item, type, className = '' }) => {
  const [showShareModal, setShowShareModal] = useState(false);

  return (
    <>
      <button
        onClick={() => setShowShareModal(true)}
        className={`text-cyan-400 hover:text-cyan-300 transition ${className}`}
        title="Share"
      >
        <Share2 size={22} />
      </button>

      {showShareModal && (
        <UniversalShareModal
          item={item}
          type={type}
          onClose={() => setShowShareModal(false)}
        />
      )}
    </>
  );
};

export default ShareButton;
