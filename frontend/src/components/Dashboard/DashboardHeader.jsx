import React, { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { PERIODS, LOGISTICS_TYPES } from '../../utils/constants';
//import { api } from '../../services/api';
import Button from '../UI/Button';

const DashboardHeader = ({ onSync }) => {
  const { period, setPeriod, logistics, setLogistics } = useAppContext();
  const [syncStatus, setSyncStatus] = useState(null);

  const handleSync = async () => {
    setSyncStatus('loading');
    try {
      // ✅ Вызываем onSync, который передаётся из родительского компонента (Dashboard)
      await onSync();
      setSyncStatus('success');
    } catch (error) {
      setSyncStatus('error');
    } finally {
      setTimeout(() => setSyncStatus(null), 2000);
    }
  };

  return (
    <div className="mb-6 p-4 bg-white dark:bg-gray-800 rounded-xl shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="flex flex-wrap items-center gap-2">
        {PERIODS.map((p) => (
          <button
            key={p.value}
            onClick={() => setPeriod(p.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              period === p.value
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200'
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {LOGISTICS_TYPES.map((l) => (
          <label key={l.value} className="flex items-center gap-1 cursor-pointer">
            <input
              type="checkbox"
              checked={logistics === l.value || (logistics === 'both' && l.value !== 'both')}
              onChange={() => setLogistics(l.value)}
              className="form-checkbox h-4 w-4 text-blue-600 rounded"
            />
            <span className="text-gray-700 dark:text-gray-300">{l.label}</span>
          </label>
        ))}
      </div>

      <div className="flex gap-2">
        <Button onClick={handleSync} disabled={syncStatus === 'loading'}>
          {syncStatus === 'loading' ? 'Обновление...' : '🔄 Синхронизировать'}
        </Button>
        {syncStatus && (
          <span className={`text-sm ${syncStatus === 'success' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            {syncStatus === 'success' ? '✓ Обновлено' : 'Ошибка'}
          </span>
        )}
      </div>
    </div>
  );
};

export default DashboardHeader;