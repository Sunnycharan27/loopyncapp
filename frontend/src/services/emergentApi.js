import axios from "axios";
import { API } from "../App";

export const ai = {
  safety: async (text) => {
    const res = await axios.post(`${API}/ai/safety`, { text });
    return res.data;
  },
  translate: async (text, target_language, source_language) => {
    const res = await axios.post(`${API}/ai/translate`, { text, target_language, source_language });
    return res.data;
  },
  rank: async (query, documents) => {
    const res = await axios.post(`${API}/ai/rank`, { query, documents });
    return res.data;
  },
  insight: async (text, task) => {
    const res = await axios.post(`${API}/ai/insight`, { text, task });
    return res.data;
  }
};
