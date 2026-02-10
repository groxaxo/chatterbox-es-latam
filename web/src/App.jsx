import { useState, useEffect } from 'react';
import { api } from './api';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('voices'); // 'voices', 'enroll', 'history'
  const [voices, setVoices] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);

  // Enrollment State
  const [enrollName, setEnrollName] = useState("");
  const [enrollFile, setEnrollFile] = useState(null);
  const [isEnrolling, setIsEnrolling] = useState(false);

  // Inference State
  const [text, setText] = useState("");
  const [isInferring, setIsInferring] = useState(false);
  const [inferenceResult, setInferenceResult] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [v, h] = await Promise.all([api.listVoices(), api.listHistory()]);
      setVoices(v);
      setHistory(h);
    } catch (err) {
      console.error(err);
    }
  };

  const handleEnroll = async (e) => {
    e.preventDefault();
    if (!enrollFile || !enrollName) return;

    setIsEnrolling(true);
    try {
      await api.enrollVoice(enrollFile, enrollName);
      await loadData();
      setEnrollName("");
      setEnrollFile(null);
      document.getElementById('file-upload').value = "";
      setActiveTab('voices');
    } catch (err) {
      alert(err.message);
    } finally {
      setIsEnrolling(false);
    }
  };

  const handleDeleteVoice = async (e, id) => {
    e.stopPropagation();
    if (!confirm("¿Estás seguro de que quieres eliminar esta voz?")) return;
    try {
      await api.deleteVoice(id);
      if (selectedVoice?.id === id) setSelectedVoice(null);
      await loadData();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleInfer = async () => {
    if (!selectedVoice || !text) return;

    setIsInferring(true);
    setInferenceResult(null);
    try {
      const res = await api.inferAudio(text, selectedVoice.id);
      setInferenceResult(res);
      await loadData(); // Refresh history
    } catch (err) {
      alert(err.message);
    } finally {
      setIsInferring(false);
    }
  };

  const handleDeleteHistory = async (id) => {
    if (!confirm("¿Eliminar este audio?")) return;
    try {
      await api.deleteHistory(id);
      await loadData();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="logo">Chatterbox</div>
        <div
          className={`nav-item ${activeTab === 'voices' ? 'active' : ''}`}
          onClick={() => setActiveTab('voices')}
        >
          🎙️ Voces e Inferencia
        </div>
        <div
          className={`nav-item ${activeTab === 'enroll' ? 'active' : ''}`}
          onClick={() => setActiveTab('enroll')}
        >
          ➕ Nueva Voz
        </div>
        <div
          className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📜 Historial
        </div>
      </div>

      {/* Main Content */}
      <div className="main">

        {activeTab === 'enroll' && (
          <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h2 className="section-title">Registrar Nueva Voz</h2>
            <form onSubmit={handleEnroll}>
              <div className="form-group">
                <label>Nombre de la Voz</label>
                <input
                  type="text"
                  value={enrollName}
                  onChange={(e) => setEnrollName(e.target.value)}
                  placeholder="ej. Lionel Messi"
                  required
                />
              </div>
              <div className="form-group">
                <label>Audio de Referencia (WAV/MP3)</label>
                <input
                  id="file-upload"
                  type="file"
                  accept="audio/*"
                  onChange={(e) => setEnrollFile(e.target.files[0])}
                  required
                />
                <small style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', display: 'block' }}>
                  Sube una muestra de audio clara (3-10 segundos recomendado).
                </small>
              </div>
              <button type="submit" className="primary" disabled={isEnrolling}>
                {isEnrolling ? "Procesando..." : "Registrar Voz"}
              </button>
            </form>
          </div>
        )}

        {activeTab === 'voices' && (
          <div className="grid" style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem' }}>
            <div>
              <h2 className="section-title">Biblioteca de Voces ({voices.length})</h2>
              <div className="voices-grid">
                {voices.map(voice => (
                  <div
                    key={voice.id}
                    className={`voice-card ${selectedVoice?.id === voice.id ? 'selected' : ''}`}
                    onClick={() => setSelectedVoice(voice)}
                  >
                    <div className="voice-header">
                      <div>
                        <div className="voice-name">{voice.name}</div>
                        <div className="voice-date">{new Date(voice.created_at).toLocaleDateString()}</div>
                      </div>
                      <button className="btn-icon btn-delete" onClick={(e) => handleDeleteVoice(e, voice.id)}>
                        🗑️
                      </button>
                    </div>
                    {voice.ref_audio_path && (
                      <audio controls src={api.getAudioUrl(`/static/input/${voice.ref_audio_path}`)} />
                    )}
                    <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Registro: {voice.enrollment_time_seconds.toFixed(2)}s
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Inference Sidebar */}
            <div className="card" style={{ height: 'fit-content', position: 'sticky', top: '2rem' }}>
              <h2 className="section-title">Inferencia</h2>
              {!selectedVoice ? (
                <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
                  Selecciona una voz para comenzar
                </div>
              ) : (
                <>
                  <div className="form-group">
                    <label>Seleccionada: <span style={{ color: 'var(--accent)' }}>{selectedVoice.name}</span></label>
                  </div>
                  <div className="form-group">
                    <label>Texto</label>
                    <textarea
                      rows="6"
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                      placeholder="Escribe algo..."
                    />
                  </div>
                  <button className="primary" onClick={handleInfer} disabled={isInferring || !text}>
                    {isInferring ? "Generando..." : "Generar Audio"}
                  </button>

                  {inferenceResult && (
                    <div className="result-grid">
                      <div className="result-box">
                        <div className="result-header">
                          <span className="label-lora">LoRA (Ajustado)</span>
                          <span className="badge">{inferenceResult.inference_time_lora.toFixed(2)}s</span>
                        </div>
                        <audio controls autoPlay src={api.getAudioUrl(inferenceResult.audio_url_lora)} style={{ width: '100%' }} />
                      </div>
                      <div className="result-box">
                        <div className="result-header">
                          <span className="label-base">Modelo Base</span>
                          <span className="badge">{inferenceResult.inference_time_base.toFixed(2)}s</span>
                        </div>
                        <audio controls src={api.getAudioUrl(inferenceResult.audio_url_base)} style={{ width: '100%' }} />
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div style={{ maxWidth: '900px', margin: '0 auto' }}>
            <h2 className="section-title">Historial de Inferencias</h2>
            {history.map(item => (
              <div key={item.id} className="history-item">
                <div className="history-info">
                  <div className="history-text">"{item.text}"</div>
                  <div className="history-meta">
                    <span>📅 {new Date(item.created_at).toLocaleString()}</span>
                    <span>🗣️ {voices.find(v => v.id === item.voice_id)?.name || 'Desconocido'}</span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                    <div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--accent)', marginBottom: '0.2rem' }}>LoRA ({item.inference_time_lora?.toFixed(2)}s)</div>
                      <audio controls src={api.getAudioUrl(`/static/output/${item.audio_path_lora}`)} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.2rem' }}>Base ({item.inference_time_base?.toFixed(2)}s)</div>
                      <audio controls src={api.getAudioUrl(`/static/output/${item.audio_path_base}`)} />
                    </div>
                  </div>

                </div>
                <button className="btn-icon btn-delete" onClick={() => handleDeleteHistory(item.id)} style={{ marginLeft: '1rem' }}>
                  🗑️
                </button>
              </div>
            ))}
            {history.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
                Sin historial aún.
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
