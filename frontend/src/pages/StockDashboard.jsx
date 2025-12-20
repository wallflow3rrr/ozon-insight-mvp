import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
//import { api } from '../services/api';
import DashboardHeader from '../components/Dashboard/DashboardHeader';
import Card from '../components/UI/Card';
import ExportButton from '../components/Export/ExportButton';

const StockDashboard = () => {
  const { period, logistics } = useAppContext();
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const mockStockData = {
        total_products: 120,
        total_stock_value: 540000,
        low_stock_count: 15,
        out_of_stock_count: 3,
        stock_by_warehouse: [
          { name: 'Склад 1', stock: 50 },
          { name: 'Склад 2', stock: 35 },
          { name: 'Склад 3', stock: 35 },
        ],
        low_stock_products: [
          { sku: 'SKU111', name: 'Шторы', stock: 2, threshold: 5 },
          { sku: 'SKU222', name: 'Подушка', stock: 0, threshold: 3 },
          { sku: 'SKU333', name: 'Ковёр', stock: 1, threshold: 2 },
        ]
      };
      setStockData(mockStockData);
    } catch (error) {
      console.error("Failed to fetch stock data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [period, logistics]);

  if (loading || !stockData) return <div className="p-6">Загрузка...</div>;

  return (
    <div className="p-6">
      {/* кнопка экспорта */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Дашборд остатков</h1>
        <ExportButton data={stockData} scope="stock" period={period} logistics={logistics} />
      </div>
      <DashboardHeader onSync={setStockData} />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Всего товаров</h3>
          <p className="text-2xl font-bold">{stockData.total_products}</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Общая стоимость</h3>
          <p className="text-2xl font-bold">{stockData.total_stock_value.toLocaleString()} ₽</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Низкий остаток</h3>
          <p className="text-2xl font-bold">{stockData.low_stock_count}</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm">Нет в наличии</h3>
          <p className="text-2xl font-bold">{stockData.out_of_stock_count}</p>
        </Card>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Остатки по складам</h3>
          <div className="space-y-2">
            {stockData.stock_by_warehouse.map((item, index) => (
              <div key={index}>
                <div className="flex justify-between">
                  <span>{item.name}</span>
                  <span>{item.stock}</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full"
                    style={{ width: `${(item.stock / 50) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Товары с низким остатком</h3>
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="py-2 px-4 text-left">SKU</th>
                <th className="py-2 px-4 text-left">Название</th>
                <th className="py-2 px-4 text-left">Остаток</th>
                <th className="py-2 px-4 text-left">Порог</th>
              </tr>
            </thead>
            <tbody>
              {stockData.low_stock_products.map((item, index) => (
                <tr key={index} className="border-t dark:border-gray-700">
                  <td className="py-2 px-4">{item.sku}</td>
                  <td className="py-2 px-4">{item.name}</td>
                  <td className="py-2 px-4">{item.stock}</td>
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