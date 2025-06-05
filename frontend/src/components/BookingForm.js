import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Box,
  Typography,
  Chip,
  Alert,
  CircularProgress,
  Autocomplete
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import dayjs from 'dayjs';
import toast from 'react-hot-toast';
import { validateBookingForm } from '../utils/bookingUtils';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function BookingForm({ open, onClose, preselectedSpace = null, preselectedDate = null }) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    space_id: preselectedSpace?.id || '',
    start_datetime: preselectedDate ? dayjs(preselectedDate).hour(9).minute(0) : dayjs().add(1, 'day').hour(9).minute(0),
    end_datetime: preselectedDate ? dayjs(preselectedDate).hour(11).minute(0) : dayjs().add(1, 'day').hour(11).minute(0),
    purpose: '',
    materials_requested: [],
    notes: ''
  });
  const [errors, setErrors] = useState({});

  // Query per ottenere spazi disponibili
  const { data: spaces = [], isLoading: spacesLoading } = useQuery(
    'spaces',
    async () => {
      const response = await axios.get(`${API_URL}/spaces/`);
      return response.data;
    }
  );

  // Mutation per creare prenotazione
  const createBookingMutation = useMutation(
    async (bookingData) => {
      const dataToSend = {
        ...bookingData,
        start_datetime: bookingData.start_datetime.toISOString(),
        end_datetime: bookingData.end_datetime.toISOString()
      };
      const response = await axios.post(`${API_URL}/bookings/`, dataToSend);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('bookings');
        toast.success('Prenotazione creata con successo!');
        onClose();
        resetForm();
      },
      onError: (error) => {
        const errorMessage = error.response?.data?.detail || 'Errore nella creazione della prenotazione';
        toast.error(errorMessage);
      }
    }
  );

  // Preset form quando cambia lo spazio preselezionato
  useEffect(() => {
    if (preselectedSpace) {
      setFormData(prev => ({
        ...prev,
        space_id: preselectedSpace.id
      }));
    }
  }, [preselectedSpace]);

  const resetForm = () => {
    setFormData({
      space_id: '',
      start_datetime: dayjs().add(1, 'day').hour(9).minute(0),
      end_datetime: dayjs().add(1, 'day').hour(11).minute(0),
      purpose: '',
      materials_requested: [],
      notes: ''
    });
    setErrors({});
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleSubmit = () => {
    const validation = validateBookingForm(formData);
    
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    createBookingMutation.mutate(formData);
  };

  const selectedSpace = spaces.find(s => s.id === formData.space_id);
  const availableMaterials = selectedSpace?.materials || [];

  const materialSuggestions = [
    'Proiettore', 'PC', 'Lavagna Interattiva', 'Microfono', 
    'Webcam', 'Schermo Grande', 'Cavi HDMI', 'Caricatori',
    'Lavagna Tradizionale', 'Marker', 'Cancellino'
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Nuova Prenotazione
        {preselectedSpace && (
          <Typography variant="body2" color="text.secondary">
            Spazio: {preselectedSpace.name}
          </Typography>
        )}
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Grid container spacing={3}>
            {/* Selezione Spazio */}
            <Grid item xs={12}>
              <FormControl fullWidth error={!!errors.space_id}>
                <InputLabel>Seleziona Spazio</InputLabel>
                <Select
                  value={formData.space_id}
                  label="Seleziona Spazio"
                  onChange={(e) => handleChange('space_id', e.target.value)}
                  disabled={spacesLoading || !!preselectedSpace}
                >
                  {spaces.map((space) => (
                    <MenuItem key={space.id} value={space.id}>
                      <Box>
                        <Typography variant="body1">{space.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {space.location} • {space.capacity} persone • {space.type}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
                {errors.space_id && (
                  <Typography variant="caption" color="error">
                    {errors.space_id}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            {/* Informazioni Spazio Selezionato */}
            {selectedSpace && (
              <Grid item xs={12}>
                <Alert severity="info">
                  <Typography variant="body2">
                    <strong>{selectedSpace.name}</strong> - {selectedSpace.location}
                  </Typography>
                  <Typography variant="caption">
                    Capacità: {selectedSpace.capacity} persone • 
                    Orari: {selectedSpace.available_hours.start_time} - {selectedSpace.available_hours.end_time}
                  </Typography>
                  {selectedSpace.booking_constraints?.max_duration && (
                    <Typography variant="caption" display="block">
                      Durata massima: {selectedSpace.booking_constraints.max_duration} minuti
                    </Typography>
                  )}
                </Alert>
              </Grid>
            )}

            {/* Data e Ora */}
            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DateTimePicker
                  label="Data e ora inizio"
                  value={formData.start_datetime}
                  onChange={(newValue) => {
                    handleChange('start_datetime', newValue);
                    // Auto-adjust end time to be 2 hours later
                    if (newValue) {
                      handleChange('end_datetime', newValue.add(2, 'hour'));
                    }
                  }}
                  renderInput={(params) => (
                    <TextField 
                      {...params} 
                      fullWidth 
                      error={!!errors.start_datetime}
                      helperText={errors.start_datetime}
                    />
                  )}
                  minDateTime={dayjs()}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DateTimePicker
                  label="Data e ora fine"
                  value={formData.end_datetime}
                  onChange={(newValue) => handleChange('end_datetime', newValue)}
                  renderInput={(params) => (
                    <TextField 
                      {...params} 
                      fullWidth 
                      error={!!errors.end_datetime}
                      helperText={errors.end_datetime}
                    />
                  )}
                  minDateTime={formData.start_datetime}
                />
              </LocalizationProvider>
            </Grid>

            {/* Scopo */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Scopo della prenotazione"
                value={formData.purpose}
                onChange={(e) => handleChange('purpose', e.target.value)}
                multiline
                rows={2}
                error={!!errors.purpose}
                helperText={errors.purpose || 'Descrivi brevemente lo scopo della prenotazione'}
                placeholder="Es: Lezione di programmazione, Seminario, Riunione di progetto..."
              />
            </Grid>

            {/* Materiali */}
            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={materialSuggestions}
                value={formData.materials_requested}
                onChange={(event, newValue) => handleChange('materials_requested', newValue)}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip variant="outlined" label={option} {...getTagProps({ index })} />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Materiali richiesti (opzionale)"
                    placeholder="Seleziona o digita materiali..."
                  />
                )}
              />
              
              {/* Materiali disponibili nello spazio */}
              {availableMaterials.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Materiali disponibili in questo spazio:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                    {availableMaterials.map((material, index) => (
                      <Chip
                        key={index}
                        label={`${material.name} (${material.quantity})`}
                        size="small"
                        variant="outlined"
                        color="primary"
                        onClick={() => {
                          if (!formData.materials_requested.includes(material.name)) {
                            handleChange('materials_requested', [
                              ...formData.materials_requested,
                              material.name
                            ]);
                          }
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Grid>

            {/* Note */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Note aggiuntive (opzionale)"
                value={formData.notes}
                onChange={(e) => handleChange('notes', e.target.value)}
                multiline
                rows={3}
                placeholder="Eventuali note o richieste speciali..."
              />
            </Grid>

            {/* Durata Calcolata */}
            {formData.start_datetime && formData.end_datetime && (
              <Grid item xs={12}>
                <Alert severity="success">
                  <Typography variant="body2">
                    Durata prenotazione: {formData.end_datetime.diff(formData.start_datetime, 'hour')}h {formData.end_datetime.diff(formData.start_datetime, 'minute') % 60}m
                  </Typography>
                </Alert>
              </Grid>
            )}
          </Grid>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          Annulla
        </Button>
        <Button 
          onClick={handleSubmit}
          variant="contained"
          disabled={createBookingMutation.isLoading}
          startIcon={createBookingMutation.isLoading && <CircularProgress size={20} />}
        >
          {createBookingMutation.isLoading ? 'Creando...' : 'Crea Prenotazione'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default BookingForm;