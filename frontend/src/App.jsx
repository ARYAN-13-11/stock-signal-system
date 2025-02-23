import React, { useState, useEffect } from "react";
import { Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import { createTheme, ThemeProvider, CssBaseline, Button, CircularProgress } from "@mui/material";
import NavBar from "./components/NavBar";
import Market from "./pages/Market";
import Signals from "./pages/Signals";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import { checkLogin, logout } from "./api/auth";

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // ✅ Check login status on app load
  useEffect(() => {
    const fetchLoginStatus = async () => {
      try {
        const response = await checkLogin();
        if (response.logged_in) {
          setLoggedInUser(response.username);
        } else {
          setLoggedInUser(null);
        }
      } catch (error) {
        console.error("❌ Login Check Error:", error);
        setLoggedInUser(null);
      }
      setLoading(false);
    };

    fetchLoginStatus();
  }, []);

  // ✅ Handle Logout (MOVED ABOVE JSX)
  const handleLogout = async () => {
    await logout();
    setLoggedInUser(null);
    navigate("/login");
  };

  // ✅ Define Material UI Theme
  const theme = createTheme({
    palette: {
      mode: darkMode ? "dark" : "light",
      primary: { main: "#4caf50" }
    }
  });

  // ✅ Show Loading Spinner While Checking Login Status
  if (loading)
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <CircularProgress />
      </div>
    );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {loggedInUser && (
        <NavBar 
          darkMode={darkMode} 
          onToggleDarkMode={() => setDarkMode(!darkMode)} 
          username={loggedInUser} 
          onLogout={handleLogout} // ✅ FIX: Now handleLogout is available
        />
      )}

      {/* ✅ Navigation Menu */}
      <nav style={{ padding: "10px", display: "flex", justifyContent: "center", gap: "10px" }}>
        {loggedInUser ? (
          <>
            <Link to="/market">📈 Market</Link>
            <Link to="/signals">📊 Signals</Link>
            <span>👤 {loggedInUser}</span>
            <Button variant="contained" color="secondary" onClick={handleLogout}>
              Logout
            </Button>
          </>
        ) : (
          <>
            <Link to="/login">🔑 Login</Link>
            <Link to="/signup">📝 Sign Up</Link>
          </>
        )}
      </nav>

      {/* ✅ Routes Setup */}
      <Routes>
        <Route path="/" element={loggedInUser ? <Navigate to="/market" /> : <Navigate to="/signup" />} />
        <Route path="/signup" element={loggedInUser ? <Navigate to="/market" /> : <Signup />} />
        <Route path="/login" element={loggedInUser ? <Navigate to="/market" /> : <Login onLogin={setLoggedInUser} />} />

        {loggedInUser ? (
          <>
            <Route path="/market" element={<Market />} />
            <Route path="/signals" element={<Signals />} />
          </>
        ) : (
          <Route path="*" element={<Navigate to="/signup" />} />
        )}
      </Routes>
    </ThemeProvider>
  );
}

export default App;
