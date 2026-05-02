const API_BASE_URL = 'http://localhost:8000';

// Получаем токен из localStorage
const getToken = () => localStorage.getItem('access_token');

// Формируем заголовки с токеном
const getAuthHeaders = () => ({
  'Content-Type': 'application/json',
  ...(getToken() && { Authorization: `Bearer ${getToken()}` }),
});

// Универсальная функция запроса с авторизацией
const authFetch = async (url, options = {}) => {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: { ...getAuthHeaders(), ...options.headers },
  });

  // Если сервер вернул 401 (токен невалидный/истёк) — очищаем хранилище и редиректим
  if (response.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    throw new Error('Session expired');
  }

  return response;
};

export const api = {
  // === DASHBOARD ===
  getDashboardData: (period, logistics) =>
    authFetch(`/api/dashboard?period=${period}&logistics=${logistics}`).then(res => res.json()),

  // === STOCK ===
  getStockData: (period, logistics) =>
    authFetch(`/api/stock?period=${period}&logistics=${logistics}`).then(res => res.json()),

  // === LOGISTICS ===
  getLogisticsData: (period, logistics) =>
    authFetch(`/api/logistics?period=${period}&logistics=${logistics}`).then(res => res.json()),

  // === RETURNS ===
  getReturnsData: (period, logistics) =>
    authFetch(`/api/returns?period=${period}&logistics=${logistics}`).then(res => res.json()),

  // === PRODUCT DETAIL ===
  getProductDetail: (sku, period) =>
    authFetch(`/api/product/${sku}?period=${period}`).then(res => res.json()),

  // === SYNC ===
  getSyncStatus: () => authFetch('/api/sync/status').then(res => res.json()),
  triggerSync: () => authFetch('/api/sync/trigger', { method: 'POST' }).then(res => res.json()),

  // === EXPORT ===
  exportReport: async (scope, format, period, logistics, sku = null) => {
  const params = new URLSearchParams({ scope, format, period, logistics });
  if (scope === 'product' && sku) params.append('sku', sku);
  
  const response = await fetch(`${API_BASE_URL}/api/export?${params.toString()}`, {
    headers: getAuthHeaders(),
  });
  
    // ✅ Показываем реальный статус и текст ошибки, а не заглушку
    if (!response.ok) {
     const errorText = await response.text();
     throw new Error(`Ошибка ${response.status}: ${errorText}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${scope}_${period}.xlsx`;
    a.click();
    window.URL.revokeObjectURL(url);
  },

  // === METRIC TOOLTIPS ===
  getMetricTooltip: (metricKey) =>
    fetch(`${API_BASE_URL}/api/metric-tooltip?metric_key=${metricKey}`).then(res => res.json()),

  // === AUTH (logout) ===
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  },
};