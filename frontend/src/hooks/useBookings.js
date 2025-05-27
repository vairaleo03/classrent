import { useQuery, useMutation, useQueryClient } from 'react-query';
import { bookingsAPI } from '../services/api';
import toast from 'react-hot-toast';

export const useBookings = () => {
  return useQuery(
    'bookings',
    bookingsAPI.getAll,
    {
      select: (response) => response.data,
      staleTime: 5 * 60 * 1000, // 5 minuti
      cacheTime: 10 * 60 * 1000, // 10 minuti
    }
  );
};

export const useCreateBooking = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    bookingsAPI.create,
    {
      onSuccess: () => {
        queryClient.invalidateQueries('bookings');
        toast.success('Prenotazione creata con successo!');
      },
      onError: (error) => {
        const message = error.response?.data?.detail || 'Errore nella creazione della prenotazione';
        toast.error(message);
      }
    }
  );
};

export const useUpdateBooking = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ id, data }) => bookingsAPI.update(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('bookings');
        toast.success('Prenotazione aggiornata con successo!');
      },
      onError: (error) => {
        const message = error.response?.data?.detail || 'Errore nell\'aggiornamento della prenotazione';
        toast.error(message);
      }
    }
  );
};

export const useCancelBooking = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    bookingsAPI.delete,
    {
      onSuccess: () => {
        queryClient.invalidateQueries('bookings');
        toast.success('Prenotazione cancellata con successo!');
      },
      onError: (error) => {
        const message = error.response?.data?.detail || 'Errore nella cancellazione della prenotazione';
        toast.error(message);
      }
    }
  );
};

export const useBookingHistory = () => {
  return useQuery(
    'booking-history',
    bookingsAPI.getHistory,
    {
      select: (response) => response.data,
      staleTime: 10 * 60 * 1000, // 10 minuti
    }
  );
};