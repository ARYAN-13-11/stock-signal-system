import React, { useState, useEffect } from "react";
import { Button, Card, CardContent, Typography, CircularProgress, Select, MenuItem } from "@mui/material";
import { ResponsiveContainer, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, Line } from "recharts";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

const StockChart = ({ stockSymbol, onClose }) => {
  const [timeframe, setTimeframe] = useState("1d");
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchChartData();
  }, [stockSymbol, timeframe]);

  const fetchChartData = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await axios.get(`${API_URL}/candlestick/${stockSymbol}?timeframe=${timeframe}`);
      if (response.data.error) {
        throw new Error(response.data.error);
      }

      const formattedData = response.data.map((d) => ({
        date: d.date,
        open: d.ohlc[0],
        high: d.ohlc[1],
        low: d.ohlc[2],
        close: d.ohlc[3],
      }));

      setChartData(formattedData);
    } catch (err) {
      console.error(`❌ Error fetching candlestick data for ${stockSymbol}:`, err);
      setError("❌ API Error. Try again later.");
    }

    setLoading(false);
  };

  return (
    <Card sx={{ marginTop: 3 }}>
      <CardContent>
        <Typography variant="h5">📊 {stockSymbol} - {timeframe.toUpperCase()} Candlestick Chart</Typography>

        <Select value={timeframe} onChange={(e) => setTimeframe(e.target.value)} sx={{ marginBottom: 2 }}>
          <MenuItem value="1min">1 Min</MenuItem>
          <MenuItem value="5min">5 Min</MenuItem>
          <MenuItem value="1hr">1 Hour</MenuItem>
          <MenuItem value="1d">1 Day</MenuItem>
        </Select>

        {loading ? (
          <CircularProgress />
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={["dataMin", "dataMax"]} />
              <Tooltip />
              <Line type="monotone" dataKey="high" stroke="green" />
              <Line type="monotone" dataKey="low" stroke="red" />
              <Line type="monotone" dataKey="close" stroke="blue" />
            </LineChart>
          </ResponsiveContainer>
        )}

        <Button variant="contained" color="error" onClick={onClose} sx={{ marginTop: 2 }}>
          Close Chart
        </Button>
      </CardContent>
    </Card>
  );
};

export default StockChart;
