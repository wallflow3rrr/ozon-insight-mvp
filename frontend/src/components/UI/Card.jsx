const Card = ({ children, className = "" }) => {
  return (
    <div className={`bg-white dark:bg-gray-800 p-5 rounded-xl shadow-md transition-all duration-200 hover:shadow-lg ${className}`}>
      {children}
    </div>
  );
};

export default Card;