import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { api } from '../services/api';
import DashboardHeader from '../components/Dashboard/DashboardHeader';
import KpiCards from '../components/Dashboard/KpiCards';
import RevenueChart from '../components/Dashboard/RevenueChart';
import TopProductsTable from '../components/Dashboard/TopProductsTable';
import ExportButton from '../components/Export/ExportButton';

const Dashboard = () => {
  const { period, logistics } = useAppContext();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardData(period, logistics);
      setDashboardData(data);
    } catch (error) {
      console.error("Failed to fetch dashboard ", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [fetchData, period, logistics]);

  if (loading || !dashboardData) return <div className="p-6">Загрузка данных дашборда...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Общий дашборд</h1>
        <ExportButton data={dashboardData} scope="dashboard" period={period} logistics={logistics} />
      </div>
      <DashboardHeader onSync={setDashboardData} />
      <KpiCards data={dashboardData} />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <RevenueChart data={dashboardData} />
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">ТОП-5 товаров</h2>
          <TopProductsTable data={dashboardData} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;