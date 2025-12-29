import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Handle token refresh on 401
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = (username, password) =>
  api.post('/auth/login/', { username, password });
export const register = data => api.post('/auth/register/', data);
export const getCurrentUser = () => api.get('/auth/user/');
export const updateProfile = data => api.patch('/auth/profile/', data);
export const changePassword = data => api.post('/auth/password/', data);
export const getPreferences = () => api.get('/auth/preferences/');
export const updatePreferences = data => api.patch('/auth/preferences/', data);

// Summary
export const getSummary = () => api.get('/summary/');

// Bank Accounts
export const getBankAccounts = () => api.get('/bank-accounts/');
export const getBankAccount = id => api.get(`/bank-accounts/${id}/`);
export const createBankAccount = data => api.post('/bank-accounts/', data);
export const updateBankAccount = (id, data) =>
  api.put(`/bank-accounts/${id}/`, data);
export const deleteBankAccount = id => api.delete(`/bank-accounts/${id}/`);

// Superannuation
export const getSuperannuationAccounts = () => api.get('/superannuation/');
export const getSuperannuationAccount = id => api.get(`/superannuation/${id}/`);
export const createSuperannuationAccount = data =>
  api.post('/superannuation/', data);
export const updateSuperannuationAccount = (id, data) =>
  api.put(`/superannuation/${id}/`, data);
export const deleteSuperannuationAccount = id =>
  api.delete(`/superannuation/${id}/`);

// Superannuation Snapshots
export const getSuperSnapshots = accountId =>
  api.get('/super-snapshots/', {
    params: accountId ? { account: accountId } : {},
  });
export const getSuperSnapshot = id => api.get(`/super-snapshots/${id}/`);
export const createSuperSnapshot = data => api.post('/super-snapshots/', data);
export const updateSuperSnapshot = (id, data) =>
  api.put(`/super-snapshots/${id}/`, data);
export const deleteSuperSnapshot = id => api.delete(`/super-snapshots/${id}/`);

// ETF Holdings
export const getETFHoldings = () => api.get('/etf-holdings/');
export const getETFHolding = id => api.get(`/etf-holdings/${id}/`);
export const createETFHolding = data => api.post('/etf-holdings/', data);
export const updateETFHolding = (id, data) =>
  api.put(`/etf-holdings/${id}/`, data);
export const deleteETFHolding = id => api.delete(`/etf-holdings/${id}/`);
export const refreshETFPrices = () => api.post('/etf/refresh-prices/');
export const getETFPrice = (ticker, exchange = 'ASX') =>
  api.get('/etf/get-price/', { params: { ticker, exchange } });

// ETF Transactions
export const getETFTransactions = etfId =>
  api.get(`/etf-transactions/${etfId ? `?etf=${etfId}` : ''}`);
export const createETFTransaction = data =>
  api.post('/etf-transactions/', data);
export const updateETFTransaction = (id, data) =>
  api.put(`/etf-transactions/${id}/`, data);
export const deleteETFTransaction = id =>
  api.delete(`/etf-transactions/${id}/`);

// Crypto Holdings
export const getCryptoHoldings = () => api.get('/crypto-holdings/');
export const getCryptoHolding = id => api.get(`/crypto-holdings/${id}/`);
export const createCryptoHolding = data => api.post('/crypto-holdings/', data);
export const updateCryptoHolding = (id, data) =>
  api.put(`/crypto-holdings/${id}/`, data);
export const deleteCryptoHolding = id => api.delete(`/crypto-holdings/${id}/`);
export const refreshCryptoPrices = () => api.post('/crypto/refresh-prices/');
export const getCryptoPrice = coingeckoId =>
  api.get('/crypto/get-price/', { params: { coingecko_id: coingeckoId } });

// Crypto Transactions
export const getCryptoTransactions = cryptoId =>
  api.get(`/crypto-transactions/${cryptoId ? `?crypto=${cryptoId}` : ''}`);
export const createCryptoTransaction = data =>
  api.post('/crypto-transactions/', data);
export const updateCryptoTransaction = (id, data) =>
  api.put(`/crypto-transactions/${id}/`, data);
export const deleteCryptoTransaction = id =>
  api.delete(`/crypto-transactions/${id}/`);

// Stock Holdings
export const getStockHoldings = () => api.get('/stock-holdings/');
export const getStockHolding = id => api.get(`/stock-holdings/${id}/`);
export const createStockHolding = data => api.post('/stock-holdings/', data);
export const updateStockHolding = (id, data) =>
  api.put(`/stock-holdings/${id}/`, data);
export const deleteStockHolding = id => api.delete(`/stock-holdings/${id}/`);
export const getStockPrice = (ticker, exchange = 'ASX') =>
  api.get('/stock/get-price/', { params: { ticker, exchange } });
export const refreshStockPrices = () => api.post('/stock/refresh-prices/');

// Stock Transactions
export const getStockTransactions = stockId =>
  api.get(`/stock-transactions/${stockId ? `?stock=${stockId}` : ''}`);
export const createStockTransaction = data =>
  api.post('/stock-transactions/', data);
export const updateStockTransaction = (id, data) =>
  api.put(`/stock-transactions/${id}/`, data);
export const deleteStockTransaction = id =>
  api.delete(`/stock-transactions/${id}/`);

export default api;
