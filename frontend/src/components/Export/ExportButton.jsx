import React from 'react';
import Button from '../UI/Button';
import { api } from '../../services/api';

const ExportButton = ({ data, scope, period, logistics, sku = null }) => {
  const handleExport = () => {
    if (scope === 'product' && (!sku || sku === null)) {
      alert('SKU товара не передан. Невозможно экспортировать.');
      return;
    }

    const url = api.exportReport(scope, 'xlsx', period, logistics, sku);
    window.open(url, '_blank');
  };

  return (
    <Button onClick={handleExport} variant="secondary">
      Экспорт в Excel
    </Button>
  );
};

export default ExportButton;