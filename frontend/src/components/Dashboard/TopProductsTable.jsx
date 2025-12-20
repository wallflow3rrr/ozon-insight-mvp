import React from 'react';
import { Link } from 'react-router-dom';

const TopProductsTable = ({ data }) => {
  // Функция для преобразования "Товар N" в "SKU_N" или "SKU_N"
  const getSKUFromName = (name) => {
    // Ищем число в строке "Товар N"
    const match = name.match(/Товар\s*(\d+)/i);
    if (match) {
      return `SKU${match[1]}`; // Возвращаем SKU1, SKU2, и т.д.
    }
    return name; // Если не найдено, возвращаем как есть
  };

  return (
    <table className="min-w-full">
      <thead>
        <tr>
          <th className="py-2 px-4 text-left">SKU</th>
          <th className="py-2 px-4 text-left">Название</th>
          <th className="py-2 px-4 text-left">Выручка</th>
          <th className="py-2 px-4 text-left">Остаток</th>
          <th className="py-2 px-4 text-left">Логистика</th>
        </tr>
      </thead>
      <tbody>
        {data?.top_products?.map((item, index) => (
          <tr key={index} className="border-t dark:border-gray-700">
            <td className="py-2 px-4">
              <Link to={`/product/${getSKUFromName(item.name)}`} className="text-blue-500 hover:underline">
                {getSKUFromName(item.name)} {/* ✅ Выводим SKU вместо name */}
              </Link>
            </td>
            <td className="py-2 px-4">{item.name}</td>
            <td className="py-2 px-4">{item.revenue?.toLocaleString()} ₽</td>
            <td className="py-2 px-4">{item.stock}</td>
            <td className="py-2 px-4">{item.logistics}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default TopProductsTable;