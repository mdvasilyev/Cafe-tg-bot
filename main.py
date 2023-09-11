import pandas as pd
import re
import asyncio
import psycopg2
from psycopg2.extras import DictCursor
import telebot
from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import types
import datetime

conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor(cursor_factory=DictCursor)

token = open("token.txt").read()
bot = AsyncTeleBot(token, state_storage=StateMemoryStorage())

admins = [1208161291, 659350346]
actual_admin = admins[0]
df = pd.read_excel("dishes.xlsx")
max_dish = len(df)


class MyStates(StatesGroup):
    address = State()
    phone = State()


async def setup_bot_commands():
    await bot.delete_my_commands()
    bot_commands = [
        telebot.types.BotCommand("/start", "Начальная страница"),
        telebot.types.BotCommand("/menu", "Посмотреть меню"),
        telebot.types.BotCommand("/address", "Ввести адрес и оплату"),
        telebot.types.BotCommand("/phone", "Ввести номер телефона"),
        telebot.types.BotCommand("/group", "Перейти в группу")
    ]
    await bot.set_my_commands(bot_commands)


@bot.message_handler(commands=["start", "help"])
async def start(message):
    query = "INSERT INTO canteen (user_id, order_list) SELECT %s, '{}'" \
            "WHERE NOT EXISTS (SELECT (user_id, order_list, courier_check) FROM canteen WHERE user_id = %s);"
    data = (message.from_user.id, message.from_user.id)
    cur.execute(query, data)
    conn.commit()
    markup = start_menu()
    send_mess = f"Привет, <b>{message.from_user.first_name}</b>!\nЯ бот \U0001F916, который поможет " \
                f"тебе сделать заказ \U0001F4C4. Пользуйся меню с командами и кнопками ниже \U0001F447"
    await bot.send_message(message.chat.id, send_mess, parse_mode="html", reply_markup=markup)


@bot.message_handler(commands=["menu"])
async def menu(message):
    date = datetime.date.today().strftime("%d.%m.%y")
    sections = df[:0].columns.values
    whole_menu = []
    for i in sections:
        whole_menu.append(i)
        whole_menu.append(gen_menu(df, i))
    result = "\n\n".join([f"Меню на <b>{date}</b>", "\n\n".join(whole_menu)])
    await bot.send_message(message.chat.id, result, parse_mode="html")


@bot.message_handler(commands=["address"])
async def address(message):
    await bot.set_state(message.from_user.id, MyStates.address, message.chat.id)
    await bot.send_message(message.chat.id, "Напишите адрес и форму оплаты")


@bot.message_handler(state=MyStates.address)
async def address_get(message):
    query = "UPDATE canteen SET address = %s WHERE user_id = %s;"
    data = (message.text, message.from_user.id)
    cur.execute(query, data)
    conn.commit()
    adr = message.text
    markup = start_menu()
    await bot.send_message(message.chat.id, f"Записал ваш адрес и форму оплаты:\n<b>{adr}</b>\nМожете продолжить "
                                            f"оформление заказа или завершить его",
                           parse_mode="html", reply_markup=markup)
    await bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(commands=["phone"])
async def phone(message):
    await bot.set_state(message.from_user.id, MyStates.phone, message.chat.id)
    await bot.send_message(message.chat.id, "Напишите ваш номер телефона")


@bot.message_handler(state=MyStates.phone)
async def phone_number_get(message):
    raw_phone = str(message.text)
    raw_phone.replace('-', '').replace('.', '').replace(' ', '')
    if raw_phone.startswith("+7"):
        phone_number = raw_phone
    elif raw_phone.startswith('7'):
        phone_number = f"+{raw_phone}"
    elif raw_phone.startswith('8'):
        phone_number = f"+7{raw_phone[1:]}"
    else:
        phone_number = f"+7{raw_phone}"
    query = "UPDATE canteen SET phone_number = %s WHERE user_id = %s;"
    data = (phone_number, message.from_user.id)
    cur.execute(query, data)
    conn.commit()
    markup = start_menu()
    await bot.send_message(message.chat.id, f"Записал ваш номер телефона:\n<b>{phone_number}</b>"
                                            f"\nМожете продолжить оформление заказа или завершить его",
                           parse_mode="html", reply_markup=markup)
    await bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(commands=["group"])
