import dayjs from 'dayjs';

export const getBookingStatus = (booking) => {
  const now = dayjs();
  const start = dayjs(booking.start_datetime);
  const end = dayjs(booking.end_datetime);
  
  if (booking.status === 'cancelled') {
    return { status: 'cancelled', label: 'Cancellata', color: 'error' };
  }
  
  if (end.isBefore(now)) {
    return { status: 'completed', label: 'Completata', color: 'success' };
  }
  
  if (start.isBefore(now) && end.isAfter(now)) {
    return { status: 'active', label: 'In corso', color: 'warning' };
  }
  
  if (booking.status === 'confirmed') {
    return { status: 'confirmed', label: 'Confermata', color: 'success' };
  }
  
  return { status: 'pending', label: 'In attesa', color: 'warning' };
};

export const canEditBooking = (booking) => {
  const now = dayjs();
  const start = dayjs(booking.start_datetime);
  
  // Può modificare solo se la prenotazione non è ancora iniziata
  // e lo status è pending o confirmed
  return start.isAfter(now) && ['pending', 'confirmed'].includes(booking.status);
};

export const canCancelBooking = (booking) => {
  const now = dayjs();
  const start = dayjs(booking.start_datetime);
  
  // Può cancellare solo se la prenotazione non è ancora iniziata
  // e lo status non è già cancelled
  return start.isAfter(now) && booking.status !== 'cancelled';
};

export const getBookingTimeInfo = (booking) => {
  const start = dayjs(booking.start_datetime);
  const end = dayjs(booking.end_datetime);
  const now = dayjs();
  
  const duration = end.diff(start, 'minute');
  const timeUntilStart = start.diff(now, 'minute');
  
  return {
    duration,
    timeUntilStart,
    durationFormatted: duration < 60 ? `${duration}m` : `${Math.floor(duration / 60)}h ${duration % 60}m`,
    timeUntilFormatted: timeUntilStart > 0 ? 
      (timeUntilStart < 60 ? `${timeUntilStart}m` : `${Math.floor(timeUntilStart / 60)}h`) : 
      'Iniziata'
  };
};

export const validateBookingForm = (formData) => {
  const errors = {};
  
  if (!formData.space_id) {
    errors.space_id = 'Seleziona uno spazio';
  }
  
  if (!formData.start_datetime) {
    errors.start_datetime = 'Seleziona data e ora di inizio';
  }
  
  if (!formData.end_datetime) {
    errors.end_datetime = 'Seleziona data e ora di fine';
  }
  
  if (!formData.purpose || formData.purpose.trim().length < 3) {
    errors.purpose = 'Lo scopo deve essere almeno 3 caratteri';
  }
  
  if (formData.start_datetime && formData.end_datetime) {
    const start = dayjs(formData.start_datetime);
    const end = dayjs(formData.end_datetime);
    
    if (end.isBefore(start)) {
      errors.end_datetime = 'La fine deve essere dopo l\'inizio';
    }
    
    if (start.isBefore(dayjs())) {
      errors.start_datetime = 'Non puoi prenotare nel passato';
    }
    
    const duration = end.diff(start, 'minute');
    if (duration < 30) {
      errors.end_datetime = 'La durata minima è 30 minuti';
    }
    
    if (duration > 480) { // 8 ore
      errors.end_datetime = 'La durata massima è 8 ore';
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

export const generateTimeSlots = (date, startHour = 8, endHour = 20, interval = 60) => {
  const slots = [];
  const baseDate = dayjs(date).startOf('day');
  
  for (let hour = startHour; hour < endHour; hour += interval / 60) {
    const slotTime = baseDate.hour(Math.floor(hour)).minute((hour % 1) * 60);
    slots.push({
      value: slotTime.toISOString(),
      label: slotTime.format('HH:mm'),
      time: slotTime
    });
  }
  
  return slots;
};