const API_URL = "http://localhost:8000/api/v1";

export const api = {
    async listVoices() {
        const res = await fetch(`${API_URL}/voices`);
        if (!res.ok) throw new Error("Failed to fetch voices");
        return res.json();
    },

    async enrollVoice(file, name) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("name", name);

        const res = await fetch(`${API_URL}/enroll`, {
            method: "POST",
            body: formData,
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Enrollment failed");
        }
        return res.json();
    },

    async deleteVoice(voiceId) {
        const res = await fetch(`${API_URL}/voices/${voiceId}`, {
            method: "DELETE",
        });
        if (!res.ok) throw new Error("Failed to delete voice");
        return res.json();
    },

    async inferAudio(text, voiceId) {
        const res = await fetch(`${API_URL}/infer`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, voice_id: voiceId }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Inference failed");
        }
        return res.json();
    },

    async listHistory() {
        const res = await fetch(`${API_URL}/history`);
        if (!res.ok) throw new Error("Failed to fetch history");
        return res.json();
    },

    async deleteHistory(historyId) {
        const res = await fetch(`${API_URL}/history/${historyId}`, {
            method: "DELETE",
        });
        if (!res.ok) throw new Error("Failed to delete history item");
        return res.json();
    },

    getAudioUrl(relativePath) {
        if (!relativePath) return "";
        return `http://localhost:8000${relativePath}`;
    }
};
