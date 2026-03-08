import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});

export const analyzeListingWithImage = async (formData) => {
  const response = await api.post('/analyze', formData);
  return response.data;
};

export const analyzeListingByURL = async (formData) => {
  const response = await api.post('/analyze/url', formData);
  return response.data;
};

export const getRecentSubmissions = async () => {
  const response = await api.get('/submissions');
  return response.data;
};

export const getSubmissionById = async (listingId) => {
  const response = await api.get(`/submissions/${listingId}`);
  return response.data;
};
