import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/it';

dayjs.extend(relativeTime);
dayjs.locale('it');

export const formatDate = (date, format = 'DD/MM/YYYY') => {
  return dayjs(date).format(format);
};

export const formatDateTime = (date) => {
  return dayjs(date).format('DD/MM/YYYY HH:mm');
};

export const formatTime = (date) => {
  return dayjs(date).format('HH:mm');
};

export const getRelativeTime = (date) => {
  return dayjs(date).fromNow();
};

export const isToday = (date) => {
  return dayjs(date).isSame(dayjs(), 'day');
};

export const isTomorrow = (date) => {
  return dayjs(date).isSame(dayjs().add(1, 'day'), 'day');
};

export const isThisWeek = (date) => {
  return dayjs(date).isSame(dayjs(), 'week');
};

export const getTimeUntil = (date) => {
  const target = dayjs(date);
  const now = dayjs();
  
  if (target.isBefore(now)) {
    return 'Scaduto';
  }
  
  const diffInHours = target.diff(now, 'hour');
  const diffInDays = target.diff(now, 'day');
  
  if (diffInHours < 24) {
    return `Tra ${diffInHours} ore`;
  } else {
    return `Tra ${diffInDays} giorni`;
  }
};

export const getDurationBetween = (startDate, endDate) => {
  const start = dayjs(startDate);
  const end = dayjs(endDate);
  const duration = end.diff(start, 'minute');
  
  if (duration < 60) {
    return `${duration} minuti`;
  } else {
    const hours = Math.floor(duration / 60);
    const minutes = duration % 60;
    return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
  }
};

export const getWeekdays = () => {
  return ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica'];
};

export const getMonths = () => {
  return [
    'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
    'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'
  ];
};