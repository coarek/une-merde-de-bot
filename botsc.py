import logging
import telebot
from telebot import types

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot('вставить токен сюда')

bot.set_my_commands([
    types.BotCommand('start', 'Запустить бота'),
    types.BotCommand('help', 'Что я умею'),
    types.BotCommand('bio', 'Обо мне'),
    types.BotCommand('files', 'Получить файлы'),
])

@bot.message_handler(commands=['start'])
def cmd_start(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id,
        f"Привет, {name}! Я uinen. Напиши /help, чтобы узнать, что я умею.")

@bot.message_handler(commands=['help'])
def cmd_help(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('📄 Выслать файлы', callback_data='files'),
        types.InlineKeyboardButton('💱 Курс валют', callback_data='rate'),
        types.InlineKeyboardButton('🤪 Пострадать хуйнёй', callback_data='fun'),
    )
    bot.send_message(message.chat.id, 'Выбери, что тебе нужно:', reply_markup=markup)

@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    bot.answer_callback_query(call.id) 
    if call.data == 'files':
        bot.send_message(call.message.chat.id, 'Файлы пока в разработке 🙂')
    elif call.data == 'rate':
        bot.send_message(call.message.chat.id, 'Курс валют: API пока не подключён.')
    elif call.data == 'fun':
        bot.send_message(call.message.chat.id,
            'https://www.youtube.com/watch?v=VbyCPXBD77w вот это вот блять')

@bot.message_handler(commands=['bio'])
def cmd_bio(message):
    bot.send_message(message.chat.id, 'Я — uinen, сделан по приколу. И всё.')

@bot.message_handler(commands=['files'])
def cmd_files(message):
    bot.send_message(message.chat.id, 'Файлы пока в разработке.')

@bot.message_handler(content_types=['text'])
def on_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет! Напиши /help, чтобы узнать, что я умею.')
    else:
        bot.send_message(message.chat.id, 'Не понял. Напиши /help.')

if __name__ == '__main__':
    bot.infinity_polling(timeout=30, long_polling_timeout=20)