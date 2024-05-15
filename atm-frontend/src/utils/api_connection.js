// src/utils/api_connection.js
import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: `${BASE_URL}/atm/`,
});

// Accounts Information
export const loginUser = async (username, password) => {
  try {
    const response = await api.post('login/', { username, password });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const registerUser = async (username, password) => {
  try {
    const response = await api.post('register/', { username, password });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createUserAccount = async (userData) => {
  try {
    const response = await api.post('user-accounts/', userData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Banking Accounts
export const fetchUserAccounts = async () => {
  try {
    const response = await api.get('user-accounts/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createNewAccount = async (data) => {
  try {
    const response = await api.post('accounts/', data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const fetchBalanceInquiries = async (pin, amount) => {
  try {
    const response = await api.get('balance-inquiries/', { pin, amount });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const fetchPinChanges = async () => {
  try {
    const response = await api.get('pin-changes/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const requestPinChange = async (data) => {
  try {
    const response = await api.post('pin-changes/', data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Account Operations Endpoints
export const depositAmount = async (pin, amount) => {
  try {
    const response = await api.post('deposit/', { pin, amount });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const withdrawAmount = async (pin, amount) => {
  try {
    const response = await api.post('withdraw/', { pin, amount });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// CRUD Operations Endpoints
export const fetchTransactions = async () => {
  try {
    const response = await api.get('transactions/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createTransaction = async (data) => {
  try {
    const response = await api.post('transactions/', data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const fetchCashWithdrawals = async (pin, amount) => {
  try {
    const response = await api.get('cash-withdrawals/', { pin, amount });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Receipts
export const fetchReceipts = async () => {
  try {
    const response = await api.get('receipts/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createReceipt = async (data) => {
  try {
    const response = await api.post('receipts/', data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Mini Statements
export const fetchMiniStatements = async () => {
  try {
    const response = await api.get('mini-statements/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createMiniStatement = async (data) => {
  try {
    const response = await api.post('mini-statements/', data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Statements
export const fetchStatements = async () => {
  try {
    const response = await api.get('statements/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createStatement = async (data) => {
  try {
    const response = await api.post('statements/', data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Bill Payments
export const fetchBillPayments = async () => {
  try {
    const response = await api.get('bill-payments/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const makeBillPayment = async (data) => {
  try {
    const response = await api.post('bill-payments/', data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Mobile Recharge
export const fetchMobileRecharges = async () => {
  try {
    const response = await api.get('mobile-recharges/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const performMobileRecharge = async (data) => {
  try {
    const response = await api.post('mobile-recharges/', data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Prepaid Electricity
export const fetchPrepaidElectricityReloads = async () => {
  try {
    const response = await api.get('prepaid-electricity-reloads/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const performPrepaidElectricityReload = async (data) => {
  try {
    const response = await api.post('prepaid-electricity-reloads/', data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api;
