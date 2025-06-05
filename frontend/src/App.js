import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Toaster } from 'react-hot-toast';

import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Bookings from './pages/Bookings';
import Spaces from './pages/Spaces';
import CalendarView from './components/CalendarView';  // NUOVO

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minuti
      cacheTime: 10 * 60 * 1000, // 10 minuti
    },
  },
});

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#fafafa',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  shape: {
    borderRadius: 8,
  },
});

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <div className="App">
              <Navbar />
              <Toaster 
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                  success: {
                    duration: 3000,
                    theme: {
                      primary: '#4aed88',
                    },
                  },
                  error: {
                    duration: 5000,
                    theme: {
                      primary: '#ff4b4b',
                    },
                  },
                }}
              />
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                {/* Protected Routes */}
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } />
                
                <Route path="/calendar" element={
                  <ProtectedRoute>
                    <CalendarView />
                  </ProtectedRoute>
                } />
                
                <Route path="/chat" element={
                  <ProtectedRoute>
                    <Chat />
                  </ProtectedRoute>
                } />
                
                <Route path="/bookings" element={
                  <ProtectedRoute>
                    <Bookings />
                  </ProtectedRoute>
                } />
                
                <Route path="/spaces" element={
                  <ProtectedRoute>
                    <Spaces />
                  </ProtectedRoute>
                } />
                
                {/* Default redirect */}
                <Route path="/" element={<Navigate to="/dashboard" />} />
                
                {/* 404 fallback */}
                <Route path="*" element={<Navigate to="/dashboard" />} />
              </Routes>
            </div>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;