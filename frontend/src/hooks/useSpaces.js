import { useQuery } from 'react-query';
import { spacesAPI } from '../services/api';

export const useSpaces = (filters = {}) => {
  return useQuery(
    ['spaces', filters],
    () => spacesAPI.getAll(filters),
    {
      select: (response) => response.data,
      staleTime: 10 * 60 * 1000, // 10 minuti
      cacheTime: 30 * 60 * 1000, // 30 minuti
    }
  );
};

export const useSpace = (spaceId) => {
  return useQuery(
    ['space', spaceId],
    () => spacesAPI.getById(spaceId),
    {
      select: (response) => response.data,
      enabled: !!spaceId,
      staleTime: 10 * 60 * 1000,
    }
  );
};

export const useSpaceAvailability = (spaceId, date) => {
  return useQuery(
    ['space-availability', spaceId, date],
    () => spacesAPI.getAvailability(spaceId, date),
    {
      select: (response) => response.data,
      enabled: !!(spaceId && date),
      staleTime: 2 * 60 * 1000, // 2 minuti per disponibilità
    }
  );
};

export const useSpaceTypes = () => {
  return useQuery(
    'space-types',
    spacesAPI.getTypes,
    {
      select: (response) => response.data,
      staleTime: 60 * 60 * 1000, // 1 ora
      cacheTime: 24 * 60 * 60 * 1000, // 24 ore
    }
  );
};

export const useSpaceMaterials = (spaceId) => {
  return useQuery(
    ['space-materials', spaceId],
    () => spacesAPI.getMaterials(spaceId),
    {
      select: (response) => response.data,
      enabled: !!spaceId,
      staleTime: 10 * 60 * 1000,
    }
  );
};