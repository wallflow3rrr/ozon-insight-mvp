import React from 'react';
import { useNavigate } from 'react-router-dom';

const TopProductsTable = ({ data }) => {
  const navigate = useNavigate();

  if (!data || !data.top_products) return <div className="text-center text-gray-500 dark:text-gray-400">Нет данных</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white dark:bg-gray-800 rounded-lg overflow-hidden">
        <thead className="bg-gray-100 dark:bg-gray-700">
          <tr>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">SKU</th>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Название</th>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Выручка</th>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Остаток</th>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Логистика</th>
          </tr>
        </thead>
        <tbody>
          {data.top_products.map((product, index) => (
            <tr
              key={product.sku}
              className={`hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors ${index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'}`}
              onClick={() => navigate(`/product/${product.sku}`)}
            >
              <td className="py-3 px-4 border-t dark:border-gray-700 text-gray-800 dark:text-gray-200">{product.sku}</td>
              <td className="py-3 px-4 border-t dark:border-gray-700 text-gray-800 dark:text-gray-200">{product.name}</td>
              <td className="py-3 px-4 border-t dark:border-gray-700 text-gray-800 dark:text-gray-200">{product.revenue.toLocaleString()} ₽</td>
              <td className="py-3 px-4 border-t dark:border-gray-700 text-gray-800 dark:text-gray-200">{product.stock}</td>
              <td className="py-3 px-4 border-t dark:border-gray-700">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    product.logistics === 'FBO' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                  }`}
                >
                  {product.logistics}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TopProductsTable;