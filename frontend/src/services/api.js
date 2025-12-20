const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Синхронизация
  getSyncStatus: () => fetch(`${API_BASE_URL}/api/sync/status`).then(res => res.json()),
  triggerSync: () => fetch(`${API_BASE_URL}/api/sync/trigger`, { method: 'POST' }).then(res => res.json()),

  // Дашборд
  getDashboardData: (period, logistics) => 
    fetch(`${API_BASE_URL}/api/dashboard?period=${period}&logistics=${logistics}`).then(res => res.json()),

  // Товар
  getProductDetail: (sku, period) => 
    fetch(`${API_BASE_URL}/api/product/${sku}?period=${period}`).then(res => res.json()),

  // Экспорт
  exportReport: (scope, format, period, logistics, sku = null) => {
    const params = new URLSearchParams({ scope, format, period, logistics });
    if (scope === 'product' && sku) {
      params.append('sku', sku);
    }
    return `${API_BASE_URL}/api/export?${params}`;
  },

  // Подсказки
  getMetricTooltip: (metricKey) => 
    fetch(`${API_BASE_URL}/api/metric-tooltip?metric_key=${metricKey}`).then(res => res.json()),
};