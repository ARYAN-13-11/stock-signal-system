import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Container, TextField, Button, Typography, Box, CircularProgress, Alert } from "@mui/material";
import { login } from "../api/auth";

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!username || !password) {
      setError("Please enter both username and password.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await login(username, password);
      if (response.message === "Login successful") {
        localStorage.setItem("username", username);  // Save user state
        onLogin(username);
        navigate("/");  // Redirect to dashboard
      } else {
        setError(response.error || "Invalid credentials");
      }
    } catch (err) {
      setError("Failed to connect to server");
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="xs">
      <Box textAlign="center" p={4} mt={5} sx={{ backgroundColor: "white", borderRadius: 3, boxShadow: 3 }}>
        <Typography variant="h4" gutterBottom>🔐 Login</Typography>

        {error && <Alert severity="error">{error}</Alert>}

        <TextField
          fullWidth
          margin="normal"
          label="Username"
          variant="outlined"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <TextField
          fullWidth
          margin="normal"
          label="Password"
          variant="outlined"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <Button
          fullWidth
          variant="contained"
          color="primary"
          onClick={handleLogin}
          disabled={loading}
          sx={{ mt: 2 }}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : "Login"}
        </Button>

        <Typography variant="body2" mt={2}>
          New User? <Link to="/signup">Create an account</Link>
        </Typography>
      </Box>
    </Container>
  );
}

export default Login;
