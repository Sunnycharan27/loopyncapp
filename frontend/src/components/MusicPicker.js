import React, { useEffect, useState } from "react";
import axios from "axios";
import { API } from "../App";
import { Search, Play, Pause } from "lucide-react";

const MusicPicker = ({ onSelect }) => {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [audio, setAudio] = useState(null);
  const [playingId, setPlayingId] = useState(null);

  useEffect(() => {
    return () => {
      if (audio) {
        audio.pause();
      }
    };
  }, [audio]);

  const search = async () => {
    if (!q.trim()) { setResults([]); return; }
    setLoading(true);
    try {
      const res = await axios.get(`${API}/music/search?q=${encodeURIComponent(q)}&limit=10`);
      setResults(res.data.items || []);
    } catch (e) {
      console.error('search failed', e);
    } finally {
      setLoading(false);
    }
  };

  const togglePlay = (track) => {
    if (playingId === track.id) {
      audio?.pause();
      setPlayingId(null);
      return;
    }
    if (audio) audio.pause();
    const a = new Audio(track.previewUrl);
    a.currentTime = 0;
    a.play().catch(() => {});
    setAudio(a);
    setPlayingId(track.id);
    // Auto-stop at 30s
    const stopAt = () => {
      if (a.currentTime >= 30) {
        a.pause();
        setPlayingId(null);
        a.removeEventListener('timeupdate', stopAt);
      }
    };
    a.addEventListener('timeupdate', stopAt);
  };

  return (
    <div className="rounded-2xl border border-gray-800 p-3">
      <div className="flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search music (mock JioSaavn)"
          className="flex-1"
          data-testid="music-search-input"
        />
        <button onClick={search} className="px-3 py-2 rounded-full bg-cyan-400/20 text-cyan-300 border border-cyan-500/30 text-xs" data-testid="music-search-btn">
          Search
        </button>
      </div>

      {loading && <div className="text-gray-500 text-sm mt-2">Searching…</div>}

      <div className="mt-3 grid gap-2 max-h-48 overflow-auto">
        {results.map(track => (
          <div key={track.id} className="flex items-center gap-3 p-2 rounded-xl bg-black/30 border border-gray-800">
            <img src={track.artwork} alt={track.title} className="w-12 h-12 rounded-lg object-cover" />
            <div className="flex-1">
              <p className="text-white text-sm font-semibold">{track.title}</p>
              <p className="text-gray-400 text-xs">{(track.artists || []).join(', ')}</p>
            </div>
            <button onClick={() => togglePlay(track)} className="p-2 rounded-full bg-cyan-400/20 text-cyan-300">
              {playingId === track.id ? <Pause size={18} /> : <Play size={18} />}
            </button>
            <button onClick={() => onSelect && onSelect(track)} className="px-3 py-2 rounded-full bg-purple-400/20 text-purple-300 border border-purple-500/30 text-xs">
              Use Preview
            </button>
          </div>
        ))}
        {(!loading && results.length === 0 && q.trim()) && (
          <div className="text-gray-500 text-sm">No results</div>
        )}
      </div>

      <p className="text-[11px] text-gray-500 mt-2">Preview only (≤30s). Attribution required. No download or mixing in MVP.</p>
    </div>
  );
};

export default MusicPicker;
