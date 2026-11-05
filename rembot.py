import telebot
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from telebot import types

bot = telebot.TeleBot('вставить токен сюда')
DB_PATH = 'reminders.db'

bot.set_my_commands([
    types.BotCommand('/start', 'Запустить бота'),
    types.BotCommand('/rsec', 'Установить напоминание'),
    types.BotCommand('/rmin', 'Установить напоминание на минуты'),
    types.BotCommand('/rhour', 'Установить напоминание на часы'),
    types.BotCommand('/list', 'Показать активные напоминания'),
])

# --- Инициализация базы данных ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            text TEXT,
            remind_at INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def cmd_start(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id,
        f"Привет, {name}! Я uinen. Напиши /rsec <секунды> <текст>, /rmin для минутных напоминаний, /rhour для часовых напоминаний или /list.")

# --- Команда /rsec ---
@bot.message_handler(commands=['rsec'])
def set_reminder(message):
    # Ожидаем формат: /rsec 60 Выпить воды
    # 60 — это количество секунд (для теста удобно)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /rsec <секунды> <текст>\nПример: /rsec 60 Позвонить маме")
        return

    try:
        seconds = int(parts[1])
        text = parts[2]
    except ValueError:
        bot.reply_to(message, "Первое значение после команды должно быть числом секунд.")
        return

    remind_at = int(time.time()) + seconds
    chat_id = message.chat.id

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reminders (chat_id, text, remind_at) VALUES (?, ?, ?)",
        (chat_id, text, remind_at)
    )
    conn.commit()
    conn.close()

    bot.reply_to(message, f"Ок, напомню через {seconds} секунд: «{text}»")

@bot.message_handler(commands=['rmin'])
def set_reminder_minutes(message):
    # Ожидаем формат: /rmin 60 Выпить воды
    # 60 — это количество минут (для теста удобно)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /rmin <минуты> <текст>\nПример: /rmin 5 Пить воду")
        return

    try:
        minutes = int(parts[1])
        seconds = minutes * 60  # Преобразуем минуты в секунды
        text = parts[2]
    except ValueError:
        bot.reply_to(message, "Первое значение после команды должно быть числом минут.")
        return

    remind_at = int(time.time()) + seconds
    chat_id = message.chat.id

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reminders (chat_id, text, remind_at) VALUES (?, ?, ?)",
        (chat_id, text, remind_at)
    )
    conn.commit()
    conn.close()

    bot.reply_to(message, f"Ок, напомню через {minutes} минут ({seconds} секунд): «{text}»")

@bot.message_handler(commands=['rhour'])
def set_reminder_hours(message):
    # Ожидаем формат: /rhour 1 Выпить воды
    # 1 — это количество часов (для теста удобно)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /rhour <часы> <текст>\nПример: /rhour 1 Пить воду")
        return

    try:
        hours = int(parts[1])
        seconds = hours * 3600  # Преобразуем часы в секунды
        text = parts[2]
    except ValueError:
        bot.reply_to(message, "Первое значение после команды должно быть числом часов.")
        return

    remind_at = int(time.time()) + seconds
    chat_id = message.chat.id

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reminders (chat_id, text, remind_at) VALUES (?, ?, ?)",
        (chat_id, text, remind_at)
    )
    conn.commit()
    conn.close()

    bot.reply_to(message, f"Ок, напомню через {hours} часов ({seconds} секунд): «{text}»")

# --- Команда /list ---
@bot.message_handler(commands=['list'])
def list_reminders(message):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT text, remind_at FROM reminders WHERE chat_id = ?", (message.chat.id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        bot.reply_to(message, "У тебя нет активных напоминаний.")
        return

    lines = ["Твои напоминания:"]
    for text, remind_at in rows:
        dt = datetime.fromtimestamp(remind_at).strftime('%H:%M:%S')
        lines.append(f"• {text} (в {dt})")
    bot.reply_to(message, "\n".join(lines))

# --- Фоновый поток проверки ---
def reminder_worker():
    while True:
        now = int(time.time())
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # Ищем напоминания, время которых уже наступило
        cur.execute("SELECT id, chat_id, text FROM reminders WHERE remind_at <= ?", (now,))
        due = cur.fetchall()

        for rem_id, chat_id, text in due:
            try:
                bot.send_message(chat_id, f"⏰ Напоминание: {text}")
            except Exception as e:
                print(f"Ошибка отправки: {e}")
            # Удаляем выполненное напоминание
            cur.execute("DELETE FROM reminders WHERE id = ?", (rem_id,))

        conn.commit()
        conn.close()
        time.sleep(2)  # проверяем каждые 2 секунды

# Запускаем фоновый поток при старте
threading.Thread(target=reminder_worker, daemon=True).start()

# --- Обработка остального текста (твой старый код) ---
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.lower() == 'привет':
        bot.reply_to(message, "Привет! Я умею напоминать. Напиши:"
        "\n/rsec секунды текст" \
        "\n/rmin минуты текст" \
        "\n/rhour часы текст" \
        "\n/list чтобы увидеть активные напоминания.")
    else:
        bot.reply_to(message, "Я не понял. Напиши /rsec <секунды> <текст> или /list")

print("Бот запущен...")
bot.infinity_polling()