async def group(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Посетить группу", url="https://t.me/joinchat/QHX1AfluPjlkYThi"))
    await bot.send_message(message.chat.id, "Нажмите на кнопку ниже, чтобы перейти в группу",
                           parse_mode="html", reply_markup=markup)


@bot.message_handler(commands=["admin"])
async def admin(message):
    is_admin = message.from_user.id
    if is_admin in admins:
        admin_markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = []
        cur.execute("SELECT user_name FROM canteen WHERE courier_check IS FALSE;")
        users = cur.fetchall()
        for user in users:
            buttons.append(types.InlineKeyboardButton(text=user[0], callback_data=user[0]))
        admin_markup.add(*buttons)
        await bot.send_message(actual_admin, "\U0001F4C4 Список актуальных заказов", parse_mode="html",
                               reply_markup=admin_markup)
    else:
        send_mess = "Вы не админ"
        await bot.send_message(message.chat.id, send_mess, parse_mode="html")


@bot.callback_query_handler(func=lambda call: True)
async def callback_inline(call):
    info = str(call.data)
    data = (info,)
    if info.startswith('+'):
        query = "SELECT user_id FROM canteen WHERE phone_number = %s;"
    else:
        query = "SELECT user_id FROM canteen WHERE user_name = %s;"
    cur.execute(query, data)
    user_id = cur.fetchone()[0]
    set_query = "UPDATE canteen SET courier_check = NULL, order_list = '{}' WHERE user_id = %s;"
    set_data = (user_id,)
    cur.execute(set_query, set_data)
    conn.commit()
    await bot.send_message(user_id, "Ваш заказ передан курьеру", parse_mode="html")


def start_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btn1 = types.KeyboardButton("Салаты")
    btn2 = types.KeyboardButton("Супы")
    btn3 = types.KeyboardButton("Горячее")
    btn4 = types.KeyboardButton("Гарнир")
    btn5 = types.KeyboardButton("Пицца и хачапури из печи")
    btn6 = types.KeyboardButton("Выпечка")
    btn7 = types.KeyboardButton("Десерты")
    btn8 = types.KeyboardButton("Напитки")
    btn9 = types.KeyboardButton("Посмотреть заказ")
    btn10 = types.KeyboardButton("Завершить заказ")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    markup.add(btn9, btn10)
    return markup


def gen_menu(dframe, dish: str):
    indexes = list(~pd.isna(dframe[dish]))
    lst = dframe[dish][indexes]
    msg = "\n".join(lst)
    return msg


def gen_markup(dframe, dish: str):
    indexes = list(~pd.isna(df[dish]))
    lst = dframe[dish][indexes]
    r_width = len(lst) // 2 + len(lst) % 2
    actual_positions = [i for i, j in zip(range(len(lst) + 1), indexes) if j is True]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=r_width)
    markup.add(*[types.KeyboardButton(f"{i + 1}") for i in actual_positions])
    return markup


def gen_order(order_list: dict):
    order = []
    price = 0
    for i, j in order_list.items():
        if j != 0:
            price += int(re.search(r", (\d+?)р.", i).group()[2:-2]) * j
            part_to_remove = re.search(r"\d+. ", i).group()
            order.append(' '.join([i.replace(part_to_remove, ''), f"{str(j)} шт"]))
    text = "\n".join(order) + f"\n\U0001F4B0<b>Итого (без упаковки):</b> {price}р."
    # for i, j in order_list.items():
    #     if j != 0:
    #         price += int(re.search(r', (\d+?)р.', i).group()[2:-2]) * j
    #         part_to_remove = re.search(r'\d+. ', i).group()
    #         order.append([i.replace(part_to_remove, ''), f'{str(j)} шт'])
    # order.append(f'\U0001F4B0<b>Итого (без упаковки):</b> {price}р.')
    # text = f'''<pre>{tabulate(order, tablefmt="plain")}</pre>'''
    return order, text


def make_order():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Добавить в заказ")
    btn2 = types.KeyboardButton("Отмена")
    btn3 = types.KeyboardButton("Вернуться к списку блюд")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup


def number_of_dishes():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(*[types.KeyboardButton(f"{i + 1} шт") for i in range(6)])
    markup.add(types.KeyboardButton("Отмена"))
    return markup


