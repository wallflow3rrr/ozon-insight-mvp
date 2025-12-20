import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { api } from '../services/api';
import Card from '../components/UI/Card';
import RevenueChart from '../components/Dashboard/RevenueChart';
import ExportButton from '../components/Export/ExportButton';

const ProductDetailPage = () => {
  const { sku } = useParams();
  const { period } = useAppContext();
  const [productData, setProductData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await api.getProductDetail(sku, period);
      setProductData(data);
    } catch (error) {
      console.error("Failed to fetch product ", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [sku, period]);

  if (loading) return <div className="p-6">Загрузка...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Товар: {productData.name}</h1>
        {/*передача sku как строки */}
        <ExportButton data={productData} scope="product" period={period} logistics="both" sku={productData.sku} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">SKU</h3>
          <p className="text-xl font-bold text-gray-800 dark:text-gray-200">{productData.sku}</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Выручка</h3>
          <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{productData.revenue.toLocaleString()} ₽</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Продано</h3>
          <p className="text-xl font-bold text-green-600 dark:text-green-400">{productData.quantity_sold}</p>
        </Card>
        <Card>
          <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Остаток</h3>
          <p className="text-xl font-bold text-purple-600 dark:text-purple-400">{productData.stock}</p>
        </Card>
      </div>
      <div className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-100">Динамика продаж</h3>
        <RevenueChart data={{ revenue_chart: productData.sales_chart }} />
      </div>
    </div>
  );
};

export default ProductDetailPage;