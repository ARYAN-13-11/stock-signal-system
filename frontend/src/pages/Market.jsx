import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Button,
} from "@mui/material";
import StockChart from "./StockChart"; // Import candlestick chart component

const API_URL = "http://127.0.0.1:5000";

const Market = () => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState("");
  const [error, setError] = useState("");
  const [selectedStock, setSelectedStock] = useState(null); // Track selected stock for chart

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_URL}/live_prices`);
        if (response.data && response.data.length > 0) {
          setStocks(response.data);
          setLastUpdated(new Date().toLocaleTimeString());
          setError(""); // Reset error if successful
        } else {
          setStocks([]);
          setError("No data available");
        }
      } catch (err) {
        setError("❌ Failed to fetch live prices. Check API connection.");
      }
      setLoading(false);
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Container sx={{ marginTop: 3 }}>
      <Typography variant="h4" gutterBottom>
        📈 Live Market Data
      </Typography>

      <Typography variant="subtitle1" color="textSecondary">
        Last Updated: {lastUpdated}
      </Typography>

      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Alert severity="error" sx={{ marginTop: 2 }}>
          {error}
        </Alert>
      ) : (
        <Grid container spacing={2}>
          {stocks.map((stock) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={stock.symbol}>
              <Card elevation={3} sx={{ padding: 2, textAlign: "center" }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                    {stock.symbol}
                  </Typography>
                  <Typography variant="h5" color="primary">
                    ${stock.price ? stock.price.toFixed(2) : "N/A"}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Prev Close: ${stock.prev_close ? stock.prev_close.toFixed(2) : "N/A"}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Timestamp: {stock.timestamp ? stock.timestamp : "N/A"}
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    sx={{ marginTop: 1 }}
                    onClick={() => setSelectedStock(stock.symbol)}
                  >
                    View Chart
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Candlestick Chart Display */}
      {selectedStock && (
        <StockChart stockSymbol={selectedStock} onClose={() => setSelectedStock(null)} />
      )}
    </Container>
  );
};

export default Market;
