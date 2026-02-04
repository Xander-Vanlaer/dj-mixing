import { create } from 'zustand';

const useMixerStore = create((set, get) => ({
  // Deck states
  deckA: {
    track: null,
    isPlaying: false,
    volume: 0.8,
    pitch: 0,
    position: 0,
    cuePoints: [],
  },
  deckB: {
    track: null,
    isPlaying: false,
    volume: 0.8,
    pitch: 0,
    position: 0,
    cuePoints: [],
  },
  
  // Mixer state
  crossfader: 0.5, // 0 = full deck A, 1 = full deck B
  masterVolume: 0.8,
  
  // EQ states (per deck)
  eqA: {
    high: 0,
    mid: 0,
    low: 0,
  },
  eqB: {
    high: 0,
    mid: 0,
    low: 0,
  },
  
  // Track library
  tracks: [],
  
  // Actions
  loadTrack: (deck, track) => {
    set((state) => ({
      [deck]: {
        ...state[deck],
        track,
        position: 0,
      },
    }));
  },
  
  togglePlay: (deck) => {
    set((state) => ({
      [deck]: {
        ...state[deck],
        isPlaying: !state[deck].isPlaying,
      },
    }));
  },
  
  setVolume: (deck, volume) => {
    set((state) => ({
      [deck]: {
        ...state[deck],
        volume,
      },
    }));
  },
  
  setPitch: (deck, pitch) => {
    set((state) => ({
      [deck]: {
        ...state[deck],
        pitch,
      },
    }));
  },
  
  setPosition: (deck, position) => {
    set((state) => ({
      [deck]: {
        ...state[deck],
        position,
      },
    }));
  },
  
  setCrossfader: (value) => {
    set({ crossfader: value });
  },
  
  setMasterVolume: (volume) => {
    set({ masterVolume: volume });
  },
  
  setEQ: (deck, band, value) => {
    const eqKey = deck === 'deckA' ? 'eqA' : 'eqB';
    set((state) => ({
      [eqKey]: {
        ...state[eqKey],
        [band]: value,
      },
    }));
  },
  
  setTracks: (tracks) => {
    set({ tracks });
  },
  
  addTrack: (track) => {
    set((state) => ({
      tracks: [...state.tracks, track],
    }));
  },
  
  removeTrack: (trackId) => {
    set((state) => ({
      tracks: state.tracks.filter(t => t.id !== trackId),
    }));
  },
}));

export default useMixerStore;
