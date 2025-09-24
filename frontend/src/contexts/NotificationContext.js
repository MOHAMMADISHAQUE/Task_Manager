import React, { createContext, useContext, useState, useEffect } from 'react';

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  // Fetch notifications
  const fetchNotifications = async (unreadOnly = false) => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/notifications/?unread_only=${unreadOnly}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch unread count
  const fetchUnreadCount = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/notifications/unread-count`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  };

  // Mark notifications as read
  const markAsRead = async (notificationIds) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/notifications/mark-read`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          notification_ids: notificationIds
        })
      });

      if (response.ok) {
        // Update local state
        setNotifications(prev => 
          prev.map(notif => 
            notificationIds.includes(notif.id) ? { ...notif, read: true } : notif
          )
        );
        
        // Update unread count
        fetchUnreadCount();
      }
    } catch (error) {
      console.error('Failed to mark notifications as read:', error);
    }
  };

  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/notifications/mark-all-read`, {
        method: 'PUT',
        credentials: 'include'
      });

      if (response.ok) {
        // Update local state
        setNotifications(prev => 
          prev.map(notif => ({ ...notif, read: true }))
        );
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  // Delete notification
  const deleteNotification = async (notificationId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/notifications/${notificationId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        // Update local state
        setNotifications(prev => 
          prev.filter(notif => notif.id !== notificationId)
        );
        
        // Update unread count
        fetchUnreadCount();
      }
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  // Create test notifications (for development)
  const createTestNotifications = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/notifications/test`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        fetchNotifications();
        fetchUnreadCount();
      }
    } catch (error) {
      console.error('Failed to create test notifications:', error);
    }
  };

  // Load notifications on mount
  useEffect(() => {
    fetchNotifications();
    fetchUnreadCount();
    
    // Set up periodic refresh (every 30 seconds)
    const interval = setInterval(() => {
      fetchUnreadCount();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const value = {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    createTestNotifications
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};