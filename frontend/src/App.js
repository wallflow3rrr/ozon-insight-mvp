import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Layout from './components/Layout/Layout';

// Публичные страницы
import Login from './pages/Login';

// Защищённые дашборды
import Dashboard from './pages/Dashboard';
import ReturnsDashboard from './pages/ReturnsDashboard';
import StockDashboard from './pages/StockDashboard';
import LogisticsDashboard from './pages/LogisticsDashboard';
import ProductDetailPage from './pages/ProductDetailPage';

// Компонент защиты маршрутов
import ProtectedRoute from './components/Auth/ProtectedRoute';

function App() {
  return (
    <Router>
      <AppProvider>
        <Routes>
          {/* === ПУБЛИЧНЫЕ МАРШРУТЫ === */}
          <Route path="/login" element={<Login />} />
          
          {/* === ЗАЩИЩЁННЫЕ МАРШРУТЫ === */}
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/returns" element={<ReturnsDashboard />} />
            <Route path="/stock" element={<StockDashboard />} />
            <Route path="/logistics" element={<LogisticsDashboard />} />
            <Route path="/product/:sku" element={<ProductDetailPage />} />
          </Route>
          
          {/* === НЕИЗВЕСТНЫЕ МАРШРУТЫ === */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AppProvider>
    </Router>
  );
}

export default App;