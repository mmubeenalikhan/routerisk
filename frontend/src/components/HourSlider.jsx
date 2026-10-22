import { useEffect, useState } from "react";
import { Box, IconButton, Slider, Stack, Typography } from "@mui/material";
import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { formatTime } from "../display";

const PLAY_STEP_MS = 400;

export default function HourSlider({ hour, onChange, start, hours }) {
  const [playing, setPlaying] = useState(false);
  const lastHour = hours - 1;
  const isPlaying = playing && hour < lastHour;

  useEffect(() => {
    if (!isPlaying) return;
    const timer = setInterval(() => onChange(h => Math.min(h + 1, lastHour)), PLAY_STEP_MS);
    return () => clearInterval(timer);
  }, [isPlaying, onChange, lastHour]);

  function togglePlay() {
    if (isPlaying) {
      setPlaying(false);
      return;
    }
    if (hour === lastHour) onChange(0);
    setPlaying(true);
  }

  function handleDrag(_, value) {
    setPlaying(false);
    onChange(value);
  }

  const clockTime = new Date(new Date(start).getTime() + hour * 3600 * 1000);
  return (
    <Box sx={{px: 2, py: 1, borderTop: 1, borderColor: "divider"}}>
      <Stack direction="row" spacing={2} sx={{alignItems: "center" }}>
        <IconButton onClick={togglePlay} aria-label={isPlaying ? "Pause" : "Play"} color="primary">
          {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
        </IconButton>
        <Slider value={hour} min={0} max={lastHour} step={1} onChange={handleDrag} aria-label="Forecast hour" />
        <Typography sx={{ minWidth: 150, fontWeight: 600 }}>
          +{hour}H · {formatTime(clockTime)}
        </Typography>
      </Stack>
      <Typography variant="caption" color="text.secondary">
        Heatmap and trucks show forecast conditions at this hour. The recommendation uses each checkpoint's own ETA and
        doesn't change.
      </Typography>
    </Box>
  );
}
