import React from "react";
import { AppBar, Toolbar, Typography, Box, Button, Switch } from "@mui/material";
import { Link } from "react-router-dom";

function NavBar({ darkMode, onToggleDarkMode, username, onLogout }) {
  return (
    <AppBar position="static">
      <Toolbar>
        <img
          src="/images/final_logo.png"
          alt="Brand Logo"
          style={{ width: 40, height: 40, marginRight: 8 }}
        />

        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Stock Signal System
        </Typography>

        {/* Dark Mode Switch */}
        <Box sx={{ marginRight: 2 }}>
          <Switch
            checked={darkMode}
            onChange={onToggleDarkMode}
            color="default"
          />
        </Box>

        <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
          <Button color="inherit" component={Link} to="/market">
            Market
          </Button>
          <Button color="inherit" component={Link} to="/signals">
            Signals
          </Button>
          {username && (
            <>
              <Typography variant="subtitle1" sx={{ marginLeft: 2 }}>
                👤 {username}
              </Typography>
              <Button color="inherit" onClick={onLogout}>
                Logout
              </Button>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default NavBar;
