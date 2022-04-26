import telebot
from utils import save_book

from create_table_script import get_configs


TOKEN = get_configs().get('token')
MODERATOR_CHAT = get_configs().get('moderator_chat')

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_add = telebot.types.KeyboardButton(text="Добавить книгу")
    btn_search = telebot.types.KeyboardButton(text="Искать книгу")
    kb.add(btn_add, btn_search)
    bot.send_message(message.chat.id, "Приветствую тебя, " + message.from_user.first_name, reply_markup=kb)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == 'Добавить книгу':
        message = bot.send_message(
            chat_id=message.chat.id,
            text="Загрузи свою книгу в формате pdf и укажи в описании ключевые слова и год выпуска книги через запятую"
        )
        bot.register_next_step_handler(message, send_book)
    elif message.text == 'Искать книгу':
        bot.send_message(message.chat.id, "Можешь ввести название этой книги")
    else:
        bot.send_message(message.chat.id, "Не понимаю")


def send_book(message):
    document = message.document
    if not document:
        bot.send_message(message.chat.id, "Это не документ!")
        return

    file_id = document.file_id
    file_name = document.file_name
    mime_type = document.mime_type
    caption = message.caption

    if mime_type != 'application/pdf':
        bot.send_message(message.chat.id, "Этот документ не в формате pdf")
        return

    book_info = f'file_id: {file_id}\nfile_name: {file_name}\ncaption: {caption}'
    if message.chat.id != MODERATOR_CHAT:
        bot.send_message(message.chat.id, "Спасибо! Отправляю книгу на модерацию")
        bot.send_message(MODERATOR_CHAT, book_info)
    else:
        bot.send_message(message.chat.id, "Книга успешно добавлена!")
        save_book(book_info)


bot.polling()