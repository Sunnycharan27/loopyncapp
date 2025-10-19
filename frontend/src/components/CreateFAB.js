import React from "react";
import { Plus, Video } from "lucide-react";

const CreateFAB = ({ onClick, type = "post" }) => {
  return (
    <button
      data-testid="create-fab-btn"
      onClick={onClick}
      className="fixed bottom-24 right-6 w-16 h-16 rounded-full bg-gradient-to-br from-cyan-400 to-pink-500 flex items-center justify-center shadow-2xl pulse-animation z-40 hover:scale-110 transition-transform"
      style={{
        boxShadow: '0 0 30px rgba(0, 224, 255, 0.5), 0 0 60px rgba(255, 61, 179, 0.3)'
      }}
    >
      {type === "reel" ? <Video size={28} /> : <Plus size={28} />}
    </button>
  );
};

export default CreateFAB;