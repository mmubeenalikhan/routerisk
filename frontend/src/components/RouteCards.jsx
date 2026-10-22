import { Box, Card, CardActionArea, CardContent, Chip, Stack, Tooltip, Typography } from "@mui/material";
import { RISK_COLORS, RISK_LABELS, RISK_LEVELS, formatDuration, formatMiles, formatTime } from "../display";

function RiskBar({ riskMiles }) {
  const total = RISK_LEVELS.reduce((sum, level) => sum + riskMiles[level], 0);
  const levels = RISK_LEVELS.filter(level => riskMiles[level] > 0);
  return (
    <Box sx={{ my: 1 }}>
      <Box sx={{ display: "flex", height: 10, borderRadius: 5, overflow: "hidden", bgcolor: "grey.200" }}>
        {levels.map(level => (
          <Tooltip key={level} title={`${RISK_LABELS[level]}: ${formatMiles(riskMiles[level])}`}>
            <Box sx={{ width: `${(riskMiles[level] / total) * 100}%`, bgcolor: RISK_COLORS[level] }} />
          </Tooltip>
        ))}
      </Box>
      <Stack direction="row" spacing={1.5} useFlexGap sx={{ flexWrap: "wrap", mt: 0.5 }}>
        {levels.map(level => (
          <Typography key={level} variant="caption" color="text.secondary">
            {RISK_LABELS[level]} {formatMiles(riskMiles[level])}
          </Typography>
        ))}
      </Stack>
    </Box>
  );
}

function RouteCard({ route, selected, onSelect }) {
  return (
    <Card variant="outlined" sx={{ borderColor: selected ? "primary.main" : "divider", borderWidth: selected ? 2 : 1 }}>
      <CardActionArea onClick={() => onSelect(route.id)}>
        <CardContent sx={{ p: 1.5, "&:last-child": { pb: 1.5 } }}>
          <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              Route {route.id}
            </Typography>
            {route.status === "recommended" && <Chip label="Recommended" color="success" size="small" />}
            {route.status === "blocked" && (
              <Chip label="No Travel" size="small" sx={{ bgcolor: RISK_COLORS.no_travel, color: "white" }} />
            )}
          </Stack>
          <Typography variant="body2" color="text.secondary">
            {formatMiles(route.distance_mi)} · {formatDuration(route.duration_s)} · arrives {formatTime(route.arrival)}
          </Typography>
          <RiskBar riskMiles={route.risk_miles} />
          <Typography variant="body2" color="text.secondary">
            Average risk: <b>{route.avg_risk.toFixed(2)}</b> (1 = Low, 5 = No Travel)
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}

export default function RouteCards({ routes, selectedId, onSelect }) {
  return (
    <Stack spacing={1}>
      {routes.map(route => (
        <RouteCard key={route.id} route={route} selected={route.id === selectedId} onSelect={onSelect} />
      ))}
    </Stack>
  );
}
