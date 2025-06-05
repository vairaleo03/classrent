import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  Paper
} from '@mui/material';
import {
  ChevronLeft,
  ChevronRight,
  Today,
  Event,
  Person,
  LocationOn,
  AccessTime,
  Add
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import axios from 'axios';
import dayjs from 'dayjs';
import BookingForm from './BookingForm';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function CalendarView() {
  const [currentDate, setCurrentDate] = useState(dayjs());
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedBookings, setSelectedBookings] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [bookingFormOpen, setBookingFormOpen] = useState(false);
  const [viewMode, setViewMode] = useState('month'); // month, week, day

  // Query per ottenere tutte le prenotazioni del mese
  const { data: monthBookings = [], isLoading } = useQuery(
    ['calendar-bookings', currentDate.format('YYYY-MM')],
    async () => {
      const startDate = currentDate.startOf('month').format('YYYY-MM-DD');
      const endDate = currentDate.endOf('month').format('YYYY-MM-DD');
      
      const response = await axios.get(`${API_URL}/calendar/bookings`, {
        params: { start_date: startDate, end_date: endDate }
      });
      return response.data;
    }
  );

  // Query per ottenere spazi disponibili
  const { data: spaces = [] } = useQuery(
    'spaces',
    async () => {
      const response = await axios.get(`${API_URL}/spaces/`);
      return response.data;
    }
  );

  const getDaysInMonth = () => {
    const startOfMonth = currentDate.startOf('month');
    const endOfMonth = currentDate.endOf('month');
    const startOfCalendar = startOfMonth.startOf('week');
    const endOfCalendar = endOfMonth.endOf('week');
    
    const days = [];
    let current = startOfCalendar;
    
    while (current.isBefore(endOfCalendar) || current.isSame(endOfCalendar)) {
      days.push(current);
      current = current.add(1, 'day');
    }
    
    return days;
  };

  const getBookingsForDate = (date) => {
    return monthBookings.filter(booking => 
      dayjs(booking.start_datetime).isSame(date, 'day')
    );
  };

  const handleDateClick = (date, bookings) => {
    setSelectedDate(date);
    setSelectedBookings(bookings);
    setDialogOpen(true);
  };

  const getBookingColor = (booking) => {
    const colors = {
      'confirmed': '#4caf50',
      'pending': '#ff9800', 
      'cancelled': '#f44336'
    };
    return colors[booking.status] || '#2196f3';
  };

  const CalendarDay = ({ date, bookings, isCurrentMonth }) => {
    const isToday = date.isSame(dayjs(), 'day');
    const isPast = date.isBefore(dayjs(), 'day');
    
    return (
      <Paper
        elevation={1}
        sx={{
          minHeight: 120,
          p: 1,
          cursor: 'pointer',
          backgroundColor: isCurrentMonth ? 'white' : '#f5f5f5',
          border: isToday ? '2px solid #1976d2' : '1px solid #e0e0e0',
          opacity: isPast ? 0.7 : 1,
          '&:hover': {
            backgroundColor: isCurrentMonth ? '#f0f8ff' : '#eeeeee'
          }
        }}
        onClick={() => handleDateClick(date, bookings)}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography
            variant="body2"
            sx={{
              fontWeight: isToday ? 'bold' : 'normal',
              color: isCurrentMonth ? (isToday ? '#1976d2' : 'inherit') : '#999'
            }}
          >
            {date.format('D')}
          </Typography>
          {bookings.length > 0 && (
            <Chip
              label={bookings.length}
              size="small"
              color="primary"
              variant="outlined"
            />
          )}
        </Box>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          {bookings.slice(0, 2).map((booking, index) => (
            <Tooltip
              key={index}
              title={`${booking.space_name} - ${booking.purpose}`}
              arrow
            >
              <Box
                sx={{
                  backgroundColor: getBookingColor(booking),
                  color: 'white',
                  borderRadius: 1,
                  px: 0.5,
                  py: 0.2,
                  fontSize: '10px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}
              >
                {dayjs(booking.start_datetime).format('HH:mm')} {booking.space_name}
              </Box>
            </Tooltip>
          ))}
          {bookings.length > 2 && (
            <Typography variant="caption" color="text.secondary">
              +{bookings.length - 2} altre
            </Typography>
          )}
        </Box>
      </Paper>
    );
  };

  const BookingDetailsDialog = () => (
    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Prenotazioni del {selectedDate?.format('DD/MM/YYYY')}
          </Typography>
          <Button
            startIcon={<Add />}
            variant="contained"
            onClick={() => {
              setDialogOpen(false);
              setBookingFormOpen(true);
            }}
          >
            Nuova Prenotazione
          </Button>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {selectedBookings.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary">
              Nessuna prenotazione per questo giorno
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              sx={{ mt: 2 }}
              onClick={() => {
                setDialogOpen(false);
                setBookingFormOpen(true);
              }}
            >
              Crea Prima Prenotazione
            </Button>
          </Box>
        ) : (
          <List>
            {selectedBookings.map((booking, index) => (
              <ListItem key={index} divider>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Event fontSize="small" />
                      <Typography variant="subtitle1" fontWeight="bold">
                        {booking.space_name}
                      </Typography>
                      <Chip
                        label={booking.status}
                        size="small"
                        color={booking.status === 'confirmed' ? 'success' : 'default'}
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <AccessTime fontSize="small" />
                        <Typography variant="body2">
                          {dayjs(booking.start_datetime).format('HH:mm')} - {dayjs(booking.end_datetime).format('HH:mm')}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <LocationOn fontSize="small" />
                        <Typography variant="body2">
                          {spaces.find(s => s.id === booking.space_id)?.location || 'Posizione non disponibile'}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Person fontSize="small" />
                        <Typography variant="body2">
                          {booking.user_name} - {booking.purpose}
                        </Typography>
                      </Box>
                      {booking.materials_requested.length > 0 && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Materiali: {booking.materials_requested.join(', ')}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={() => setDialogOpen(false)}>Chiudi</Button>
      </DialogActions>
    </Dialog>
  );

  const days = getDaysInMonth();
  const weeks = [];
  for (let i = 0; i < days.length; i += 7) {
    weeks.push(days.slice(i, i + 7));
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Calendario */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <IconButton onClick={() => setCurrentDate(currentDate.subtract(1, 'month'))}>
                <ChevronLeft />
              </IconButton>
              <Typography variant="h5" fontWeight="bold">
                {currentDate.format('MMMM YYYY')}
              </Typography>
              <IconButton onClick={() => setCurrentDate(currentDate.add(1, 'month'))}>
                <ChevronRight />
              </IconButton>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                startIcon={<Today />}
                onClick={() => setCurrentDate(dayjs())}
                variant="outlined"
              >
                Oggi
              </Button>
              <Button
                startIcon={<Add />}
                onClick={() => setBookingFormOpen(true)}
                variant="contained"
              >
                Nuova Prenotazione
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Calendario */}
      <Card>
        <CardContent>
          {/* Header giorni della settimana */}
          <Grid container sx={{ mb: 2 }}>
            {['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'].map((day) => (
              <Grid item xs key={day}>
                <Typography
                  variant="subtitle2"
                  align="center"
                  color="text.secondary"
                  fontWeight="bold"
                >
                  {day}
                </Typography>
              </Grid>
            ))}
          </Grid>

          {/* Settimane */}
          {weeks.map((week, weekIndex) => (
            <Grid container key={weekIndex} sx={{ mb: 1 }}>
              {week.map((date) => {
                const bookings = getBookingsForDate(date);
                const isCurrentMonth = date.isSame(currentDate, 'month');
                
                return (
                  <Grid item xs key={date.format('YYYY-MM-DD')}>
                    <CalendarDay
                      date={date}
                      bookings={bookings}
                      isCurrentMonth={isCurrentMonth}
                    />
                  </Grid>
                );
              })}
            </Grid>
          ))}
        </CardContent>
      </Card>

      {/* Legenda */}
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>
            Legenda Stati
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Chip label="Confermata" size="small" sx={{ backgroundColor: '#4caf50', color: 'white' }} />
            <Chip label="In Attesa" size="small" sx={{ backgroundColor: '#ff9800', color: 'white' }} />
            <Chip label="Cancellata" size="small" sx={{ backgroundColor: '#f44336', color: 'white' }} />
          </Box>
        </CardContent>
      </Card>

      {/* Dialogs */}
      <BookingDetailsDialog />
      <BookingForm
        open={bookingFormOpen}
        onClose={() => setBookingFormOpen(false)}
        preselectedDate={selectedDate}
      />
    </Box>
  );
}

export default CalendarView;