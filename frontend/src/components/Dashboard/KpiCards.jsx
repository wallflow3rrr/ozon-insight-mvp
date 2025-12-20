import React from 'react';
import Card from '../UI/Card';

const KpiCards = ({ data }) => {
  if (!data || !data.kpi) return <div className="p-6 text-center text-gray-500 dark:text-gray-400">Загрузка...</div>;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
      <Card>
        <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Выручка</h3>
        <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{data.kpi.revenue.toLocaleString()} ₽</p>
      </Card>
      <Card>
        <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Заказы</h3>
        <p className="text-3xl font-bold text-green-600 dark:text-green-400">{data.kpi.orders}</p>
      </Card>
      <Card>
        <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Средний чек</h3>
        <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">{data.kpi.avg_check} ₽</p>
      </Card>
      <Card>
        <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Возвраты</h3>
        <p className="text-3xl font-bold text-red-600 dark:text-red-400">{data.kpi.return_rate}%</p>
      </Card>
    </div>
  );
};

export default KpiCards;