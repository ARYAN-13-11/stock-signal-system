// src/StockSignals.js
import React, { useState } from "react";

function StockSignals() {
  const [ticker, setTicker] = useState("");
  const [signalData, setSignalData] = useState(null);
  const [metricsData, setMetricsData] = useState(null);
  const [error, setError] = useState("");

  const handleInputChange = (e) => {
    setTicker(e.target.value);
  };

  const fetchSignal = async () => {
    try {
      setError("");
      setSignalData(null);
      setMetricsData(null);

      // e.g. "/signal/AAPL" 
      // If using proxy, we can do fetch(`/signal/${ticker}`)
      // Otherwise: `fetch(`http://127.0.0.1:5000/signal/${ticker}`)`
      const resp = await fetch(`/signal/${ticker}`);
      const data = await resp.json();
      if (resp.ok) {
        setSignalData(data);
      } else {
        setError(data.error || "Error fetching signal");
      }
    } catch (err) {
      setError("Error: " + err.message);
    }
  };

  const fetchMetrics = async () => {
    try {
      setError("");
      setMetricsData(null);

      const resp = await fetch(`/metrics/${ticker}`);
      const data = await resp.json();
      if (resp.ok) {
        setMetricsData(data);
      } else {
        setError(data.error || "Error fetching metrics");
      }
    } catch (err) {
      setError("Error: " + err.message);
    }
  };

  return (
    <div style={{ margin: "20px" }}>
      <h2>Stock Signal Generator</h2>
      <input
        type="text"
        value={ticker}
        onChange={handleInputChange}
        placeholder="Enter Ticker Symbol (e.g. AAPL)"
      />
      <button onClick={fetchSignal} style={{ marginLeft: "10px" }}>
        Get Signal
      </button>
      <button onClick={fetchMetrics} style={{ marginLeft: "10px" }}>
        Get Metrics
      </button>

      {error && <div style={{ color: "red" }}>Error: {error}</div>}

      {signalData && (
        <div style={{ marginTop: "20px" }}>
          <h3>Signal for {signalData.ticker}:</h3>
          <p>{signalData.signal}</p>
        </div>
      )}

      {metricsData && (
        <div style={{ marginTop: "20px" }}>
          <h3>Metrics for {metricsData.ticker}:</h3>
          <ul>
            <li>Final Cash: {metricsData["Final Cash"]}</li>
            <li>Total PnL: {metricsData["Total PnL"]}</li>
            <li>Win Rate: {metricsData["Win Rate"]} %</li>
            <li>Num Trades: {metricsData["Num Trades"]}</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default StockSignals;
