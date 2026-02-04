import React from 'react';
import { Box, Typography, Slider, Divider } from '@mui/material';
import useMixerStore from '../contexts/mixerStore';

const Mixer = () => {
  const { crossfader, masterVolume, eqA, eqB, setCrossfader, setMasterVolume, setEQ } =
    useMixerStore();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 3 }}>
      <Typography variant="h6" align="center">
        Mixer
      </Typography>

      {/* EQ Deck A */}
      <Box>
        <Typography variant="caption" color="primary">
          Deck A EQ
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption">High</Typography>
          <Slider
            value={eqA.high}
            onChange={(e, value) => setEQ('deckA', 'high', value)}
            min={-12}
            max={12}
            step={1}
            marks
            size="small"
            orientation="vertical"
            sx={{ height: 80 }}
          />
        </Box>
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption">Mid</Typography>
          <Slider
            value={eqA.mid}
            onChange={(e, value) => setEQ('deckA', 'mid', value)}
            min={-12}
            max={12}
            step={1}
            marks
            size="small"
            orientation="vertical"
            sx={{ height: 80 }}
          />
        </Box>
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption">Low</Typography>
          <Slider
            value={eqA.low}
            onChange={(e, value) => setEQ('deckA', 'low', value)}
            min={-12}
            max={12}
            step={1}
            marks
            size="small"
            orientation="vertical"
            sx={{ height: 80 }}
          />
        </Box>
      </Box>

      <Divider />

      {/* Crossfader */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Typography variant="caption" align="center" gutterBottom>
          Crossfader
        </Typography>
        <Slider
          value={crossfader * 100}
          onChange={(e, value) => setCrossfader(value / 100)}
          min={0}
          max={100}
          step={1}
          marks={[
            { value: 0, label: 'A' },
            { value: 50, label: '50' },
            { value: 100, label: 'B' },
          ]}
        />
      </Box>

      <Divider />

      {/* EQ Deck B */}
      <Box>
        <Typography variant="caption" color="secondary">
          Deck B EQ
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption">High</Typography>
          <Slider
            value={eqB.high}
            onChange={(e, value) => setEQ('deckB', 'high', value)}
            min={-12}
            max={12}
            step={1}
            marks
            size="small"
            orientation="vertical"
            sx={{ height: 80 }}
          />
        </Box>
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption">Mid</Typography>
          <Slider
            value={eqB.mid}
            onChange={(e, value) => setEQ('deckB', 'mid', value)}
            min={-12}
            max={12}
            step={1}
            marks
            size="small"
            orientation="vertical"
            sx={{ height: 80 }}
          />
        </Box>
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption">Low</Typography>
          <Slider
            value={eqB.low}
            onChange={(e, value) => setEQ('deckB', 'low', value)}
            min={-12}
            max={12}
            step={1}
            marks
            size="small"
            orientation="vertical"
            sx={{ height: 80 }}
          />
        </Box>
      </Box>

      <Divider />

      {/* Master Volume */}
      <Box>
        <Typography variant="caption" align="center" display="block" gutterBottom>
          Master Volume
        </Typography>
        <Slider
          value={masterVolume * 100}
          onChange={(e, value) => setMasterVolume(value / 100)}
          min={0}
          max={100}
          step={1}
          marks
        />
      </Box>
    </Box>
  );
};

export default Mixer;
