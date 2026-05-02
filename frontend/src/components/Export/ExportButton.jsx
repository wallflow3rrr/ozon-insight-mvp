import React, { useState } from 'react';
import { api } from '../../services/api';
import Button from '../UI/Button';

const ExportButton = ({ scope, period, logistics, sku }) => {
  const [loading, setLoading] = useState(false);

  const handleExport = async (e) => {
    e.preventDefault(); // ✅ Блокируем переход по ссылке
    setLoading(true);

    try {
      // api.exportReport() уже отправляет заголовок Authorization: Bearer ...
      await api.exportReport(scope, 'xlsx', period, logistics, sku);
    } catch (error) {
      console.error('Ошибка экспорта:', error);
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button onClick={handleExport} disabled={loading} className="ml-2">
      {loading ? '⏳ Генерация...' : '📥 Экспорт в Excel'}
    </Button>
  );
};

export default ExportButton;