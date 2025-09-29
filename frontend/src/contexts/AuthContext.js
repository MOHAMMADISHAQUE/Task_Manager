import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session on app load
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (loading) {
        console.warn('Auth check taking too long, stopping loading state');
        setLoading(false);
        setUser(null);
      }
    }, 8000); // 8 second absolute maximum

    checkExistingSession().finally(() => {
      clearTimeout(timeoutId);
    });
    
    return () => clearTimeout(timeoutId);
  }, []);

  const checkExistingSession = async () => {
    let completed = false;
    
    try {
      // Race between the request and a timeout
      const authCheck = axios.get(`${API}/auth/me`, {
        withCredentials: true,
        timeout: 5000 // 5 second request timeout
      });
      
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 6000);
      });
      
      const response = await Promise.race([authCheck, timeoutPromise]);
      
      if (response && response.data) {
        setUser(response.data);
        console.log('Existing session found:', response.data.email);
      }
    } catch (error) {
      // Handle all error types gracefully
      console.log('No valid session or auth check failed:', error.message);
      setUser(null);
    } finally {
      if (!completed) {
        completed = true;
        setLoading(false);
      }
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password
      }, {
        withCredentials: true
      });
      
      setUser(response.data.user);
      return { success: true };
    } catch (error) {
      console.error('Login error:', error.response?.data);
      return { 
        success: false, 
        message: error.response?.data?.detail || error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const signup = async (name, email, password) => {
    try {
      const response = await axios.post(`${API}/auth/signup`, {
        name,
        email,
        password
      }, {
        withCredentials: true
      });
      
      setUser(response.data.user);
      return { success: true, isNewUser: true };
    } catch (error) {
      console.error('Signup error:', error.response?.data);
      return { 
        success: false, 
        message: error.response?.data?.detail || error.response?.data?.message || 'Signup failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  const forgotPassword = async (email) => {
    try {
      await axios.post(`${API}/auth/forgot-password`, { email });
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Password reset failed' 
      };
    }
  };

  const resetPassword = async (token, password) => {
    try {
      await axios.post(`${API}/auth/reset-password`, { token, password });
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Password reset failed' 
      };
    }
  };

  const loginWithEmergent = async (sessionId) => {
    try {
      const response = await axios.post(`${API}/auth/emergent/callback`, {
        session_id: sessionId
      }, {
        withCredentials: true
      });
      
      setUser(response.data.user);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || error.response?.data?.message || 'Emergent login failed' 
      };
    }
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    forgotPassword,
    resetPassword,
    loginWithEmergent,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};