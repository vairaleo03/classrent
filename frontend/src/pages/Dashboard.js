import React from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import {
  CalendarToday,
  Chat,
  School,
  Event
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const { data: recentBookings = [] } = useQuery(
    'recent-bookings',
    async () => {
      const response = await axios.get(`${API_URL}/bookings/`);
      return response.data.slice(0, 5); // Ultime 5 prenotazioni
    }
  );

  const { data: spaces = [] } = useQuery(
    'spaces',
    async () => {
      const response = await axios.get(`${API_URL}/chat/spaces`);
      return response.data.slice(0, 4); // Prime 4 aule
    }
  );

  const quickActions = [
    {
      title: 'Chat con Assistente',
      description: 'Prenota aule usando il linguaggio naturale',
      icon: <Chat color="primary" fontSize="large" />,
      action: () => navigate('/chat'),
      color: 'primary'
    },
    {
      title: 'Le Mie Prenotazioni',
      description: 'Visualizza e gestisci le tue prenotazioni',
      icon: <CalendarToday color="secondary" fontSize="large" />,
      action: () => navigate('/bookings'),
      color: 'secondary'
    },
    {
      title: 'Spazi Disponibili',
      description: 'Esplora aule e sale disponibili',
      icon: <School color="success" fontSize="large" />,
      action: () => navigate('/spaces'),
      color: 'success'
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Welcome Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Benvenuto, {user?.full_name}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Gestisci le tue prenotazioni universitarie con ClassRent
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={8}>
          <Typography variant="h6" gutterBottom>
            Azioni Rapide
          </Typography>
          <Grid container spacing={2}>
            {quickActions.map((action, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': { elevation: 4 },
                    height: '100%'
                  }}
                  onClick={action.action}
                >
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Box sx={{ mb: 2 }}>
                      {action.icon}
                    </Box>
                    <Typography variant="h6" gutterBottom>
                      {action.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {action.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Recent Bookings */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Prenotazioni Recenti
              </Typography>
              {recentBookings.length > 0 ? (
                <List dense>
                  {recentBookings.map((booking) => (
                    <ListItem key={booking.id} divider>
                      <ListItemText
                        primary={booking.space_name}
                        secondary={
                          <Box>
                            <Typography variant="caption" display="block">
                              {new Date(booking.start_datetime).toLocaleDateString()}
                            </Typography>
                            <Chip 
                              label={booking.status} 
                              size="small" 
                              color={booking.status === 'confirmed' ? 'success' : 'default'}
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Nessuna prenotazione recente
                </Typography>
              )}
              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/bookings')}
              >
                Vedi Tutte
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Available Spaces Preview */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Spazi Popolari
          </Typography>
          <Grid container spacing={2}>
            {spaces.map((space) => (
              <Grid item xs={12} sm={6} md={3} key={space.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {space.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {space.location}
                    </Typography>
                    <Typography variant="body2">
                      Capacità: {space.capacity} persone
                    </Typography>
                    {space.materials.length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption">Materiali:</Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {space.materials.slice(0, 2).map((material, idx) => (
                            <Chip key={idx} label={material.name} size="small" />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: 'primary.main', color: 'white' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Event fontSize="large" />
                  <Typography variant="h4" component="div">
                    {recentBookings.length}
                  </Typography>
                  <Typography variant="body2">
                    Prenotazioni Totali
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: 'success.main', color: 'white' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <School fontSize="large" />
                  <Typography variant="h4" component="div">
                    {spaces.length}
                  </Typography>
                  <Typography variant="body2">
                    Spazi Disponibili
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: 'secondary.main', color: 'white' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <CalendarToday fontSize="large" />
                  <Typography variant="h4" component="div">
                    {recentBookings.filter(b => b.status === 'confirmed').length}
                  </Typography>
                  <Typography variant="body2">
                    Prenotazioni Confermate
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;