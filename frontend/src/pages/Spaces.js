import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Paper,
  IconButton,
  Collapse,
  Alert
} from '@mui/material';
import {
  LocationOn,
  Group,
  Build,
  School,
  MeetingRoom,
  LocalHospital,
  Computer,
  ExpandMore,
  ExpandLess,
  EventAvailable,
  AccessTime,
  Info
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { useQuery } from 'react-query';
import axios from 'axios';
import dayjs from 'dayjs';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Spaces() {
  const [filters, setFilters] = useState({
    type: '',
    capacity: '',
    materials: ''
  });
  const [selectedSpace, setSelectedSpace] = useState(null);
  const [availabilityDate, setAvailabilityDate] = useState(dayjs());
  const [expandedCard, setExpandedCard] = useState(null);

  // Query per ottenere tutti gli spazi
  const { data: spaces = [], isLoading } = useQuery(
    ['spaces', filters],
    async () => {
      const params = new URLSearchParams();
      if (filters.type) params.append('space_type', filters.type);
      if (filters.capacity) params.append('capacity_min', filters.capacity);
      if (filters.materials) params.append('materials', filters.materials);
      
      const response = await axios.get(`${API_URL}/spaces/?${params}`);
      return response.data;
    }
  );

  // Query per i tipi di spazi
  const { data: spaceTypes = [] } = useQuery(
    'space-types',
    async () => {
      const response = await axios.get(`${API_URL}/spaces/types/list`);
      return response.data;
    }
  );

  // Query per disponibilità spazio selezionato
  const { data: availability, isLoading: loadingAvailability } = useQuery(
    ['availability', selectedSpace?.id, availabilityDate.format('YYYY-MM-DD')],
    async () => {
      if (!selectedSpace) return null;
      const response = await axios.get(
        `${API_URL}/spaces/${selectedSpace.id}/availability?date=${availabilityDate.format('YYYY-MM-DD')}`
      );
      return response.data;
    },
    {
      enabled: !!selectedSpace
    }
  );

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      type: '',
      capacity: '',
      materials: ''
    });
  };

  const getSpaceIcon = (type) => {
    switch (type) {
      case 'aula':
        return <School color="primary" />;
      case 'laboratorio':
        return <Computer color="primary" />;
      case 'sala_riunioni':
        return <MeetingRoom color="primary" />;
      case 'box_medico':
        return <LocalHospital color="primary" />;
      default:
        return <School color="primary" />;
    }
  };

  const getSpaceTypeLabel = (type) => {
    const labels = {
      'aula': 'Aula',
      'laboratorio': 'Laboratorio',
      'sala_riunioni': 'Sala Riunioni',
      'box_medico': 'Box Medico'
    };
    return labels[type] || type;
  };

  const generateTimeSlots = () => {
    if (!availability) return [];
    
    const slots = [];
    const startHour = parseInt(availability.available_hours.start_time.split(':')[0]);
    const endHour = parseInt(availability.available_hours.end_time.split(':')[0]);
    
    for (let hour = startHour; hour < endHour; hour++) {
      const timeSlot = `${hour.toString().padStart(2, '0')}:00`;
      const nextTimeSlot = `${(hour + 1).toString().padStart(2, '0')}:00`;
      
      const isBooked = availability.bookings.some(booking => {
        const bookingStart = booking.start_time;
        const bookingEnd = booking.end_time;
        return timeSlot >= bookingStart && timeSlot < bookingEnd;
      });
      
      slots.push({
        time: `${timeSlot} - ${nextTimeSlot}`,
        available: !isBooked,
        booking: isBooked ? availability.bookings.find(b => 
          timeSlot >= b.start_time && timeSlot < b.end_time
        ) : null
      });
    }
    
    return slots;
  };

  const SpaceCard = ({ space }) => {
    const isExpanded = expandedCard === space.id;
    
    return (
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {getSpaceIcon(space.type)}
            <Box sx={{ ml: 2 }}>
              <Typography variant="h6" component="h3">
                {space.name}
              </Typography>
              <Chip 
                label={getSpaceTypeLabel(space.type)} 
                size="small" 
                variant="outlined"
              />
            </Box>
          </Box>

          <List dense>
            <ListItem disablePadding>
              <ListItemIcon><LocationOn fontSize="small" /></ListItemIcon>
              <ListItemText primary={space.location} />
            </ListItem>
            
            <ListItem disablePadding>
              <ListItemIcon><Group fontSize="small" /></ListItemIcon>
              <ListItemText primary={`Capacità: ${space.capacity} persone`} />
            </ListItem>

            <ListItem disablePadding>
              <ListItemIcon><AccessTime fontSize="small" /></ListItemIcon>
              <ListItemText 
                primary={`${space.available_hours.start_time} - ${space.available_hours.end_time}`}
                secondary="Orari disponibili"
              />
            </ListItem>
          </List>

          {space.description && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {space.description}
            </Typography>
          )}

          {/* Materiali */}
          {space.materials?.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                <Build fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
                Materiali disponibili:
              </Typography>
              <Collapse in={isExpanded} collapsedSize={40}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {space.materials.map((material, index) => (
                    <Chip
                      key={index}
                      label={`${material.name} (${material.quantity})`}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Collapse>
              {space.materials.length > 3 && (
                <IconButton
                  size="small"
                  onClick={() => setExpandedCard(isExpanded ? null : space.id)}
                >
                  {isExpanded ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
              )}
            </Box>
          )}

          {/* Vincoli di prenotazione */}
          {space.booking_constraints && Object.keys(space.booking_constraints).length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                <Info fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
                Vincoli di prenotazione:
              </Typography>
              <List dense>
                {space.booking_constraints.max_duration && (
                  <ListItem disablePadding>
                    <ListItemText 
                      primary={`Durata massima: ${space.booking_constraints.max_duration} minuti`}
                      primaryTypographyProps={{ variant: 'caption' }}
                    />
                  </ListItem>
                )}
                {space.booking_constraints.advance_booking_days && (
                  <ListItem disablePadding>
                    <ListItemText 
                      primary={`Anticipo minimo: ${space.booking_constraints.advance_booking_days} giorni`}
                      primaryTypographyProps={{ variant: 'caption' }}
                    />
                  </ListItem>
                )}
              </List>
            </Box>
          )}
        </CardContent>

        <CardActions>
          <Button 
            size="small" 
            startIcon={<EventAvailable />}
            onClick={() => setSelectedSpace(space)}
          >
            Verifica Disponibilità
          </Button>
          <Button 
            size="small" 
            variant="contained"
            onClick={() => window.location.href = `/chat?space=${space.id}`}
          >
            Prenota
          </Button>
        </CardActions>
      </Card>
    );
  };

  const AvailabilityDialog = () => {
    const timeSlots = generateTimeSlots();

    return (
      <Dialog 
        open={!!selectedSpace} 
        onClose={() => setSelectedSpace(null)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          Disponibilità - {selectedSpace?.name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DatePicker
                label="Seleziona data"
                value={availabilityDate}
                onChange={(newValue) => setAvailabilityDate(newValue)}
                renderInput={(params) => <TextField {...params} fullWidth />}
                minDate={dayjs()}
                maxDate={dayjs().add(30, 'day')}
              />
            </LocalizationProvider>
          </Box>

          {loadingAvailability ? (
            <Typography>Caricamento disponibilità...</Typography>
          ) : availability ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                {availability.date} - {availability.space_name}
              </Typography>
              
              <Grid container spacing={1}>
                {timeSlots.map((slot, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Paper
                      sx={{
                        p: 1,
                        backgroundColor: slot.available ? 'success.light' : 'error.light',
                        color: slot.available ? 'success.contrastText' : 'error.contrastText'
                      }}
                    >
                      <Typography variant="body2" align="center">
                        {slot.time}
                      </Typography>
                      {!slot.available && slot.booking && (
                        <Typography variant="caption" align="center" display="block">
                          {slot.booking.purpose}
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>

              {timeSlots.length === 0 && (
                <Alert severity="info">
                  Nessun orario disponibile per questa data
                </Alert>
              )}
            </Box>
          ) : (
            <Typography>Errore nel caricamento della disponibilità</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedSpace(null)}>Chiudi</Button>
          <Button 
            variant="contained"
            onClick={() => {
              window.location.href = `/chat?space=${selectedSpace.id}&date=${availabilityDate.format('YYYY-MM-DD')}`;
            }}
          >
            Prenota questo spazio
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography>Caricamento spazi...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Spazi Disponibili
      </Typography>

      {/* Filtri */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Filtra Spazi
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Tipo di Spazio</InputLabel>
              <Select
                value={filters.type}
                label="Tipo di Spazio"
                onChange={(e) => handleFilterChange('type', e.target.value)}
              >
                <MenuItem value="">Tutti</MenuItem>
                {spaceTypes.map((type) => (
                  <MenuItem key={type.type} value={type.type}>
                    {getSpaceTypeLabel(type.type)} ({type.count})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Capacità Minima"
              type="number"
              value={filters.capacity}
              onChange={(e) => handleFilterChange('capacity', e.target.value)}
              inputProps={{ min: 1 }}
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Materiali (separati da virgola)"
              value={filters.materials}
              onChange={(e) => handleFilterChange('materials', e.target.value)}
              placeholder="Proiettore, PC, Microfono"
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Button 
              variant="outlined" 
              fullWidth
              onClick={clearFilters}
            >
              Rimuovi Filtri
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Statistiche */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="body1" color="text.secondary">
          Trovati {spaces.length} spazi
          {filters.type && ` di tipo "${getSpaceTypeLabel(filters.type)}"`}
          {filters.capacity && ` con capacità minima ${filters.capacity}`}
          {filters.materials && ` con materiali "${filters.materials}"`}
        </Typography>
      </Box>

      {/* Griglia Spazi */}
      {spaces.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            Nessuno spazio trovato
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Prova a modificare i filtri di ricerca
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {spaces.map((space) => (
            <Grid item xs={12} sm={6} md={4} key={space.id}>
              <SpaceCard space={space} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Dialog Disponibilità */}
      <AvailabilityDialog />
    </Container>
  );
}

export default Spaces;