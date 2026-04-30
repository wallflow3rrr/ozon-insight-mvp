import React, { useState, useEffect, useCallback } from 'react';
import { useAppContext } from '../context/AppContext';
import { api } from '../services/api';
import DashboardHeader from '../components/Dashboard/DashboardHeader';
import Card from '../components/UI/Card';
import RevenueChart from '../components/Dashboard/RevenueChart';
import ExportButton from '../components/Export/ExportButton';

const LogisticsDashboard = () => {
  const { period, logistics } = useAppContext();
  const [logisticsData, setLogisticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getLogisticsData(period, logistics);
      setLogisticsData(data);
    } catch (error) {
      console.error("Failed to fetch logistics data", error);
    } finally {
      setLoading(false);
    }
  }, [period, logistics]);

  const handleSync = useCallback(async () => {
    try {
      await api.triggerSync();
      setTimeout(fetchData, 1000);
    } catch (error) {
      console.error("Sync error", error);
    }
  }, [fetchData]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading || !logisticsData) return <div className="p-6">Загрузка данных логистики...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Дашборд логистики</h1>
        <ExportButton data={logisticsData} scope="logistics" period={period} logistics={logistics} />
      </div>
      <DashboardHeader onSync={handleSync} />
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card><h3 className="text-gray-500 dark:text-gray-400 text-sm">Заказов FBO</h3><p className="text-2xl font-bold">{logisticsData.total_orders_fbo}</p></Card>
        <Card><h3 className="text-gray-500 dark:text-gray-400 text-sm">Заказов FBS</h3><p className="text-2xl font-bold">{logisticsData.total_orders_fbs}</p></Card>
        <Card><h3 className="text-gray-500 dark:text-gray-400 text-sm">Ср. доставка FBO</h3><p className="text-2xl font-bold">{logisticsData.avg_delivery_time_fbo} дн.</p></Card>
        <Card><h3 className="text-gray-500 dark:text-gray-400 text-sm">Ср. доставка FBS</h3><p className="text-2xl font-bold">{logisticsData.avg_delivery_time_fbs} дн.</p></Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Расходы на логистику</h3>
          <div className="space-y-3">
            {logisticsData.cost_by_type?.map((item, index) => (
              <div key={index}>
                <div className="flex justify-between"><span>{item.type}</span><span>{item.cost.toLocaleString('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2})} ₽</span></div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mt-1">
                  <div className={`h-2.5 rounded-full ${item.type === 'FBO' ? 'bg-green-600' : 'bg-blue-600'}`} style={{ width: `${(item.cost / logisticsData.total_logistics_cost) * 100}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Динамика доставок</h3>
          {/* ✅ Преобразуем delivery_chart в формат revenue_chart для RevenueChart */}
          <RevenueChart data={{ 
            revenue_chart: logisticsData.delivery_chart.map(d => ({ 
              date: d.date, 
              value: d.fbo + d.fbs 
            })) 
          }} 
          title="Динамика доставок"
          />
        </div>
      </div>
    </div>
  );
};
export default LogisticsDashboard;