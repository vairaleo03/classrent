import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Avatar
} from '@mui/material';
import {
  School,
  AccountCircle,
  Dashboard,
  Chat,
  CalendarToday,
  MeetingRoom,
  DateRange  // NUOVO ICONA
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    handleClose();
  };

  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { text: 'Calendario', icon: <DateRange />, path: '/calendar' },  // NUOVO
    { text: 'Chat AI', icon: <Chat />, path: '/chat' },
    { text: 'Le Mie Prenotazioni', icon: <CalendarToday />, path: '/bookings' },
    { text: 'Spazi Disponibili', icon: <MeetingRoom />, path: '/spaces' }
  ];

  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        {/* Logo e Nome */}
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          onClick={() => navigate('/')}
          sx={{ mr: 2 }}
        >
          <School />
        </IconButton>
        
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 1, 
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
          onClick={() => navigate('/')}
        >
          ClassRent
        </Typography>

        {/* Menu di navigazione per utenti autenticati */}
        {isAuthenticated && (
          <Box sx={{ display: { xs: 'none', md: 'flex' }, mr: 2 }}>
            {menuItems.map((item) => (
              <Button
                key={item.text}
                color="inherit"
                startIcon={item.icon}
                onClick={() => navigate(item.path)}
                sx={{ 
                  mx: 1,
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)'
                  }
                }}
              >
                {item.text}
              </Button>
            ))}
          </Box>
        )}

        {/* Account Menu o Login */}
        {isAuthenticated ? (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ mr: 1, display: { xs: 'none', sm: 'block' } }}>
              Ciao, {user?.full_name?.split(' ')[0]}
            </Typography>
            <IconButton
              size="large"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                {user?.full_name?.charAt(0)}
              </Avatar>
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem onClick={() => { navigate('/dashboard'); handleClose(); }}>
                <Dashboard sx={{ mr: 1 }} /> Dashboard
              </MenuItem>
              <MenuItem onClick={() => { navigate('/calendar'); handleClose(); }}>
                <DateRange sx={{ mr: 1 }} /> Calendario
              </MenuItem>
              <MenuItem onClick={() => { navigate('/chat'); handleClose(); }}>
                <Chat sx={{ mr: 1 }} /> Chat AI
              </MenuItem>
              <MenuItem onClick={() => { navigate('/bookings'); handleClose(); }}>
                <CalendarToday sx={{ mr: 1 }} /> Prenotazioni
              </MenuItem>
              <MenuItem onClick={() => { navigate('/spaces'); handleClose(); }}>
                <MeetingRoom sx={{ mr: 1 }} /> Spazi
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                <AccountCircle sx={{ mr: 1 }} /> Logout
              </MenuItem>
            </Menu>
          </Box>
        ) : (
          <Box>
            <Button color="inherit" onClick={() => navigate('/login')}>
              Login
            </Button>
            <Button color="inherit" onClick={() => navigate('/register')}>
              Registrati
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;