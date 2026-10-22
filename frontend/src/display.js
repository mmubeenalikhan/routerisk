export const RISK_LEVELS = ["low", "moderate", "high", "severe", "no_travel"];

export const RISK_COLORS = {
  low: "#2e7d32",
  moderate: "#f9a825",
  high: "#ef6c00",
  severe: "#c62828",
  no_travel: "#4a148c",
};

export const RISK_LABELS = {
  low: "Low",
  moderate: "Moderate",
  high: "High",
  severe: "Severe",
  no_travel: "No Travel",
};

export const riskFromLevel = level => RISK_LEVELS[level - 1];

const timeFormat = new Intl.DateTimeFormat([], { weekday: "short", hour: "2-digit", minute: "2-digit" });

export const formatTime = date => timeFormat.format(new Date(date));

export function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  return `${hours}h ${minutes}min`;
}

export const formatMiles = miles => `${Math.round(miles).toLocaleString()}mi`;