@bot.message_handler(content_types=["text"])
async def mess(message):
    userid = message.chat.id
    get_message_bot = str(message.text.strip())
    if get_message_bot == "Вернуться к списку блюд":
        markup = start_menu()
        final_message = "Хочешь выбрать что-то ещё?"
    elif get_message_bot in df.iloc[:0]:
        query = "UPDATE canteen SET section_stack = %s WHERE user_id = %s;"
        data = (get_message_bot, userid)
        cur.execute(query, data)
        conn.commit()
        markup = gen_markup(df, get_message_bot)
        markup.add(types.KeyboardButton("Вернуться к списку блюд"))
        final_message = gen_menu(df, get_message_bot)
    elif get_message_bot.isnumeric():
        query = "SELECT section_stack FROM canteen WHERE user_id = %s;"
        data = (userid,)
        cur.execute(query, data)
        section = cur.fetchone()[0]
        actual_positions = [i for i, j in zip(range(1, max_dish + 1), list(pd.isna(df[section]))) if j is False]
        if int(get_message_bot) in actual_positions:
            dish = df[section][int(get_message_bot) - 1]
            dish_query = "UPDATE canteen SET dish_stack = %s WHERE user_id = %s;"
            dish_data = (dish, userid)
            cur.execute(dish_query, dish_data)
            conn.commit()
            markup = make_order()
            final_message = f"{dish}\nДобавляем в заказ?"
        else:
            markup = start_menu()
            final_message = "Кажется, такой позиции нет в меню"
    elif get_message_bot == "Добавить в заказ":
        markup = number_of_dishes()
        final_message = "Выберите количество"
    elif get_message_bot == "Отмена":
        query = "SELECT section_stack FROM canteen WHERE user_id = %s;"
        data = (userid,)
        cur.execute(query, data)
        section = cur.fetchone()[0]
        markup = gen_markup(df, section)
        markup.add(types.KeyboardButton("Вернуться к списку блюд"))
        final_message = "Может что-нибудь другое?"
    elif len(get_message_bot) <= 5 and "шт" in get_message_bot:
        number = int(get_message_bot.replace("шт", ''))
        query = "SELECT dish_stack FROM canteen WHERE user_id = %s;"
        data = (userid,)
        cur.execute(query, data)
        dish = cur.fetchone()[0]
        order_query = "UPDATE canteen SET order_list = order_list || jsonb_build_object(%s, %s) WHERE user_id = %s;"
        order_data = (dish, number, userid)
        cur.execute(order_query, order_data)
        conn.commit()
        markup = start_menu()
        final_message = "Отличный выбор \U0001F44D"
    elif get_message_bot == "Посмотреть заказ":
        query = "SELECT order_list, address FROM canteen WHERE user_id = %s;"
        data = (userid,)
        cur.execute(query, data)
        order_list, addr = cur.fetchone()
        markup = start_menu()
        order, text = gen_order(order_list)
        if len(order) != 0 and addr is not None:
            final_message = "\n".join(
                ["\U0001F37D <b>Заказ:</b>", f"{text}", "\U0001F4CD<b>Адрес и форма оплаты:</b>", addr])
        else:
            final_message = "\U000026A0 Проверьте, что вы добавили блюда и указали адрес доставки (/address)"
    elif get_message_bot == "Завершить заказ":
        markup = start_menu()
        username = message.from_user.username
        query = "SELECT phone_number FROM canteen WHERE user_id = %s;"
        data = (userid,)
        cur.execute(query, data)
        phone_number = cur.fetchone()[0]
        if username is None and phone_number is None:
            final_message = "\U000026A0 Укажите, пожалуйста, номер телефона для связи (/phone)"
        else:
            query = "SELECT order_list, address FROM canteen WHERE user_id = %s;"
            data = (userid,)
            cur.execute(query, data)
            order_list, addr = cur.fetchone()
            order, text = gen_order(order_list)
            if len(order) != 0 and addr is not None:
                query = "UPDATE canteen SET courier_check = FALSE, user_name = %s WHERE address = %s;"
                data = (username, addr)
                cur.execute(query, data)
                conn.commit()
                final_message = "\n".join(
                    ["Ваш заказ принят\n", f"\U0001F37D <b>Заказ:</b>", f"{text}",
                     "\U0001F4CD <b>Адрес и форма оплаты:</b>",
                     addr])
                if username is not None:
                    admin_fin_mes = "\n".join(
                        [f"\U0001F37D <b>Заказ от @{username}:</b>", f"{text}",
                         "\U0001F4CD <b>Адрес и форма оплаты:</b>", addr,
                         "Чтобы посмотреть список актуальных заказов, воспользуйтесь командой /admin"])
                else:
                    admin_fin_mes = "\n".join(
                        [f"\U0001F37D <b>Заказ от t.me/{phone_number}:</b>", f"{text}",
                         "\U0001F4CD <b>Адрес и форма оплаты:</b>", addr,
                         "Чтобы посмотреть список актуальных заказов, воспользуйтесь командой /admin"])
                admin_markup = types.InlineKeyboardMarkup(row_width=3)
                cur.execute(f"SELECT user_name, phone_number FROM canteen WHERE user_id = {userid};")
                user = cur.fetchone()
                user_info = list(filter(None, user))[0]
                admin_markup.add(types.InlineKeyboardButton(text=user_info, callback_data=user_info))
                await bot.send_message(actual_admin, admin_fin_mes, parse_mode="html", reply_markup=admin_markup)
            else:
                final_message = "\U000026A0 Проверьте, что вы добавили блюда и указали адрес доставки (/address)"
    else:
        markup = start_menu()
        final_message = "Для совершения заказа пользуйтесь предлагаемыми кнопками и меню \U0001F916"
    await bot.send_message(userid, final_message, parse_mode="html", reply_markup=markup)


