import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from analytics import generate_weekly_report  # наш модуль

def send_email_with_report(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    recipient_email: str,
    subject: str,
    body: str,
    attachment_path: str
):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f"attachment; filename= {os.path.basename(attachment_path)}",
    )

    msg.attach(part)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()

def main():
    # Генерируем отчёт
    report_path = generate_weekly_report()

    # Настройки почты (замените на свои)
    SMTP_SERVER = "smtp.yandex.ru"  # для Яндекса
    SMTP_PORT = 587
    SENDER_EMAIL = "your_email@yandex.ru"
    SENDER_PASSWORD = "your_app_password"  # не пароль от почты, а "приложение"
    RECIPIENT_EMAIL = "client@company.ru"

    # Тема и текст письма
    subject = f"Недельный отчёт от {datetime.now().strftime('%d.%m.%Y')}"
    body = f"""
    Добрый день!

    Прикреплён недельный отчёт от {datetime.now().strftime('%d.%m.%Y')} по работе Telegram-бота.

    В отчёте:
    - Откуда пришли клиенты
    - Сколько токенов OpenAI потрачено
    - Средняя оценка бота
    - Частые вопросы

    С уважением,
    Ваша команда
    """

    send_email_with_report(
        SMTP_SERVER,
        SMTP_PORT,
        SENDER_EMAIL,
        SENDER_PASSWORD,
        RECIPIENT_EMAIL,
        subject,
        body,
        report_path
    )

    print(f"Отчёт отправлен на {RECIPIENT_EMAIL}")

if __name__ == "__main__":
    main()