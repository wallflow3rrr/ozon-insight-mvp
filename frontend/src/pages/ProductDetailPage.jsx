import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { api } from '../services/api';
import Card from '../components/UI/Card';
import RevenueChart from '../components/Dashboard/RevenueChart';
import ExportButton from '../components/Export/ExportButton';
import Button from '../components/UI/Button';

const ProductDetailPage = () => {
  const { sku } = useParams();
  const navigate = useNavigate();
  const { period } = useAppContext();
  const [productData, setProductData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // ✅ Запрос идет с SKU из URL
        const data = await api.getProductDetail(sku, period);
        setProductData(data);
      } catch (err) {
        console.error("Ошибка загрузки товара:", err);
        setError("Товар не найден или произошла ошибка загрузки.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [sku, period]);

  if (loading) return <div className="p-6 text-center text-gray-500">Загрузка данных товара...</div>;

  if (error || !productData) {
    return (
      <div className="p-6 text-center">
        <h2 className="text-xl font-bold text-red-600 mb-4">{error || "Данные не найдены"}</h2>
        <Button onClick={() => navigate('/dashboard')}>Вернуться на дашборд</Button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div>
          <Button onClick={() => navigate('/dashboard')} variant="secondary" className="mb-2 text-sm">
            ← Назад к списку
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{productData.name}</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">SKU: {productData.sku}</p>
        </div>
        <ExportButton 
          data={productData} 
          scope="product" 
          period={period} 
          logistics="both" 
          sku={productData.sku} 
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Выручка</h3>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">
            {productData.revenue?.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽
          </p>
        </Card>
        <Card>
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Продано (шт.)</h3>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{productData.quantity_sold}</p>
        </Card>
        <Card>
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Остаток на складе</h3>
          <p className="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">{productData.stock} шт.</p>
        </Card>
        <Card>
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Тип логистики</h3>
          <p className="text-2xl font-bold text-gray-800 dark:text-gray-200 mt-1">
            {productData.logistics || 'FBO'}
          </p>
        </Card>
      </div>

      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-100">Динамика продаж</h3>
        <RevenueChart data={{ revenue_chart: productData.sales_chart }} />
      </div>
    </div>
  );
};

export default ProductDetailPage;