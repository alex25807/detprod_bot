import os
import csv
import json
from datetime import datetime, timedelta
import pandas as pd

LOGS_DIR = "logs"
REPORTS_DIR = "reports"

# Убедимся, что папки существуют
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ================ ЛОГИРОВАНИЕ СОБЫТИЙ ================

def log_new_client(user_id: int, source: str, timestamp: str = None):
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    with open(os.path.join(LOGS_DIR, "clients.csv"), "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["user_id", "source", "timestamp"])
        writer.writerow([user_id, source, timestamp])

def log_question(user_id: int, question: str, timestamp: str = None):
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    with open(os.path.join(LOGS_DIR, "questions.csv"), "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["user_id", "question", "timestamp"])
        writer.writerow([user_id, question, timestamp])

def log_rating(user_id: int, rating: int, timestamp: str = None):
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    with open(os.path.join(LOGS_DIR, "ratings.csv"), "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["user_id", "rating", "timestamp"])
        writer.writerow([user_id, rating, timestamp])

def log_token_usage(prompt_tokens: int, completion_tokens: int, total_tokens: int, timestamp: str = None):
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    with open(os.path.join(LOGS_DIR, "tokens.csv"), "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["timestamp", "prompt_tokens", "completion_tokens", "total_tokens"])
        writer.writerow([timestamp, prompt_tokens, completion_tokens, total_tokens])

# ================ ГЕНЕРАЦИЯ НЕДЕЛЬНОГО ОТЧЁТА ================

def generate_weekly_report() -> str:
    """Создаёт отчёт за последние 7 дней. Возвращает путь к файлу."""
    seven_days_ago = datetime.now() - timedelta(days=7)

    # Загружаем данные
    clients_df = pd.read_csv(os.path.join(LOGS_DIR, "clients.csv"), parse_dates=["timestamp"]) if os.path.exists(os.path.join(LOGS_DIR, "clients.csv")) else pd.DataFrame()
    questions_df = pd.read_csv(os.path.join(LOGS_DIR, "questions.csv"), parse_dates=["timestamp"]) if os.path.exists(os.path.join(LOGS_DIR, "questions.csv")) else pd.DataFrame()
    ratings_df = pd.read_csv(os.path.join(LOGS_DIR, "ratings.csv"), parse_dates=["timestamp"]) if os.path.exists(os.path.join(LOGS_DIR, "ratings.csv")) else pd.DataFrame()
    tokens_df = pd.read_csv(os.path.join(LOGS_DIR, "tokens.csv"), parse_dates=["timestamp"]) if os.path.exists(os.path.join(LOGS_DIR, "tokens.csv")) else pd.DataFrame()

    # Фильтруем за 7 дней
    if not clients_df.empty:
        clients_df = clients_df[clients_df["timestamp"] >= seven_days_ago]
    if not questions_df.empty:
        questions_df = questions_df[questions_df["timestamp"] >= seven_days_ago]
    if not ratings_df.empty:
        ratings_df = ratings_df[ratings_df["timestamp"] >= seven_days_ago]
    if not tokens_df.empty:
        tokens_df = tokens_df[tokens_df["timestamp"] >= seven_days_ago]

    # Агрегация
    total_clients = len(clients_df)
    top_sources = clients_df["source"].value_counts().to_dict() if not clients_df.empty else {}
    total_questions = len(questions_df)
    top_questions = questions_df["question"].value_counts().head(10).to_dict() if not questions_df.empty else {}
    avg_rating = round(ratings_df["rating"].mean(), 1) if not ratings_df.empty else 0
    total_tokens = tokens_df["total_tokens"].sum() if not tokens_df.empty else 0
    estimated_cost_usd = round(total_tokens * 0.00000015, 3)  # gpt-4o-mini: ~$0.15/1M токенов

    summary = {
        "Отчёт за": f"{seven_days_ago.strftime('%Y-%m-%d')} – {datetime.now().strftime('%Y-%m-%d')}",
        "Новые клиенты": total_clients,
        "Топ источников": json.dumps(top_sources, ensure_ascii=False),
        "Всего вопросов": total_questions,
        "Топ вопросов": json.dumps(top_questions, ensure_ascii=False),
        "Средняя оценка": f"{avg_rating} ⭐",
        "Потрачено токенов": int(total_tokens),
        "Расходы на OpenAI (примерно)": f"${estimated_cost_usd}"
    }

    # Путь к файлу
    report_path = os.path.join(REPORTS_DIR, f"weekly_report_{datetime.now().strftime('%Y%m%d')}.xlsx")

    # Сохраняем в Excel
    with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
        pd.DataFrame([summary]).to_excel(writer, sheet_name="Сводка", index=False)
        if not clients_df.empty:
            clients_df.to_excel(writer, sheet_name="Клиенты", index=False)
        if not questions_df.empty:
            questions_df.to_excel(writer, sheet_name="Вопросы", index=False)
        if not ratings_df.empty:
            ratings_df.to_excel(writer, sheet_name="Оценки", index=False)
        if not tokens_df.empty:
            tokens_df.to_excel(writer, sheet_name="Токены", index=False)

    return report_path