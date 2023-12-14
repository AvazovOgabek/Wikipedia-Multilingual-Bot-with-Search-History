import telebot
from googletrans import Translator
import wikipedia
from telebot import types
from datetime import datetime
from decouple import config
import json
import time

BOT_TOKEN = config('BOT_TOKEN')
CHANNEL_USERNAME = '@sudowikipedia'
wikipedia.set_lang("uz")  


bot = telebot.TeleBot(BOT_TOKEN)

search_history = {}
MAX_QUERY_LENGTH = 300


@bot.message_handler(commands=['start'])
def handle_start(message):
    javob = "Assalomu alaykum! Men sizning so'rovingizga Wikipedia malumot tastiqlangan olib qaytaraman."
    bot.send_message(message.chat.id, javob)

@bot.message_handler(commands=['history'])
def handle_history(message):
    user_id = message.from_user.id
    if user_id in search_history and search_history[user_id]:
        tarix = "\n".join(search_history[user_id])
        javob = f"Foydalanuvchi qidirgan so'rovlari tarixi:\n{tarix}"
        keyboard = types.InlineKeyboardMarkup()
        button_clear_history = types.InlineKeyboardButton(text='Tarixni Tozalash', callback_data='clear_history')
        button_clear_last_search = types.InlineKeyboardButton(text='Ohirgi Qidiruvni Tozalash', callback_data='clear_last_search')
        keyboard.add(button_clear_history, button_clear_last_search)
        bot.send_message(message.chat.id, javob, reply_markup=keyboard, parse_mode='Markdown')
    else:
        javob = "Foydalanuvchi hech qanday qidiruv bajarilmagan✖️"
        bot.send_message(message.chat.id, javob)

def send_wikipedia_message(message, bot, keyboard, chunk):
    try:

        chunk_size = 4096
        chunks = [chunk[i:i + chunk_size] for i in range(0, len(chunk), chunk_size)]

        for sub_chunk in chunks:
            bot.send_message(message.chat.id, f"`{sub_chunk}`", reply_markup=keyboard, parse_mode='Markdown')
            log_search_history(message.from_user.id, f"`{message.text}` |✔️")


            time.sleep(1)

    except telebot.apihelper.ApiTelegramException as e:
        if e.result.status_code == 429:
            retry_after = e.result.json()['parameters']['retry_after']
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            send_wikipedia_message(message, bot, keyboard, chunk)
        else:
            print(f"Error: {str(e)}")
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        query = message.text[:MAX_QUERY_LENGTH]
        search_result = wikipedia.summary(query)
        search_result = wikipedia.summary(message.text)
        keyboard = types.InlineKeyboardMarkup()
        button_eng = types.InlineKeyboardButton(text='Inglizcha', callback_data='en')
        button_rus = types.InlineKeyboardButton(text='Ruscha', callback_data='ru')
        button_uzb = types.InlineKeyboardButton(text='O\'zbekcha', callback_data='uz')
        keyboard.add(button_eng, button_rus, button_uzb)

        chunk_size = 4000  
        chunks = [search_result[i:i + chunk_size] for i in range(0, len(search_result), chunk_size)]

        for chunk in chunks:
            send_wikipedia_message(message, bot, keyboard, chunk)

    except wikipedia.exceptions.DisambiguationError as e:
        javob = "Kerakli ma'lumotni topa olmadim. Iltimos, boshqa so'rov yuboring."
        bot.send_message(message.chat.id, javob)
        log_search_history(message.from_user.id, f"`{message.text}` |✖️")
    except wikipedia.exceptions.PageError as e:
        javob = "Bunday ma'lumot topa olmadim. Iltimos, boshqa so'rov yuboring."
        bot.send_message(message.chat.id, javob)
        log_search_history(message.from_user.id, f"`{message.text}` |✖️")
    except json.decoder.JSONDecodeError:
        javob = "Wikipedia dan kelgan ma'lumot JSON formatida emas. Iltimos, boshqa so'rov yuboring."
        bot.send_message(message.chat.id, javob)
        log_search_history(message.from_user.id, f"`{message.text}` |✖️")
    except wikipedia.exceptions.WikipediaException as e:
        error_message = f"Wikipedia API dan xato: {str(e)}"
        bot.send_message(message.chat.id, error_message)
        log_search_history(message.from_user.id, f"`{message.text}` |✖️")



@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.message:
        user_id = call.from_user.id
        translator = Translator()
        if call.data == 'en':
            tarjima = translator.translate(call.message.text, src='uz', dest='en').text
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"`{tarjima}`", parse_mode='Markdown')
        elif call.data == 'ru':
            tarjima = translator.translate(call.message.text, src='uz', dest='ru').text
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"`{tarjima}`", parse_mode='Markdown')
        elif call.data == 'uz':
            tarjima = call.message.text
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"`{tarjima}`", parse_mode='Markdown')
        elif call.data == 'clear_history':
            search_history[user_id] = []  
            bot.send_message(call.message.chat.id, "Foydalanuvchi qidiruvlar tarixi tozalandi✔️")
            user_id = call.from_user.id     
            javob = "Foydalanuvchi hech qanday qidiruv bajarilmagan✖️"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=javob)

        elif call.data == 'clear_last_search':
            if user_id in search_history and search_history[user_id]:
                del search_history[user_id][-1] 
                bot.send_message(call.message.chat.id, "Oxirgi qidirilgan ma'lumot o'chirildi✔️")
            else:
                bot.send_message(call.message.chat.id, "Foydalanuvchi hech qanday qidiruv bajarilmagan✖️")
            keyboard = types.InlineKeyboardMarkup()
            button_clear_history = types.InlineKeyboardButton(text='Tarixni Tozalash', callback_data='clear_history')
            button_clear_last_search = types.InlineKeyboardButton(text='Ohirgi Qidiruvni Tozalash', callback_data='clear_last_search')
            keyboard.add(button_clear_history, button_clear_last_search)
            user_id = call.from_user.id     
            if user_id in search_history and search_history[user_id]:
                tarix = "\n".join(search_history[user_id])
                javob = f"Foydalanuvchi qidirgan so'rovlari tarixi:\n{tarix}"
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=javob, reply_markup=keyboard, parse_mode='Markdown')
            else:
                javob = "Foydalanuvchi hech qanday qidiruv bajarilmagan✖️"
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=javob)

def log_search_history(user_id, query):
    if user_id not in search_history:
        search_history[user_id] = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    search_history[user_id].append(f"{current_time}: {query}")

bot.polling(none_stop=True)
