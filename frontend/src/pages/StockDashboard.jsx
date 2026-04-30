import React, { useState, useEffect, useCallback } from 'react';
import { useAppContext } from '../context/AppContext';
import { api } from '../services/api';
import DashboardHeader from '../components/Dashboard/DashboardHeader';
import Card from '../components/UI/Card';
import ExportButton from '../components/Export/ExportButton';

const StockDashboard = () => {
  const { period, logistics } = useAppContext();
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getStockData(period, logistics);
      setStockData(data);
    } catch (error) {
      console.error("Failed to fetch stock data", error);
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

  if (loading || !stockData) return <div className="p-6">Загрузка данных остатков...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Дашборд остатков</h1>
        <ExportButton data={stockData} scope="stock" period={period} logistics={logistics} />
      </div>
      <DashboardHeader onSync={handleSync} showPeriodFilter={false} />
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card><h3 className="text-gray-500 dark:text-gray-400 text-sm">Всего товаров</h3><p className="text-2xl font-bold">{stockData.total_products}</p></Card>
        <Card><h3 className="text-gray-500 dark:text-gray-400 text-sm">Общая стоимость</h3><p className="text-2xl font-bold">{stockData.total_stock_value.toLocaleString('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2})} ₽</p></Card>
        <Card><h3 className="text-gray-500 dark:text-gray-400 text-sm">Низкий остаток</h3><p className="text-2xl font-bold">{stockData.low_stock_count}</p></Card>
        <Card><h3 className="text-gray-500 dark:text-gray-400 text-sm">Нет в наличии</h3><p className="text-2xl font-bold">{stockData.out_of_stock_count}</p></Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Остатки по складам</h3>
          <div className="space-y-2">
            {stockData.stock_by_warehouse.map((item, index) => (
              <div key={index}>
                <div className="flex justify-between"><span>{item.name}</span><span>{item.stock} шт.</span></div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mt-1">
                  <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${Math.min((item.stock / 100) * 100, 100)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Товары с низким остатком</h3>
          <table className="min-w-full">
            <thead><tr><th className="py-2 px-4 text-left">SKU</th><th className="py-2 px-4 text-left">Название</th><th className="py-2 px-4 text-left">Остаток</th><th className="py-2 px-4 text-left">Порог</th></tr></thead>
            <tbody>
              {stockData.low_stock_products.map((item, index) => (
                <tr key={index} className="border-t dark:border-gray-700">
                  <td className="py-2 px-4">{item.sku}</td>
                  <td className="py-2 px-4">{item.name}</td>
                  <td className={`py-2 px-4 font-bold ${item.stock === 0 ? 'text-red-600' : 'text-yellow-600'}`}>{item.stock}</td>
                  <td className="py-2 px-4">{item.threshold}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default StockDashboard;