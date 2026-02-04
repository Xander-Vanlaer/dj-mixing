// Keyboard shortcuts configuration
export const KEYBOARD_SHORTCUTS = {
  // Deck A controls
  deckA: {
    play: 'a',
    cue: 's',
    sync: 'd',
    pitchUp: 'w',
    pitchDown: 'q',
    volumeUp: 'e',
    volumeDown: 'r',
  },
  // Deck B controls
  deckB: {
    play: 'k',
    cue: 'l',
    sync: ';',
    pitchUp: 'i',
    pitchDown: 'u',
    volumeUp: 'o',
    volumeDown: 'p',
  },
  // Mixer controls
  mixer: {
    crossfaderLeft: 'ArrowLeft',
    crossfaderRight: 'ArrowRight',
    crossfaderCenter: 'ArrowDown',
    masterVolumeUp: '+',
    masterVolumeDown: '-',
  },
  // Global controls
  global: {
    help: '?',
    library: 't',
    mixer: 'm',
  },
};

export const formatDuration = (seconds) => {
  if (!seconds) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export const formatFileSize = (bytes) => {
  if (!bytes) return '0 B';
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
};

export const getBPMColor = (bpm) => {
  if (!bpm) return '#666';
  if (bpm < 100) return '#4caf50'; // Green - slow
  if (bpm < 130) return '#2196f3'; // Blue - medium
  if (bpm < 150) return '#ff9800'; // Orange - fast
  return '#f44336'; // Red - very fast
};

export const getEnergyColor = (energy) => {
  if (!energy) return '#666';
  if (energy < 0.3) return '#4caf50'; // Green - chill
  if (energy < 0.6) return '#2196f3'; // Blue - moderate
  if (energy < 0.8) return '#ff9800'; // Orange - energetic
  return '#f44336'; // Red - high energy
};

export const getCompatibilityColor = (score) => {
  if (!score) return '#666';
  if (score < 50) return '#f44336'; // Red - poor
  if (score < 70) return '#ff9800'; // Orange - moderate
  if (score < 85) return '#2196f3'; // Blue - good
  return '#4caf50'; // Green - excellent
};

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};
