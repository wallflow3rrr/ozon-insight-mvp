import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { api } from '../services/api';
import DashboardHeader from '../components/Dashboard/DashboardHeader';
import Card from '../components/UI/Card';
import ExportButton from '../components/Export/ExportButton';

const LogisticsDashboard = () => {
  const { period, logistics } = useAppContext();
  const [logisticsData, setLogisticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const mockLogisticsData = {
        total_orders_fbo: 200,
        total_orders_fbs: 120,
        avg_delivery_time_fbo: 3.2,
        avg_delivery_time_fbs: 5.1,
        total_logistics_cost: 45000,
        logistics_cost_fbo: 25000,
        logistics_cost_fbs: 20000,
        delivery_chart: [
          { date: '2025-01-01', fbo: 5, fbs: 3 },
          { date: '2025-01-02', fbo: 4, fbs: 2 },
          { date: '2025-01-03', fbo: 6, fbs: 4 },
        ],
        cost_by_type: [
          { type: 'FBO', cost: 25000 },
          { type: 'FBS', cost: 20000 },
        ]
      };
      setLogisticsData(mockLogisticsData);
    } catch (error) {
      console.error("Failed to fetch logistics data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [period, logistics]);

  if (loading || !logisticsData) return <div className="p-6">Загрузка...</div>;

  return (
    <div className="p-6">
      {/*кнопка экспорта */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Дашборд логистики</h1>
        <ExportButton data={logisticsData} scope="logistics" period={period} logistics={logistics} />
      </div>
      <DashboardHeader onSync={setLogisticsData} />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Заказов FBO</h3>
          <p className="text-2xl font-bold">{logisticsData.total_orders_fbo}</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Заказов FBS</h3>
          <p className="text-2xl font-bold">{logisticsData.total_orders_fbs}</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Ср. доставка FBO</h3>
          <p className="text-2xl font-bold">{logisticsData.avg_delivery_time_fbo} дн.</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Ср. доставка FBS</h3>
          <p className="text-2xl font-bold">{logisticsData.avg_delivery_time_fbs} дн.</p>
        </Card>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Расходы на логистику</h3>
          <div className="space-y-2">
            {logisticsData.cost_by_type?.map((item, index) => (
              <div key={index}>
                <div className="flex justify-between">
                  <span>{item.type}</span>
                  <span>{item.cost.toLocaleString()} ₽</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                  <div
                    className={`h-2.5 rounded-full ${item.type === 'FBO' ? 'bg-green-600' : 'bg-blue-600'}`}
                    style={{ width: `${(item.cost / logisticsData.total_logistics_cost) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Динамика доставок</h3>
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="py-2 px-4 text-left">Дата</th>
                <th className="py-2 px-4 text-left">FBO</th>
                <th className="py-2 px-4 text-left">FBS</th>
              </tr>
            </thead>
            <tbody>
              {logisticsData.delivery_chart?.map((item, index) => (
                <tr key={index} className="border-t dark:border-gray-700">
                  <td className="py-2 px-4">{item.date}</td>
                  <td className="py-2 px-4">{item.fbo}</td>
                  <td className="py-2 px-4">{item.fbs}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default LogisticsDashboard;