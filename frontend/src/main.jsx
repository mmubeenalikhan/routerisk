import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import "leaflet/dist/leaflet.css";
import "./index.css";
import App from "./App.jsx";

const theme = createTheme({
  palette: { primary: { main: "#1565c0" } },
  shape: { borderRadius: 6 },
  typography: { button: { textTransform: "none", fontWeight: 600 } },
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </StrictMode>,
);
