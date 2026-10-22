import { useEffect, useState } from "react";
import { Alert, Box, LinearProgress, Stack, Typography } from "@mui/material";
import { checkHealth, planTrip } from "./api";
import HourSlider from "./components/HourSlider";
import MapView from "./components/MapView";
import RouteCards from "./components/RouteCards";
import TripForm from "./components/TripForm";

const WAKING_NOTICE_DELAY_MS = 1500;

function useServerWaking() {
  const [waking, setWaking] = useState(false);
  useEffect(() => {
    const timer = setTimeout(() => setWaking(true), WAKING_NOTICE_DELAY_MS);
    checkHealth()
      .catch(() => {})
      .finally(() => {
        clearTimeout(timer);
        setWaking(false);
      });
  }, []);
  return waking;
}

function TripResults({ plan, selectedId, onSelect }) {
  return (
    <Stack spacing={1.5}>
      {plan.all_blocked && <Alert severity="error">{plan.message}</Alert>}
      {plan.warnings.map(warning => (
        <Alert key={warning} severity="warning">
          {warning}
        </Alert>
      ))}
      <RouteCards routes={plan.routes} selectedId={selectedId} onSelect={onSelect} />
    </Stack>
  );
}

export default function App() {
  const [plan, setPlan] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [hour, setHour] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const serverWaking = useServerWaking();

  async function handlePlan(trip) {
    setLoading(true);
    setError("");
    try {
      const result = await planTrip(trip);
      setPlan(result);
      setSelectedId(result.recommended_route_id ?? result.routes[0].id);
      setHour(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box sx={{ display: "flex", flexDirection: { xs: "column", md: "row" }, height: "100vh" }}>
      <Stack
        component="aside"
        spacing={2}
        sx={{
          width: { xs: "100%", md: 380 },
          maxHeight: { xs: "45vh", md: "none" },
          flexShrink: 0,
          overflowY: "auto",
          p: 2,
          bgcolor: "grey.50",
          borderRight: { md: 1 },
          borderBottom: { xs: 1, md: 0 },
          borderColor: "divider",
        }}
      >

        <div>
          <Typography variant="h6" component="h1" sx={{ lineHeight: 1.2 }}>
            RouteRisk
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Weather-aware truck routing
          </Typography>
        </div>
        {serverWaking && <Alert severity="info">Waking up the server, this can take up to a minute...</Alert>}
        <TripForm onSubmit={handlePlan} loading={loading} />
        {loading && (
          <Box>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Finding routes and checking the weather along each one...
            </Typography>
          </Box>
        )}
        {error && <Alert severity="error">{error}</Alert>}
        {plan && !loading && <TripResults plan={plan} selectedId={selectedId} onSelect={setSelectedId} />}
      </Stack>
      <Box component="main" sx={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, minHeight: 0 }}>
        <MapView plan={plan} selectedId={selectedId} onSelect={setSelectedId} hour={hour} />
        {plan && <HourSlider hour={hour} onChange={setHour} start={plan.heatmap.start} hours={plan.heatmap.hours} />}
      </Box>
    </Box>
  );
}
