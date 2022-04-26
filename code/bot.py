import telebot
from utils import save_book, find_book_in_db_by_title, get_file_id, find_book_in_db_by_author, \
    find_book_in_db_by_keywords, find_last_books

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
            text="Загрузи свою книгу (pdf) и укажи в описании автора, ключевые слова и год выпуска книги через запятую"
        )
        bot.register_next_step_handler(message, send_book)
    elif message.text == 'Искать книгу':
        kb = telebot.types.InlineKeyboardMarkup(row_width=1)
        title_btn = telebot.types.InlineKeyboardButton(text="По названию", callback_data="search_title")
        author_btn = telebot.types.InlineKeyboardButton(text="По автору", callback_data="search_author")
        keyword_btn = telebot.types.InlineKeyboardButton(text="По ключевым словам", callback_data="search_keywords")
        last_btn = telebot.types.InlineKeyboardButton(text="Последние добавленные", callback_data="show_last")
        kb.add(title_btn, author_btn, keyword_btn, last_btn)
        bot.send_message(message.chat.id, "Выберите один из вариантов поиска", reply_markup=kb)
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


@bot.callback_query_handler(func=lambda c: c.data)
def answer_callback(callback):
    if callback.data == "search_title":
        message = bot.send_message(
            chat_id=callback.message.chat.id,
            text="Просто введи название или его часть и я постараюсь найти эту книгу"
        )
        bot.register_next_step_handler(message, find_by_title)
    elif callback.data == "search_author":
        message = bot.send_message(
            chat_id=callback.message.chat.id,
            text="Просто введи автора и я постараюсь найти эту книгу"
        )
        bot.register_next_step_handler(message, find_by_author)
    elif callback.data == "search_keywords":
        message = bot.send_message(
            chat_id=callback.message.chat.id,
            text="Просто введи ключевые слова через запятую и я постараюсь найти подходящую книгу"
        )
        bot.register_next_step_handler(message, find_by_keywords)
    elif callback.data.startswith("book_id"):
        book_id = callback.data.strip("book_id")
        file_id = get_file_id(int(book_id))[0]
        bot.send_document(callback.message.chat.id, file_id)


def show_result(result, message):
    if not result:
        bot.send_message(message.chat.id, "По вашему запросу ничего не найдено")
        return
    kb = telebot.types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        telebot.types.InlineKeyboardButton(text=str(idx+1) + ". " + item[0], callback_data="book_id" + str(item[1]))
        for idx, item in enumerate(result)
    ]
    kb.add(*buttons)
    bot.send_message(message.chat.id, "Вот, что я нашел:", reply_markup=kb)


def find_by_title(message):
    result = find_book_in_db_by_title(message.text.replace(' ', '_'))
    show_result(result, message)


def find_by_author(message):
    result = find_book_in_db_by_author(message.text.replace(' ', '_'))
    show_result(result, message)


def find_by_keywords(message):
    keywords = [item.strip().replace(' ', '_') for item in message.text.split(',')]
    result = find_book_in_db_by_keywords(keywords)
    show_result(result, message)


bot.infinity_polling()