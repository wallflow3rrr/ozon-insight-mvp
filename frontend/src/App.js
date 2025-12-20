import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Navbar from './components/Layout/Navbar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProductDetailPage from './pages/ProductDetailPage';
import ReturnsDashboard from './pages/ReturnsDashboard';
import StockDashboard from './pages/StockDashboard';
import LogisticsDashboard from './pages/LogisticsDashboard';

function App() {
  return (
    <AppProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
          <Navbar />
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/returns" element={<ReturnsDashboard />} />
            <Route path="/stock" element={<StockDashboard />} />
            <Route path="/logistics" element={<LogisticsDashboard />} />
            <Route path="/product/:sku" element={<ProductDetailPage />} />
          </Routes>
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;