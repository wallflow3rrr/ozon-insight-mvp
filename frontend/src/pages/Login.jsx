import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/UI/Button';

const Login = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate('/dashboard');
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-xl w-full max-w-md">
        <div className="text-center mb-6">
          <div className="mx-auto bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16 dark:bg-gray-700" />
          <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">OzonInsight</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-300">
            Подключите свой аккаунт Ozon для начала анализа
          </p>
        </div>
        <Button onClick={handleLogin} className="w-full py-3 text-base">
          Войти через Ozon
        </Button>
        <p className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
          Ваши данные не передаются и не хранятся.
        </p>
      </div>
    </div>
  );
};

export default Login;