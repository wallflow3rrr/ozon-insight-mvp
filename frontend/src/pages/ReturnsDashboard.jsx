import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { api } from '../services/api';
import DashboardHeader from '../components/Dashboard/DashboardHeader';
import Card from '../components/UI/Card';
import RevenueChart from '../components/Dashboard/RevenueChart';
import ExportButton from '../components/Export/ExportButton'; // ✅ Добавим кнопку экспорта

const ReturnsDashboard = () => {
  const { period, logistics } = useAppContext();
  const [returnsData, setReturnsData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Заглушка: возвращаем фиктивные данные для возвратов
      const mockReturnsData = {
        total_returns: 42,
        total_return_amount: 12500,
        return_rate: 8,
        returns_chart: Array.from({ length: period }, (_, i) => {
          const date = new Date();
          date.setDate(date.getDate() - (period - i - 1));
          return {
            date: date.toISOString().split('T')[0],
            value: Math.floor(Math.random() * 5)
          };
        }),
        top_returned_products: [
          { sku: 'SKU123', name: 'Шторы', returns: 10, reason: 'Не подошёл размер' },
          { sku: 'SKU456', name: 'Подушка', returns: 8, reason: 'Не понравилось качество' },
          { sku: 'SKU789', name: 'Ковёр', returns: 6, reason: 'Неправильный цвет' },
        ]
      };
      setReturnsData(mockReturnsData);
    } catch (error) {
      console.error("Failed to fetch returns data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [period, logistics]);

  if (loading || !returnsData) return <div className="p-6">Загрузка...</div>;

  return (
    <div className="p-6">
      {/* кнопка экспорта */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Дашборд возвратов</h1>
        <ExportButton data={returnsData} scope="returns" period={period} logistics={logistics} />
      </div>
      <DashboardHeader onSync={setReturnsData} />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Всего возвратов</h3>
          <p className="text-2xl font-bold">{returnsData.total_returns}</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Сумма возвратов</h3>
          <p className="text-2xl font-bold">{returnsData.total_return_amount.toLocaleString()} ₽</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Доля возвратов</h3>
          <p className="text-2xl font-bold">{returnsData.return_rate}%</p>
        </Card>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Динамика возвратов</h3>
          <RevenueChart data={{ revenue_chart: returnsData.returns_chart }} />
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">ТОП возвращённых товаров</h3>
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="py-2 px-4 text-left">SKU</th>
                <th className="py-2 px-4 text-left">Название</th>
                <th className="py-2 px-4 text-left">Кол-во</th>
                <th className="py-2 px-4 text-left">Причина</th>
              </tr>
            </thead>
            <tbody>
              {returnsData.top_returned_products.map((item, index) => (
                <tr key={index} className="border-t dark:border-gray-700">
                  <td className="py-2 px-4">{item.sku}</td>
                  <td className="py-2 px-4">{item.name}</td>
                  <td className="py-2 px-4">{item.returns}</td>
                  <td className="py-2 px-4">{item.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ReturnsDashboard;