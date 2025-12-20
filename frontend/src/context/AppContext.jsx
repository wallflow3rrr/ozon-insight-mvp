import React, { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const useAppContext = () => useContext(AppContext);

export const AppProvider = ({ children }) => {
  const [period, setPeriod] = useState(30);
  const [logistics, setLogistics] = useState('both');
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  return (
    <AppContext.Provider value={{ period, setPeriod, logistics, setLogistics, darkMode, toggleDarkMode }}>
      {children}
    </AppContext.Provider>
  );
};