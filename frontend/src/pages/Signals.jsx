import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Switch,
  FormControlLabel,
  CircularProgress,
  Alert,
} from "@mui/material";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

function Signals() {
  const [ticker, setTicker] = useState("");
  const [signalData, setSignalData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");

  const [loadingSignal, setLoadingSignal] = useState(false);
  const [loadingMetrics, setLoadingMetrics] = useState(false);
  const [progress, setProgress] = useState(0);
  const [darkMode, setDarkMode] = useState(false);

  let progressInterval = null;

  const handleThemeToggle = (e) => {
    setDarkMode(e.target.checked);
  };

  const handleChange = (e) => {
    setTicker(e.target.value.toUpperCase());
  };

  const fetchSignal = async () => {
    setError("");
    setSignalData(null);
    setLoadingSignal(true);
    try {
      const response = await axios.get(`${API_URL}/signal/${ticker}`);
      setSignalData(response.data);
    } catch (err) {
      setError("❌ Error fetching signal. Check API or symbol.");
    }
    setLoadingSignal(false);
  };

  const fetchMetrics = async () => {
    setError("");
    setMetrics(null);
    setLoadingMetrics(true);
    setProgress(0);

    progressInterval = setInterval(() => {
      setProgress((prev) => (prev >= 95 ? 95 : prev + 3));
    }, 400);

    try {
      const response = await axios.get(`${API_URL}/metrics/${ticker}`);
      setMetrics(response.data);
    } catch (err) {
      setError("❌ Error fetching metrics. Check API.");
    }

    clearInterval(progressInterval);
    setProgress(100);
    setLoadingMetrics(false);
  };

  useEffect(() => {
    return () => {
      if (progressInterval) clearInterval(progressInterval);
    };
  }, []);

  return (
    <Container sx={{ marginTop: 3 }}>
      <FormControlLabel
        control={<Switch checked={darkMode} onChange={handleThemeToggle} color="primary" />}
        label="Dark Mode"
      />

      <Typography variant="h4" gutterBottom>
        📊 Stock Signals & Backtest Metrics
      </Typography>

      <TextField
        label="Enter Stock Symbol"
        value={ticker}
        onChange={handleChange}
        sx={{ marginRight: 2 }}
      />
      <Button variant="contained" onClick={fetchSignal}>
        Get Signal
      </Button>
      <Button variant="contained" onClick={fetchMetrics} sx={{ marginLeft: 2 }}>
        Get Metrics
      </Button>

      {error && <Alert severity="error" sx={{ marginTop: 2 }}>{error}</Alert>}

      {loadingSignal && <CircularProgress sx={{ marginTop: 2 }} />}

      {signalData && !error && (
        <Card sx={{ marginTop: 3 }}>
          <CardContent>
            <Typography variant="h6">
              Signal for {signalData.ticker}: {signalData.signal}
            </Typography>
            <Typography>Current Price: ${signalData.currentPrice ?? "N/A"}</Typography>
            <Typography>Recommended Entry: ${signalData.recommendedEntry ?? "N/A"}</Typography>
            <Typography>Stop Loss: ${signalData.stopLoss ?? "N/A"}</Typography>
            <Typography>Take Profit: ${signalData.takeProfit ?? "N/A"}</Typography>
            <Typography color="text.secondary" sx={{ marginTop: 1 }}>
              Explanation: {signalData.explanation ?? "No explanation available."}
            </Typography>
          </CardContent>
        </Card>
      )}

      {loadingMetrics && (
        <div style={{ marginTop: "20px" }}>
          <Typography>Fetching metrics... {progress}%</Typography>
          <LinearProgress variant="determinate" value={progress} />
        </div>
      )}

      {metrics && !loadingMetrics && (
        <Card sx={{ marginTop: 3 }}>
          <CardContent>
            <Typography variant="h6">Metrics for {ticker}</Typography>
            <Typography>Final Value: ${metrics["Final Value"]?.toFixed(2) ?? "N/A"}</Typography>
            <Typography>
              Total PnL: 
              <span style={{ color: metrics["Total PnL"] > 0 ? "green" : "red" }}>
                ${metrics["Total PnL"]?.toFixed(2) ?? "N/A"}
              </span>
            </Typography>
            <Typography>Win Rate: {metrics["Win Rate"]?.toFixed(2) ?? "N/A"}%</Typography>
            <Typography>Num Trades: {metrics["Num Trades"] ?? "N/A"}</Typography>
          </CardContent>
        </Card>
      )}
    </Container>
  );
}

export default Signals;
