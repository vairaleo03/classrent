import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
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
  Info,
  Star,
  StarBorder
} from '@mui/icons-material';
import BookingForm from './BookingForm';

function SpaceCard({ space, onBookingSuccess, showFavoriteButton = false }) {
  const [expanded, setExpanded] = useState(false);
  const [bookingDialogOpen, setBookingDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

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

  const getSpaceTypeColor = (type) => {
    const colors = {
      'aula': 'primary',
      'laboratorio': 'secondary',
      'sala_riunioni': 'success',
      'box_medico': 'warning'
    };
    return colors[type] || 'default';
  };

  const handleToggleFavorite = () => {
    setIsFavorite(!isFavorite);
    // TODO: Implementare API per salvare/rimuovere dai preferiti
  };

  const handleBookingSuccess = () => {
    setBookingDialogOpen(false);
    if (onBookingSuccess) {
      onBookingSuccess();
    }
  };

  const SpaceDetailsDialog = () => (
    <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {getSpaceIcon(space.type)}
          <Box>
            <Typography variant="h6">{space.name}</Typography>
            <Chip 
              label={getSpaceTypeLabel(space.type)} 
              size="small" 
              color={getSpaceTypeColor(space.type)}
            />
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <List>
          <ListItem>
            <ListItemIcon><LocationOn /></ListItemIcon>
            <ListItemText primary="Posizione" secondary={space.location} />
          </ListItem>
          
          <ListItem>
            <ListItemIcon><Group /></ListItemIcon>
            <ListItemText primary="Capacità" secondary={`${space.capacity} persone`} />
          </ListItem>
          
          <ListItem>
            <ListItemIcon><AccessTime /></ListItemIcon>
            <ListItemText 
              primary="Orari disponibili" 
              secondary={`${space.available_hours.start_time} - ${space.available_hours.end_time}`} 
            />
          </ListItem>
        </List>

        {space.description && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>Descrizione</Typography>
            <Typography variant="body2" color="text.secondary">
              {space.description}
            </Typography>
          </Box>
        )}

        {space.materials?.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              <Build sx={{ verticalAlign: 'middle', mr: 1 }} />
              Materiali disponibili
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {space.materials.map((material, index) => (
                <Chip
                  key={index}
                  label={`${material.name} (${material.quantity})`}
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}

        {space.booking_constraints && Object.keys(space.booking_constraints).length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              <Info sx={{ verticalAlign: 'middle', mr: 1 }} />
              Vincoli di prenotazione
            </Typography>
            <List dense>
              {space.booking_constraints.max_duration && (
                <ListItem disablePadding>
                  <ListItemText 
                    primary={`Durata massima: ${space.booking_constraints.max_duration} minuti`}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              )}
              {space.booking_constraints.advance_booking_days && (
                <ListItem disablePadding>
                  <ListItemText 
                    primary={`Anticipo minimo: ${space.booking_constraints.advance_booking_days} giorni`}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              )}
            </List>
          </Box>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={() => setDetailsDialogOpen(false)}>Chiudi</Button>
        <Button 
          variant="contained"
          onClick={() => {
            setDetailsDialogOpen(false);
            setBookingDialogOpen(true);
          }}
        >
          Prenota
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <>
      <Card sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        '&:hover': { elevation: 4 },
        transition: 'all 0.2s ease-in-out'
      }}>
        <CardContent sx={{ flexGrow: 1 }}>
          {/* Header con icona e titolo */}
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              {getSpaceIcon(space.type)}
              <Box sx={{ ml: 2 }}>
                <Typography variant="h6" component="h3" gutterBottom>
                  {space.name}
                </Typography>
                <Chip 
                  label={getSpaceTypeLabel(space.type)} 
                  size="small" 
                  color={getSpaceTypeColor(space.type)}
                />
              </Box>
            </Box>
            
            {showFavoriteButton && (
              <IconButton onClick={handleToggleFavorite} size="small">
                {isFavorite ? <Star color="warning" /> : <StarBorder />}
              </IconButton>
            )}
          </Box>

          {/* Informazioni base */}
          <List dense>
            <ListItem disablePadding>
              <ListItemIcon><LocationOn fontSize="small" /></ListItemIcon>
              <ListItemText 
                primary={space.location}
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItem>
            
            <ListItem disablePadding>
              <ListItemIcon><Group fontSize="small" /></ListItemIcon>
              <ListItemText 
                primary={`${space.capacity} persone`}
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItem>

            <ListItem disablePadding>
              <ListItemIcon><AccessTime fontSize="small" /></ListItemIcon>
              <ListItemText 
                primary={`${space.available_hours.start_time} - ${space.available_hours.end_time}`}
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItem>
          </List>

          {/* Descrizione (se presente) */}
          {space.description && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {space.description.length > 100 
                ? `${space.description.substring(0, 100)}...` 
                : space.description}
            </Typography>
          )}

          {/* Materiali (preview) */}
          {space.materials?.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                <Build fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
                Materiali disponibili:
              </Typography>
              
              <Collapse in={expanded} collapsedSize={40}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {space.materials.map((material, index) => (
                    <Chip
                      key={index}
                      label={`${material.name}${material.quantity > 1 ? ` (${material.quantity})` : ''}`}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Collapse>
              
              {space.materials.length > 3 && (
                <IconButton
                  size="small"
                  onClick={() => setExpanded(!expanded)}
                  sx={{ p: 0.5 }}
                >
                  {expanded ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
              )}
            </Box>
          )}
        </CardContent>

        <CardActions sx={{ pt: 0 }}>
          <Button 
            size="small" 
            startIcon={<Info />}
            onClick={() => setDetailsDialogOpen(true)}
          >
            Dettagli
          </Button>
          <Button 
            size="small" 
            startIcon={<EventAvailable />}
            onClick={() => setBookingDialogOpen(true)}
            variant="contained"
          >
            Prenota
          </Button>
        </CardActions>
      </Card>

      {/* Dialogs */}
      <SpaceDetailsDialog />
      <BookingForm 
        open={bookingDialogOpen}
        onClose={() => setBookingDialogOpen(false)}
        preselectedSpace={space}
        onSuccess={handleBookingSuccess}
      />
    </>
  );
}

export default SpaceCard;
