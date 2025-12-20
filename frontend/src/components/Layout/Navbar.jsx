import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAppContext } from '../../context/AppContext';

const Navbar = () => {
  const { darkMode, toggleDarkMode } = useAppContext();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white dark:bg-gray-900 shadow-lg p-4 flex flex-col md:flex-row md:justify-between md:items-center gap-4">
      <div className="flex items-center gap-6">
        <Link to="/dashboard" className="text-xl font-bold text-blue-600 dark:text-blue-400">
          OzonInsight
        </Link>
        <div className="flex gap-4">
          <Link
            to="/dashboard"
            className={`text-sm px-3 py-1 rounded-lg transition-colors ${isActive('/dashboard') ? 'font-bold text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30' : 'text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400'}`}
          >
            Общий
          </Link>
          <Link
            to="/returns"
            className={`text-sm px-3 py-1 rounded-lg transition-colors ${isActive('/returns') ? 'font-bold text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30' : 'text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400'}`}
          >
            Возвраты
          </Link>
          <Link
            to="/stock"
            className={`text-sm px-3 py-1 rounded-lg transition-colors ${isActive('/stock') ? 'font-bold text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30' : 'text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400'}`}
          >
            Остатки
          </Link>
          <Link
            to="/logistics"
            className={`text-sm px-3 py-1 rounded-lg transition-colors ${isActive('/logistics') ? 'font-bold text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30' : 'text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400'}`}
          >
            Логистика
          </Link>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button
          onClick={toggleDarkMode}
          className="text-sm px-4 py-2 rounded-lg bg-gradient-to-r from-gray-200 to-gray-300 hover:from-gray-300 hover:to-gray-400 dark:from-gray-700 dark:to-gray-600 dark:hover:from-gray-600 dark:hover:to-gray-500 transition-colors"
        >
          {darkMode ? '☀️ Светлая' : '🌙 Тёмная'}
        </button>
      </div>
    </nav>
  );
};

export default Navbar;