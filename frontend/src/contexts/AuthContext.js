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
    checkExistingSession();
  }, []);

  // Handle session_id from URL fragment after OAuth redirect
  useEffect(() => {
    const handleSessionId = async () => {
      const hash = window.location.hash;
      console.log('Checking URL hash:', hash);
      
      if (hash && hash.includes('session_id=')) {
        console.log('Found session_id in URL hash, processing OAuth...');
        setLoading(true);
        const sessionId = hash.split('session_id=')[1].split('&')[0];
        console.log('Extracted session ID:', sessionId);
        
        try {
          console.log('Calling Emergent Auth API...');
          // Process session with Emergent backend
          const response = await axios.get('https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data', {
            headers: {
              'X-Session-ID': sessionId
            }
          });
          
          console.log('Emergent Auth response:', response.data);

          console.log('Calling our backend OAuth process...');
          // Send session data to our backend to create user session
          const authResponse = await axios.post(`${API}/auth/process-oauth`, {
            user_data: response.data,
            session_token: response.data.session_token
          }, {
            withCredentials: true
          });

          console.log('Backend auth response:', authResponse.data);
          setUser(authResponse.data.user);
          
          // Clean URL fragment
          window.location.hash = '';
          window.history.replaceState(null, null, window.location.pathname);
          console.log('OAuth processing completed successfully');
          
        } catch (error) {
          console.error('OAuth processing failed:', error);
          console.error('Error details:', error.response?.data);
          // Redirect to login on error
          window.location.href = '/login';
        } finally {
          setLoading(false);
        }
      }
    };

    handleSessionId();
  }, []);

  const checkExistingSession = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        withCredentials: true
      });
      setUser(response.data);
    } catch (error) {
      // No valid session
      console.log('No existing session');
    } finally {
      setLoading(false);
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
      return { 
        success: false, 
        message: error.response?.data?.message || 'Login failed' 
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
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Signup failed' 
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

  const initiateGoogleAuth = () => {
    const redirectUrl = `${window.location.origin}/dashboard`;
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
    window.location.href = authUrl;
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    forgotPassword,
    resetPassword,
    initiateGoogleAuth,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};