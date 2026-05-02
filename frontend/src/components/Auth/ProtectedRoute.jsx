import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  
  // Проверяем наличие access_token в localStorage
  const token = localStorage.getItem('access_token');
  
  // Если токена нет — редиректим на логин, сохраняя текущий путь
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // Если токен есть — показываем защищённый контент
  return children;
};

export default ProtectedRoute;