import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Fab,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Paper,
  Tab,
  Tabs
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  LocationOn,
  Schedule,
  Group,
  Build,
  Notes,
  Event,
  Cancel,
  CheckCircle,
  Pending
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';
import dayjs from 'dayjs';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`booking-tabpanel-${index}`}
      aria-labelledby={`booking-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function Bookings() {
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [editMode, setEditMode] = useState(false);

  // Query per ottenere le prenotazioni
  const { data: bookings = [], isLoading } = useQuery(
    'bookings',
    async () => {
      const response = await axios.get(`${API_URL}/bookings/`);
      return response.data;
    }
  );

  // Query per ottenere gli spazi disponibili
  const { data: spaces = [] } = useQuery(
    'spaces',
    async () => {
      const response = await axios.get(`${API_URL}/spaces/`);
      return response.data;
    }
  );

  // Mutation per cancellare prenotazione
  const cancelBookingMutation = useMutation(
    async (bookingId) => {
      await axios.delete(`${API_URL}/bookings/${bookingId}`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('bookings');
        toast.success('Prenotazione cancellata con successo');
      },
      onError: () => {
        toast.error('Errore nella cancellazione della prenotazione');
      }
    }
  );

  // Mutation per aggiornare prenotazione
  const updateBookingMutation = useMutation(
    async ({ bookingId, data }) => {
      await axios.put(`${API_URL}/bookings/${bookingId}`, data);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('bookings');
        toast.success('Prenotazione aggiornata con successo');
        setOpenDialog(false);
        setSelectedBooking(null);
      },
      onError: () => {
        toast.error('Errore nell\'aggiornamento della prenotazione');
      }
    }
  );

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle color="success" />;
      case 'pending':
        return <Pending color="warning" />;
      case 'cancelled':
        return <Cancel color="error" />;
      default:
        return <Event />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const filterBookings = (status) => {
    const now = dayjs();
    switch (status) {
      case 'upcoming':
        return bookings.filter(b => 
          dayjs(b.start_datetime).isAfter(now) && 
          ['confirmed', 'pending'].includes(b.status)
        );
      case 'past':
        return bookings.filter(b => 
          dayjs(b.end_datetime).isBefore(now) || 
          b.status === 'completed'
        );
      case 'cancelled':
        return bookings.filter(b => b.status === 'cancelled');
      default:
        return bookings;
    }
  };

  const handleEdit = (booking) => {
    setSelectedBooking(booking);
    setEditMode(true);
    setOpenDialog(true);
  };

  const handleCancel = (bookingId) => {
    if (window.confirm('Sei sicuro di voler cancellare questa prenotazione?')) {
      cancelBookingMutation.mutate(bookingId);
    }
  };

  const EditBookingDialog = () => {
    const [formData, setFormData] = useState({
      start_datetime: selectedBooking ? dayjs(selectedBooking.start_datetime) : dayjs(),
      end_datetime: selectedBooking ? dayjs(selectedBooking.end_datetime) : dayjs(),
      purpose: selectedBooking?.purpose || '',
      notes: selectedBooking?.notes || ''
    });

    const handleSubmit = () => {
      const updateData = {
        start_datetime: formData.start_datetime.toISOString(),
        end_datetime: formData.end_datetime.toISOString(),
        purpose: formData.purpose,
        notes: formData.notes
      };

      updateBookingMutation.mutate({
        bookingId: selectedBooking.id,
        data: updateData
      });
    };

    return (
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Modifica Prenotazione</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DateTimePicker
                label="Data e ora inizio"
                value={formData.start_datetime}
                onChange={(newValue) => setFormData({ ...formData, start_datetime: newValue })}
                renderInput={(params) => <TextField {...params} fullWidth margin="normal" />}
              />
              
              <DateTimePicker
                label="Data e ora fine"
                value={formData.end_datetime}
                onChange={(newValue) => setFormData({ ...formData, end_datetime: newValue })}
                renderInput={(params) => <TextField {...params} fullWidth margin="normal" />}
              />
            </LocalizationProvider>

            <TextField
              fullWidth
              margin="normal"
              label="Scopo della prenotazione"
              value={formData.purpose}
              onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
              multiline
              rows={2}
            />

            <TextField
              fullWidth
              margin="normal"
              label="Note aggiuntive"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              multiline
              rows={3}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Annulla</Button>
          <Button onClick={handleSubmit} variant="contained">
            Salva Modifiche
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const BookingCard = ({ booking }) => {
    const canEdit = dayjs(booking.start_datetime).isAfter(dayjs()) && 
                   ['confirmed', 'pending'].includes(booking.status);

    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Typography variant="h6" component="h3">
              {booking.space_name}
            </Typography>
            <Chip 
              label={booking.status}
              color={getStatusColor(booking.status)}
              icon={getStatusIcon(booking.status)}
              size="small"
            />
          </Box>

          <List dense>
            <ListItem disablePadding>
              <ListItemIcon><Schedule color="primary" /></ListItemIcon>
              <ListItemText 
                primary={`${dayjs(booking.start_datetime).format('DD/MM/YYYY HH:mm')} - ${dayjs(booking.end_datetime).format('HH:mm')}`}
                secondary={`Durata: ${dayjs(booking.end_datetime).diff(dayjs(booking.start_datetime), 'hour')}h`}
              />
            </ListItem>
            
            <ListItem disablePadding>
              <ListItemIcon><Event color="primary" /></ListItemIcon>
              <ListItemText primary={booking.purpose} />
            </ListItem>

            {booking.materials_requested?.length > 0 && (
              <ListItem disablePadding>
                <ListItemIcon><Build color="primary" /></ListItemIcon>
                <ListItemText 
                  primary="Materiali richiesti"
                  secondary={booking.materials_requested.join(', ')}
                />
              </ListItem>
            )}

            {booking.notes && (
              <ListItem disablePadding>
                <ListItemIcon><Notes color="primary" /></ListItemIcon>
                <ListItemText primary={booking.notes} />
              </ListItem>
            )}
          </List>
        </CardContent>

        {canEdit && (
          <CardActions>
            <Button 
              size="small" 
              startIcon={<Edit />}
              onClick={() => handleEdit(booking)}
            >
              Modifica
            </Button>
            <Button 
              size="small" 
              color="error"
              startIcon={<Delete />}
              onClick={() => handleCancel(booking.id)}
            >
              Cancella
            </Button>
          </CardActions>
        )}
      </Card>
    );
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography>Caricamento prenotazioni...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Le Mie Prenotazioni
        </Typography>
        <Fab 
          color="primary" 
          aria-label="add"
          onClick={() => window.location.href = '/chat'}
        >
          <Add />
        </Fab>
      </Box>

      {bookings.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            Nessuna prenotazione trovata
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            Inizia a prenotare spazi usando il nostro assistente AI!
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<Add />}
            onClick={() => window.location.href = '/chat'}
            sx={{ mt: 2 }}
          >
            Nuova Prenotazione
          </Button>
        </Paper>
      ) : (
        <>
          {/* Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label={`Prossime (${filterBookings('upcoming').length})`} />
              <Tab label={`Passate (${filterBookings('past').length})`} />
              <Tab label={`Cancellate (${filterBookings('cancelled').length})`} />
              <Tab label={`Tutte (${bookings.length})`} />
            </Tabs>
          </Box>

          {/* Tab Panels */}
          <TabPanel value={tabValue} index={0}>
            {filterBookings('upcoming').map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
            {filterBookings('upcoming').length === 0 && (
              <Typography color="text.secondary" align="center">
                Nessuna prenotazione prossima
              </Typography>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {filterBookings('past').map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
            {filterBookings('past').length === 0 && (
              <Typography color="text.secondary" align="center">
                Nessuna prenotazione passata
              </Typography>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            {filterBookings('cancelled').map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
            {filterBookings('cancelled').length === 0 && (
              <Typography color="text.secondary" align="center">
                Nessuna prenotazione cancellata
              </Typography>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            {bookings.map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
          </TabPanel>
        </>
      )}

      {/* Edit Dialog */}
      {selectedBooking && <EditBookingDialog />}
    </Container>
  );
}

export default Bookings;