import React, { createContext, useContext, useState, useEffect } from 'react';

/**
 * NotificationContext
 * 
 * Context untuk mengelola state notifikasi global
 * - Toggle on/off auto-prediction alerts
 * - Persist preference ke localStorage
 */

const NotificationContext = createContext();

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  // Load initial state from localStorage
  const [notificationsEnabled, setNotificationsEnabled] = useState(() => {
    const saved = localStorage.getItem('notificationsEnabled');
    return saved !== null ? JSON.parse(saved) : true; // Default: enabled
  });

  // Save to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('notificationsEnabled', JSON.stringify(notificationsEnabled));
  }, [notificationsEnabled]);

  const toggleNotifications = () => {
    setNotificationsEnabled(prev => !prev);
  };

  const value = {
    notificationsEnabled,
    toggleNotifications,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};
