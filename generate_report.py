from analytics import generate_weekly_report

if __name__ == "__main__":
    report_path = generate_weekly_report()
    print(f"Отчёт сохранён: {report_path}")