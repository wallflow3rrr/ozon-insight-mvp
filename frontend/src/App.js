// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Navbar from './components/Layout/Navbar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProductDetailPage from './pages/ProductDetailPage';
import ReturnsDashboard from './pages/ReturnsDashboard';
import StockDashboard from './pages/StockDashboard';
import LogisticsDashboard from './pages/LogisticsDashboard';

// Компонент, который показывает Navbar ТОЛЬКО на защищённых страницах
const Layout = ({ children }) => {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login' || location.pathname === '/';

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {!isLoginPage && <Navbar />}
      {children}
    </div>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Публичные роуты — без AppProvider и Navbar */}
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />

        {/* Защищённые роуты — с контекстом и лейаутом */}
        <Route
          element={
            <AppProvider>
              <Layout>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/returns" element={<ReturnsDashboard />} />
                  <Route path="/stock" element={<StockDashboard />} />
                  <Route path="/logistics" element={<LogisticsDashboard />} />
                  <Route path="/product/:sku" element={<ProductDetailPage />} />
                </Routes>
              </Layout>
            </AppProvider>
          }
        >
          {/* Эти пути будут обрабатываться внутри вложенного Routes */}
          <Route path="/dashboard" />
          <Route path="/returns" />
          <Route path="/stock" />
          <Route path="/logistics" />
          <Route path="/product/:sku" />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;