// Chatterbox ES-LATAM TTS Server - Client-side JavaScript

// API Base URL
const API_BASE = window.location.origin;

// DOM Elements
const textInput = document.getElementById('text-input');
const charCount = document.getElementById('char-count');
const voiceModeRadios = document.querySelectorAll('input[name="voice-mode"]');
const predefinedVoiceGroup = document.getElementById('predefined-voice-group');
const referenceAudioGroup = document.getElementById('reference-audio-group');
const predefinedVoiceSelect = document.getElementById('predefined-voice');
const referenceAudioInput = document.getElementById('reference-audio');
const temperatureSlider = document.getElementById('temperature');
const exaggerationSlider = document.getElementById('exaggeration');
const cfgWeightSlider = document.getElementById('cfg-weight');
const speedSlider = document.getElementById('speed');
const seedInput = document.getElementById('seed');
const formatSelect = document.getElementById('format');
const generateBtn = document.getElementById('generate-btn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const resultAudio = document.getElementById('result-audio');
const downloadBtn = document.getElementById('download-btn');
const regenerateBtn = document.getElementById('regenerate-btn');
const modelStatus = document.getElementById('model-status');
const deviceStatus = document.getElementById('device-status');

// State
let currentAudioBlob = null;
let uploadedReferenceFile = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadVoices();
    setupEventListeners();
    updateSliderValues();
});

// Check server health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            modelStatus.textContent = data.model_loaded ? 'Cargado ✓' : 'Error al cargar';
            modelStatus.style.background = data.model_loaded 
                ? 'linear-gradient(135deg, #4caf50, #8bc34a)' 
                : 'linear-gradient(135deg, #f44336, #e91e63)';
            deviceStatus.textContent = data.device || 'CPU';
        } else {
            modelStatus.textContent = 'Error';
            modelStatus.style.background = 'linear-gradient(135deg, #f44336, #e91e63)';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        modelStatus.textContent = 'Desconectado';
        modelStatus.style.background = '#9e9e9e';
        deviceStatus.textContent = '-';
    }
}

// Load available voices
async function loadVoices() {
    try {
        // Try to fetch voices from API (if endpoint exists)
        // For now, we'll use a default list
        const defaultVoices = [
            { id: 'default.wav', name: 'Voz por Defecto' },
            { id: 'masculine.wav', name: 'Voz Masculina' },
            { id: 'feminine.wav', name: 'Voz Femenina' }
        ];
        
        predefinedVoiceSelect.innerHTML = '';
        defaultVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = voice.name;
            predefinedVoiceSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load voices:', error);
        predefinedVoiceSelect.innerHTML = '<option value="">Error al cargar voces</option>';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Character count
    textInput.addEventListener('input', () => {
        charCount.textContent = textInput.value.length;
    });
    
    // Voice mode toggle
    voiceModeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            if (radio.value === 'predefined') {
                predefinedVoiceGroup.classList.remove('hidden');
                referenceAudioGroup.classList.add('hidden');
            } else {
                predefinedVoiceGroup.classList.add('hidden');
                referenceAudioGroup.classList.remove('hidden');
            }
        });
    });
    
    // Reference audio upload
    referenceAudioInput.addEventListener('change', (e) => {
        uploadedReferenceFile = e.target.files[0];
    });
    
    // Slider value updates
    temperatureSlider.addEventListener('input', updateSliderValues);
    exaggerationSlider.addEventListener('input', updateSliderValues);
    cfgWeightSlider.addEventListener('input', updateSliderValues);
    speedSlider.addEventListener('input', updateSliderValues);
    
    // Generate button
    generateBtn.addEventListener('click', generateAudio);
    
    // Download button
    downloadBtn.addEventListener('click', downloadAudio);
    
    // Regenerate button
    regenerateBtn.addEventListener('click', () => {
        result.classList.add('hidden');
        generateAudio();
    });
}

// Update slider value displays
function updateSliderValues() {
    document.getElementById('temp-value').textContent = temperatureSlider.value;
    document.getElementById('exag-value').textContent = exaggerationSlider.value;
    document.getElementById('cfg-value').textContent = cfgWeightSlider.value;
    document.getElementById('speed-value').textContent = speedSlider.value;
}

// Generate audio
async function generateAudio() {
    const text = textInput.value.trim();
    
    if (!text) {
        alert('Por favor, ingresa un texto para sintetizar.');
        return;
    }
    
    const voiceMode = document.querySelector('input[name="voice-mode"]:checked').value;
    
    if (voiceMode === 'predefined' && !predefinedVoiceSelect.value) {
        alert('Por favor, selecciona una voz predefinida.');
        return;
    }
    
    if (voiceMode === 'clone' && !uploadedReferenceFile) {
        alert('Por favor, sube un archivo de audio de referencia.');
        return;
    }
    
    // Show loading
    generateBtn.disabled = true;
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    
    try {
        let requestBody = {
            text: text,
            voice_mode: voiceMode,
            temperature: parseFloat(temperatureSlider.value),
            exaggeration: parseFloat(exaggerationSlider.value),
            cfg_weight: parseFloat(cfgWeightSlider.value),
            speed_factor: parseFloat(speedSlider.value),
            seed: parseInt(seedInput.value),
            output_format: formatSelect.value,
            split_text: true,
            chunk_size: 200,
            language: 'es'
        };
        
        if (voiceMode === 'predefined') {
            requestBody.predefined_voice_id = predefinedVoiceSelect.value;
        }
        
        // If using reference audio, we need to upload it first
        if (voiceMode === 'clone' && uploadedReferenceFile) {
            // For now, use a simple approach - in production, implement file upload
            alert('La clonación de voz requiere subir el archivo primero. Esta función estará disponible próximamente.');
            loading.classList.add('hidden');
            generateBtn.disabled = false;
            return;
        }
        
        const response = await fetch(`${API_BASE}/tts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al generar audio');
        }
        
        // Get audio blob
        currentAudioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(currentAudioBlob);
        
        // Display result
        resultAudio.src = audioUrl;
        result.classList.remove('hidden');
        
    } catch (error) {
        console.error('Generation error:', error);
        alert(`Error: ${error.message}`);
    } finally {
        loading.classList.add('hidden');
        generateBtn.disabled = false;
    }
}

// Download audio
function downloadAudio() {
    if (!currentAudioBlob) return;
    
    const url = URL.createObjectURL(currentAudioBlob);
    const a = document.createElement('a');
    a.href = url;
    const format = formatSelect.value;
    a.download = `chatterbox-tts-${Date.now()}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to generate
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (!generateBtn.disabled) {
            generateAudio();
        }
    }
});
