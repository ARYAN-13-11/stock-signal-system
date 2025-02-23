import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signup } from "../api/auth";
import { Button, TextField, Typography, Container, Box, CircularProgress, Alert } from "@mui/material";
import toast, { Toaster } from "react-hot-toast";

const Signup = () => {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");  // ✅ Add email state
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleSignup = async () => {
        if (!username || !email || !password || !confirmPassword) {
            setError("Please fill out all fields.");
            return;
        }

        if (!email.includes("@") || !email.includes(".")) {
            setError("Invalid email format.");
            return;
        }

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const response = await fetch("http://127.0.0.1:5000/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, email, password, confirmPassword })  // ✅ Include email
            });

            const data = await response.json();

            if (response.ok) {
                toast.success("✅ Account created successfully! Redirecting to login...");
                setTimeout(() => navigate("/login"), 2000);
            } else {
                setError(data.error || "Signup failed.");
            }
        } catch (err) {
            setError("Server error. Please try again.");
        }
        setLoading(false);
    };

    return (
        <Container maxWidth="xs">
            <Toaster />
            <Box textAlign="center" p={4} mt={5} sx={{ backgroundColor: "white", borderRadius: 3, boxShadow: 3 }}>
                <Typography variant="h4" gutterBottom>📈 Stock Signal System</Typography>
                <Typography variant="h6" gutterBottom>🔑 Create an Account</Typography>

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
                    label="Email"
                    variant="outlined"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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

                <TextField
                    fullWidth
                    margin="normal"
                    label="Confirm Password"
                    variant="outlined"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                />

                <Button
                    fullWidth
                    variant="contained"
                    color="primary"
                    onClick={handleSignup}
                    disabled={loading}
                    sx={{ mt: 2 }}
                >
                    {loading ? <CircularProgress size={24} color="inherit" /> : "Sign Up"}
                </Button>

                <Typography variant="body2" mt={2}>
                    Already have an account? <Link to="/login">Login</Link>
                </Typography>
            </Box>
        </Container>
    );
};

export default Signup;
