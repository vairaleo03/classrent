import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Link
} from '@mui/material';
import { School } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!formData.email || !formData.password) {
      setError('Tutti i campi sono obbligatori');
      setLoading(false);
      return;
    }

    try {
      const result = await login(formData.email, formData.password);
      
      if (result.success) {
        toast.success('Login effettuato con successo!');
        navigate('/dashboard');
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Errore durante il login. Riprova.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          {/* Header */}
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
            <School color="primary" sx={{ fontSize: 48, mb: 1 }} />
            <Typography component="h1" variant="h4" gutterBottom>
              ClassRent
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Accedi al tuo account
            </Typography>
          </Box>

          {/* Form */}
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email universitaria"
              name="email"
              autoComplete="email"
              autoFocus
              value={formData.email}
              onChange={handleChange}
              disabled={loading}
              type="email"
            />

            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              disabled={loading}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2, py: 1.5 }}
              disabled={loading}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Accedi'
              )}
            </Button>

            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2">
                Non hai un account?{' '}
                <Link
                  component="button"
                  variant="body2"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate('/register');
                  }}
                  sx={{ textDecoration: 'none' }}
                >
                  Registrati qui
                </Link>
              </Typography>
            </Box>
          </Box>

          {/* Demo Info */}
          <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary" align="center">
              <strong>Account Demo:</strong><br />
              Email: demo@università.edu<br />
              Password: demo123
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}

export default Login;