import { useEffect } from "react";
import L from "leaflet";
import { Box, Paper, Stack, Typography } from "@mui/material";
import { CircleMarker, MapContainer, Marker, Polyline, Popup, Rectangle, TileLayer, useMap } from "react-leaflet";
import { RISK_COLORS, RISK_LABELS, RISK_LEVELS, formatTime, riskFromLevel } from "../display";

const US_CENTER = [39.5, -96];
const TRUCK_SIZE = 30;
const truckIcon = L.divIcon({
  className: "truck-icon",
  iconSize: [TRUCK_SIZE, TRUCK_SIZE],
  html: "🚚",
});

function FitToRoutes({ routes }) {
  const map = useMap();
  useEffect(() => {
    const points = routes.flatMap(route => route.segments.flatMap(segment => segment.path));
    if (points.length) map.fitBounds(points, { padding: [30, 30] });
  }, [map, routes]);
  return null;
}

function HeatmapLayer({ heatmap, hour }) {
  const half = heatmap.cell_deg / 2;
  const riskySquares = heatmap.cells.filter(cell => cell.risk[hour] > 1);
  return riskySquares.map(cell => (
    <Rectangle
      key={`${cell.lat},${cell.lon}`}
      bounds={[
        [cell.lat - half, cell.lon - half],
        [cell.lat + half, cell.lon + half],
      ]}
      pathOptions={{ stroke: false, fillColor: RISK_COLORS[riskFromLevel(cell.risk[hour])], fillOpacity: 0.40 }}
    />
  ));
}

function RouteLines({ routes, selectedId, onSelect }) {
  const drawOrder = [...routes].sort((a, b) => (a.id === selectedId) - (b.id === selectedId));
  return drawOrder.map(route =>
    route.segments.map((segment, i) => (
      <Polyline
        key={`${route.id}-${i}`}
        positions={segment.path}
        eventHandlers={{ click: () => onSelect(route.id) }}
        pathOptions={{
          color: RISK_COLORS[segment.risk],
          weight: route.id === selectedId ? 6 : 4,
          opacity: route.id === selectedId ? 1 : 0.35,
        }}
      />
    )),
  );
}

function CheckpointPopup({ checkpoint }) {
  return (
    <Box>
      <Typography variant="subtitle2">Miles: {Math.round(checkpoint.mile)}</Typography>
      <Typography variant="body2">Risk: {RISK_LABELS[checkpoint.risk]}</Typography>
      <Typography variant="body2">ETA: {formatTime(checkpoint.eta)}</Typography>
      <Typography variant="body2">Wind: {checkpoint.wind_mph} mph</Typography>
      <Typography variant="body2">Rain: {checkpoint.rain_in_hr} in/hr</Typography>
      <Typography variant="body2">Snow: {checkpoint.snow_in_hr} in/hr</Typography>
    </Box>
  );
}

function CheckpointMarkers({ route }) {
  return route.checkpoints.map(checkpoint => (
    <CircleMarker
      key={checkpoint.mile}
      center={[checkpoint.lat, checkpoint.lon]}
      radius={5}
      pathOptions={{ color: "#222", weight: 1, fillColor: RISK_COLORS[checkpoint.risk], fillOpacity: 1 }}
    >
      <Popup>
        <CheckpointPopup checkpoint={checkpoint} />
      </Popup>
    </CircleMarker>
  ));
}

const truckPosition = (route, hour) => route.checkpoints.filter(cp => cp.elapsed_h <= hour).pop();

function TruckMarkers({ routes, selectedId, hour }) {
  return routes.map(route => {
    const checkpoint = truckPosition(route, hour);
    return (
      <Marker
        key={route.id}
        position={[checkpoint.lat, checkpoint.lon]}
        icon={truckIcon}
        opacity={route.id === selectedId ? 1 : 0.5}
        zIndexOffset={route.id === selectedId ? 1000 : 0}
      />
    );
  });
}

function Legend() {
  return (
    <Paper elevation={3} sx={{ position: "absolute", right: 10, bottom: 24, zIndex: 1000, px: 1.5, py: 1 }}>
      {RISK_LEVELS.map(level => (
        <Stack key={level} direction="row" spacing={1} sx={{ alignItems: "center" }}>
          <Box sx={{ width: 12, height: 12, bgcolor: RISK_COLORS[level] }} />
          <Typography variant="body2">{RISK_LABELS[level]}</Typography>
        </Stack>
      ))}
    </Paper>
  );
}

export default function MapView({ plan, selectedId, onSelect, hour }) {
  const selectedRoute = plan?.routes.find(route => route.id === selectedId);
  return (
    <Box sx={{ flex: 1, position: "relative" }}>
      <MapContainer center={US_CENTER} zoom={4} preferCanvas className="map">
        <TileLayer
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {plan && (
          <>
            <FitToRoutes routes={plan.routes} />
            <HeatmapLayer heatmap={plan.heatmap} hour={hour} />
            <RouteLines routes={plan.routes} selectedId={selectedId} onSelect={onSelect} />
            {selectedRoute && <CheckpointMarkers route={selectedRoute} />}
            <TruckMarkers routes={plan.routes} selectedId={selectedId} hour={hour} />
          </>
        )}
      </MapContainer>
      <Legend />
    </Box>
  );
}
