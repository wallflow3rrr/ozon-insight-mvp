from csv_generator import generate_csv_files
from csv_parser import parse_and_load_csv
from metrics import calculate_daily_metrics

def run_full_seed():
    print(" Запуск полного цикла инициализации...")
    generate_csv_files(days=90)
    parse_and_load_csv()
    calculate_daily_metrics(user_id="mock_user_123", days=90)
    print("✅ Система полностью готова к работе")