@bot.message_handler(content_types=["audio"])
async def audio(message):
    userid = message.chat.id
    markup = start_menu()
    final_message = "\U0001F916 Классный трек"
    await bot.send_message(userid, final_message, parse_mode="html", reply_markup=markup)


@bot.message_handler(content_types=["photo"])
async def photo(message):
    userid = message.chat.id
    markup = start_menu()
    final_message = "\U0001F916 Классное фото"
    await bot.send_message(userid, final_message, parse_mode="html", reply_markup=markup)


@bot.message_handler(content_types=["voice"])
async def voice(message):
    userid = message.chat.id
    markup = start_menu()
    final_message = "\U0001F916 Классный голос"
    await bot.send_message(userid, final_message, parse_mode="html", reply_markup=markup)


@bot.message_handler(content_types=["video"])
async def video(message):
    userid = message.chat.id
    markup = start_menu()
    final_message = "\U0001F916 Классное видео"
    await bot.send_message(userid, final_message, parse_mode="html", reply_markup=markup)


@bot.message_handler(content_types=["document"])
async def document(message):
    userid = message.chat.id
    markup = start_menu()
    final_message = "\U0001F916 Ого, это документ?"
    await bot.send_message(userid, final_message, parse_mode="html", reply_markup=markup)


@bot.message_handler(content_types=["location"])
async def location(message):
    userid = message.chat.id
    markup = start_menu()
    final_message = "\U0001F916 Ого, это геометка?"
    await bot.send_message(userid, final_message, parse_mode="html", reply_markup=markup)


@bot.message_handler(content_types=["contact"])
async def contact(message):
    userid = message.chat.id
    markup = start_menu()
    final_message = "\U0001F916 Чей же это контакт?"
    await bot.send_message(userid, final_message, parse_mode="html", reply_markup=markup)


@bot.message_handler(content_types=["sticker"])
async def sticker(message):
    markup = start_menu()
    final_message = "\U0001F916 Неплохо, я тоже так умею умею"
    sti = open("batman-emblem.webp", 'rb')
    await bot.reply_to(message, final_message, parse_mode="html", reply_markup=markup)
    await bot.send_sticker(message.chat.id, sti)


# @bot.message_handler(
#     commands=["text", "audio", "photo", "voice", "video", "document", "location", "contact", "sticker"])
# async def emergency_content(message):
#     text = "Извините, сейчас бот не работает, обращайтесь напрямую в группу"
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton("Посетить группу", url="https://t.me/joinchat/QHX1AfluPjlkYThi"))
#     await bot.send_message(message.chat.id, text, parse_mode="html", reply_markup=markup)
#
#
# @bot.message_handler(commands=["start", "help", "menu", "address", "phone", "group", "admin"])
# async def emergency_commands(message):
#     text = "Извините, сейчас бот не работает, обращайтесь напрямую в группу"
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton("Посетить группу", url="https://t.me/joinchat/QHX1AfluPjlkYThi"))
#     await bot.send_message(message.chat.id, text, parse_mode="html", reply_markup=markup)


bot.add_custom_filter(asyncio_filters.StateFilter(bot))

asyncio.run(bot.polling())
