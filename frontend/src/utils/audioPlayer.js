/**
 * Web Audio API based audio player for DJ decks
 * Provides low-latency playback, pitch shifting, and audio effects
 */

class AudioPlayer {
  constructor() {
    this.audioContext = null;
    this.sourceNode = null;
    this.gainNode = null;
    this.filterNode = null;
    this.analyserNode = null;
    this.audioBuffer = null;
    this.startTime = 0;
    this.pauseTime = 0;
    this.isPlaying = false;
    this.playbackRate = 1.0;
    this.volume = 0.8;
  }

  async initialize() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.setupAudioNodes();
    }
  }

  setupAudioNodes() {
    // Create gain node for volume control
    this.gainNode = this.audioContext.createGain();
    this.gainNode.gain.value = this.volume;

    // Create filter node for EQ
    this.filterNode = this.audioContext.createBiquadFilter();
    this.filterNode.type = 'lowshelf';
    this.filterNode.frequency.value = 320;

    // Create analyser for waveform visualization
    this.analyserNode = this.audioContext.createAnalyser();
    this.analyserNode.fftSize = 2048;

    // Connect nodes
    this.gainNode.connect(this.filterNode);
    this.filterNode.connect(this.analyserNode);
    this.analyserNode.connect(this.audioContext.destination);
  }

  async loadAudio(audioUrl) {
    try {
      const response = await fetch(audioUrl);
      const arrayBuffer = await response.arrayBuffer();
      this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      return this.audioBuffer.duration;
    } catch (error) {
      console.error('Error loading audio:', error);
      throw error;
    }
  }

  play() {
    if (!this.audioBuffer || this.isPlaying) return;

    // Create new source node
    this.sourceNode = this.audioContext.createBufferSource();
    this.sourceNode.buffer = this.audioBuffer;
    this.sourceNode.playbackRate.value = this.playbackRate;
    this.sourceNode.connect(this.gainNode);

    // Start playback
    const offset = this.pauseTime;
    this.sourceNode.start(0, offset);
    this.startTime = this.audioContext.currentTime - offset;
    this.isPlaying = true;
  }

  pause() {
    if (!this.isPlaying) return;

    this.pauseTime = this.audioContext.currentTime - this.startTime;
    this.sourceNode.stop();
    this.isPlaying = false;
  }

  stop() {
    if (this.sourceNode) {
      this.sourceNode.stop();
    }
    this.pauseTime = 0;
    this.startTime = 0;
    this.isPlaying = false;
  }

  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
    if (this.gainNode) {
      this.gainNode.gain.value = this.volume;
    }
  }

  setPitch(pitchPercent) {
    // Convert pitch percentage to playback rate
    // -8% to +8% -> 0.92 to 1.08
    this.playbackRate = 1 + (pitchPercent / 100);
    if (this.sourceNode) {
      this.sourceNode.playbackRate.value = this.playbackRate;
    }
  }

  getCurrentTime() {
    if (this.isPlaying) {
      return this.audioContext.currentTime - this.startTime;
    }
    return this.pauseTime;
  }

  seek(time) {
    const wasPlaying = this.isPlaying;
    if (wasPlaying) {
      this.pause();
    }
    this.pauseTime = Math.max(0, Math.min(time, this.audioBuffer.duration));
    if (wasPlaying) {
      this.play();
    }
  }

  setEQ(band, value) {
    // Simplified EQ - would need multiple filter nodes for full 3-band EQ
    if (this.filterNode) {
      if (band === 'low') {
        this.filterNode.type = 'lowshelf';
        this.filterNode.gain.value = value;
      }
    }
  }

  getWaveformData() {
    if (!this.analyserNode) return null;

    const bufferLength = this.analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyserNode.getByteTimeDomainData(dataArray);
    return dataArray;
  }

  getFrequencyData() {
    if (!this.analyserNode) return null;

    const bufferLength = this.analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyserNode.getByteFrequencyData(dataArray);
    return dataArray;
  }

  dispose() {
    this.stop();
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }
}

export default AudioPlayer;
