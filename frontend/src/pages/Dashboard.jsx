import React, { useState, useEffect, useCallback } from 'react';
import { useAppContext } from '../context/AppContext';
import { api } from '../services/api';
import DashboardHeader from '../components/Dashboard/DashboardHeader';
import KpiCards from '../components/Dashboard/KpiCards';
import RevenueChart from '../components/Dashboard/RevenueChart';
import TopProductsTable from '../components/Dashboard/TopProductsTable';
import ExportButton from '../components/Export/ExportButton';
import Button from '../components/UI/Button';

const Dashboard = () => {
  const { period, logistics } = useAppContext();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingError, setLoadingError] = useState(null);

  // ✅ Оберни fetchData в useCallback
  const fetchData = useCallback(async () => {
    setLoading(true);
    setLoadingError(null);
    try {
      const data = await api.getDashboardData(period, logistics);
      setDashboardData(data);
    } catch (error) {
      console.error("Failed to fetch dashboard ", error);
      // Проверяем статус 404 и обрабатываем как отсутствие данных
      if (error.status === 404) {
        setDashboardData(null); // Явно устанавливаем в null, если данных нет
      } else {
        setLoadingError(error.message || "Не удалось загрузить данные");
      }
    } finally {
      setLoading(false);
    }
  }, [period, logistics]);

  // ✅ Функция для синхронизации и последующей загрузки данных
  const handleSync = useCallback(async () => {
    try {
      await api.triggerSync();
      // Ждём немного, чтобы синхронизация точно началась, затем обновляем данные
      setTimeout(() => {
        fetchData();
      }, 1000);
    } catch (error) {
      console.error("Failed to trigger sync", error);
      alert("Ошибка синхронизации: " + (error.message || "Неизвестная ошибка"));
    }
  }, [fetchData]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ✅ Проверяем, есть ли данные
  if (loading) {
    return <div className="p-6">Загрузка данных дашборда...</div>;
  }

  if (loadingError) {
    return (
      <div className="p-6 text-center">
        <p className="text-red-600 dark:text-red-400">Ошибка: {loadingError}</p>
        {/* ✅ Кнопка "Повторить попытку" теперь вызывает синхронизацию */}
        <Button onClick={handleSync} className="mt-4">
          🔄 Попробовать синхронизировать
        </Button>
      </div>
    );
  }

  // ✅ Если данных нет (dashboardData === null), показываем сообщение и кнопку синхронизации
  if (!dashboardData) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold mb-4">Общий дашборд</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Данные отсутствуют. Нажмите кнопку ниже, чтобы синхронизировать данные с Ozon.
        </p>
        <Button onClick={handleSync}>
          🔄 Синхронизировать данные
        </Button>
      </div>
    );
  }

  // ✅ Если данные есть, отображаем обычный дашборд
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Общий дашборд</h1>
        <ExportButton data={dashboardData} scope="dashboard" period={period} logistics={logistics} />
      </div>
      {/* ✅ Передаём handleSync как onSync, чтобы кнопка в DashboardHeader работала */}
      <DashboardHeader onSync={handleSync} />
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