/**
 * Chatterbox ES-LATAM Client SDK
 * 
 * SDK for local TTS inference on Surface tablets.
 * 
 * @example
 * ```typescript
 * import { ChatterboxTTS, detectCapability } from '@neufitech/chatterbox-client';
 * 
 * const tts = await ChatterboxTTS.create();
 * await tts.loadVoice('./voices/user.onnx');
 * await tts.speak("Hola mundo");
 * ```
 * 
 * @packageDocumentation
 */

// TODO: Implement in Phase 3

export type TTSCapability = 'npu' | 'directml' | 'cpu' | 'webspeech';

export interface TTSOptions {
    modelsPath?: string;
    backend?: 'auto' | TTSCapability;
    sampleRate?: number;
    debug?: boolean;
}

export interface SynthesisOptions {
    temperature?: number;
    topP?: number;
    maxLength?: number;
}

export interface SpeakOptions extends SynthesisOptions {
    volume?: number;
}

export interface VoiceInfo {
    id: string;
    name: string;
    path: string;
    loadedAt: Date;
}

export interface LocalVoice {
    id: string;
    name: string;
    path: string;
    size: number;
    createdAt: Date;
}

/**
 * Detect the TTS capability of the current device.
 */
export async function detectCapability(): Promise<TTSCapability> {
    // TODO: Implement actual detection
    // For now, return webspeech as fallback

    // Check for NPU (Surface Pro 11)
    // Check for DirectML
    // Check RAM availability

    return 'webspeech';
}

/**
 * Check if Chatterbox TTS is supported on this device.
 */
export function isSupported(): boolean {
    // Check for required APIs
    return typeof window !== 'undefined' &&
        'speechSynthesis' in window;
}

/**
 * Main TTS class for synthesis.
 * 
 * @example
 * ```typescript
 * const tts = await ChatterboxTTS.create();
 * await tts.speak("Hello world");
 * ```
 */
export class ChatterboxTTS {
    private options: TTSOptions;
    private capability: TTSCapability = 'webspeech';
    private currentVoice: VoiceInfo | null = null;
    private initialized = false;

    private constructor(options: TTSOptions) {
        this.options = {
            modelsPath: './models',
            backend: 'auto',
            sampleRate: 24000,
            debug: false,
            ...options
        };
    }

    /**
     * Create a new ChatterboxTTS instance.
     */
    static async create(options: TTSOptions = {}): Promise<ChatterboxTTS> {
        const instance = new ChatterboxTTS(options);
        await instance.initialize();
        return instance;
    }

    private async initialize(): Promise<void> {
        this.capability = await detectCapability();

        if (this.options.debug) {
            console.log(`ChatterboxTTS initialized with capability: ${this.capability}`);
        }

        // TODO: Load ONNX models if not webspeech

        this.initialized = true;
    }

    /**
     * Load a voice file.
     */
    async loadVoice(voicePath: string): Promise<void> {
        if (this.capability === 'webspeech') {
            console.warn('WebSpeech fallback does not support custom voices');
            return;
        }

        // TODO: Implement ONNX voice loading

        this.currentVoice = {
            id: 'placeholder',
            name: voicePath.split('/').pop() || 'Unknown',
            path: voicePath,
            loadedAt: new Date()
        };
    }

    /**
     * Download a voice from the server.
     */
    async downloadVoice(serverUrl: string, voiceId: string): Promise<string> {
        // TODO: Implement download
        throw new Error('Not implemented yet');
    }

    /**
     * Synthesize text to audio buffer.
     */
    async synthesize(text: string, options: SynthesisOptions = {}): Promise<AudioBuffer> {
        // TODO: Implement ONNX inference
        throw new Error('Not implemented yet');
    }

    /**
     * Synthesize and play audio.
     */
    async speak(text: string, options: SpeakOptions = {}): Promise<void> {
        if (this.capability === 'webspeech') {
            return this.speakWebSpeech(text, options.volume || 1.0);
        }

        // TODO: Implement ONNX inference + playback
        throw new Error('Not implemented yet');
    }

    private speakWebSpeech(text: string, volume: number): Promise<void> {
        return new Promise((resolve, reject) => {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.volume = volume;
            utterance.onend = () => resolve();
            utterance.onerror = (e) => reject(e);
            window.speechSynthesis.speak(utterance);
        });
    }

    /**
     * Stop current playback.
     */
    stop(): void {
        window.speechSynthesis.cancel();
    }

    /**
     * Get the detected capability.
     */
    getCapability(): TTSCapability {
        return this.capability;
    }

    /**
     * Check if TTS is ready.
     */
    isReady(): boolean {
        return this.initialized;
    }

    /**
     * Get current voice info.
     */
    getCurrentVoice(): VoiceInfo | null {
        return this.currentVoice;
    }
}

/**
 * Voice management utilities.
 */
export class VoiceManager {
    private static instance: VoiceManager;

    private constructor() { }

    static getInstance(): VoiceManager {
        if (!VoiceManager.instance) {
            VoiceManager.instance = new VoiceManager();
        }
        return VoiceManager.instance;
    }

    /**
     * List all local voices.
     */
    async listVoices(): Promise<LocalVoice[]> {
        // TODO: Implement
        return [];
    }

    /**
     * Delete a local voice.
     */
    async deleteVoice(voiceId: string): Promise<void> {
        // TODO: Implement
    }

    /**
     * Get voice info.
     */
    async getVoiceInfo(voiceId: string): Promise<LocalVoice | null> {
        // TODO: Implement
        return null;
    }
}

// Default export
export default ChatterboxTTS;
