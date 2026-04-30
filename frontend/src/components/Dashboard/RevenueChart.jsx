import React from 'react';
import { Line } from 'react-chartjs-2';
import {
Chart as ChartJS,
CategoryScale,
LinearScale,
PointElement,
LineElement,
Title,
Tooltip,
Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const RevenueChart = ({ data, title = 'Динамика выручки' }) => {
  if (!data || !data.revenue_chart) return <div className="text-center text-gray-500 dark:text-gray-400">Нет данных</div>;

  const chartData = {
    labels: data.revenue_chart.map(d => d.date),
    datasets: [
      {
        label: title,
        data: data.revenue_chart.map(d => d.value),
        fill: false,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.3,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { 
        display: true, 
        text: title,  // ✅ Динамический заголовок
        color: '#6b7280', 
        font: { size: 16 } 
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(209, 213, 219, 0.2)',
        },
        ticks: {
          color: '#6b7280',
        }
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#6b7280',
        }
      }
    }
  };

  return <Line data={chartData} options={options} />;
};

export default RevenueChart;