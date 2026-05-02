import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

const Layout = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="p-6">
        <Outlet /> {/* Здесь будут рендериться дочерние маршруты */}
      </main>
    </div>
  );
};

export default Layout;