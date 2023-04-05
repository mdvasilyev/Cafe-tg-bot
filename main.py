import pandas as pd
import re
import telebot
from telebot import asyncio_filters
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import types

bot = AsyncTeleBot('6049022584:AAEK8QxoT9kN0E1LTYaNhKNz4NjDdTxIdok', state_storage=StateMemoryStorage())

order = []
order_list = {}
section_stack = []
dish_stack = []
adrs = []
user = []

superadmin = [1208161291]
admins = [1208161291, 659350346, 669249622]

df = pd.read_excel('dishes.xlsx')
max_dish = len(df)
test_df = pd.read_csv('Book1.csv')

class MyStates(StatesGroup):
    address = State()


async def setup_bot_commands():
    await bot.delete_my_commands()
    bot_commands = [
        telebot.types.BotCommand("/start", "Начальная страница"),
        telebot.types.BotCommand("/address", "Ввести адрес и оплату"),
        telebot.types.BotCommand("/vk", "Ссылка на группу ВК"),
        telebot.types.BotCommand("/phone", "Номер телефона")
    ]
    await bot.set_my_commands(bot_commands)


@bot.message_handler(commands=['start'])
async def start(message):
    markup = start_menu()
    send_mess = f"Привет, <b>{message.from_user.first_name}</b>!\nЯ бот, который поможет " \
                f"тебе сделать заказ"
    await bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['vk'])
async def vk(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Посетить группу Вк", url="https://ru.wikipedia.org/wiki/%D0%A1%D1%82%D0%BE"
                                                                    "%D0%BB%D0%BE%D0%B2%D0%B0%D1%8F"))
    await bot.send_message(message.chat.id, "Нажмите на кнопку ниже и посетите нашу группу Вк", parse_mode='html',
                           reply_markup=markup)


@bot.message_handler(commands=['phone'])
async def phone(message):
    await bot.send_message(message.chat.id, "Вы можете связаться с нами по телефону: <i>+7(123)456-78-90</i>",
                           parse_mode='html')


@bot.message_handler(commands=['address'])
async def address(message):
    await bot.set_state(message.from_user.id, MyStates.address, message.chat.id)
    await bot.send_message(message.chat.id, 'Напишите адрес и форму оплаты')


@bot.message_handler(state=MyStates.address)
async def address_get(message):
    markup = start_menu()
    adrs.clear()
    adrs.append(str(message.text))
    await bot.send_message(message.chat.id, "Записал ваш адрес и форму оплаты:\n<b>{address}</b>\nМожете продолжить "
                                            "оформление заказа или завершить его".format(address=adrs[0]),
                           parse_mode="html", reply_markup=markup)
    await bot.delete_state(message.from_user.id, message.chat.id)


# @bot.message_handler(commands=['test'])
# async def menu(message):
# 	markup = start_menu()
# 	send_mess = 'test'
# 	ids = [admins[2], message.chat.id]
# 	[await bot.send_message(i, send_mess, parse_mode='html', reply_markup=markup) for i in ids]

@bot.message_handler(commands=['admin'])
async def admin(message):
    is_admin = message.from_user.id
    if is_admin in admins:
        send_mess = 'Вы админ'
    else:
        send_mess = 'Вы не админ'
    await bot.send_message(message.chat.id, send_mess, parse_mode='html')


@bot.message_handler(commands=['add'])
async def add(message):
    send_mess = f'{message.from_user.id}'
    await bot.send_message(message.chat.id, send_mess, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
async def callback_inline(call):
    if call.data == 'order_checkbox':
        await bot.send_message(user[0], "Ваш заказ передан курьеру", parse_mode='html')


def start_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btn1 = types.KeyboardButton('Салаты')
    btn2 = types.KeyboardButton('Супы')
    btn3 = types.KeyboardButton('Горячее')
    btn4 = types.KeyboardButton('Гарнир')
    btn5 = types.KeyboardButton('Пицца и хачапури из печи')
    btn6 = types.KeyboardButton('Выпечка')
    btn7 = types.KeyboardButton('Десерты')
    btn8 = types.KeyboardButton('Напитки')
    btn9 = types.KeyboardButton('Посмотреть заказ')
    btn10 = types.KeyboardButton('Завершить заказ')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    markup.add(btn9, btn10)
    return markup


def gen_menu(dframe, dish: str):
    indexes = list(~pd.isna(dframe[dish]))
    l = dframe[dish][indexes]
    msg = '\n'.join(l)
    return msg


def gen_markup(dframe, dish: str):
    indexes = list(~pd.isna(df[dish]))
    l = dframe[dish][indexes]
    r_width = len(l) // 2 + len(l) % 2
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=r_width)
    markup.add(*[types.KeyboardButton(f'{i + 1}') for i in range(len(l))])
    return markup


def gen_order(order_list: dict):
    order = []
    price = 0
    for i, j in order_list.items():
        if j != 0:
            price += int(re.search(r', (\d+?)р.', i).group()[2:-2]) * j
            part_to_remove = re.search(r'\d+. ', i).group()
            order.append(' '.join([i.replace(part_to_remove, ''), f'{str(j)} шт']))
    text = '\n'.join(order) + f'\n\U0001F4B0<b>Итого (без упаковки):</b> {price}р.'
    return order, text

def make_order():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('Добавить в заказ')
    btn2 = types.KeyboardButton('Отмена')
    btn3 = types.KeyboardButton('Вернуться к списку блюд')
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup


def number_of_dishes():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(*[types.KeyboardButton(f'{i + 1} шт') for i in range(6)])
    markup.add(types.KeyboardButton('Отмена'))
    return markup


@bot.message_handler(content_types=['text'])
async def mess(message):
    user.clear()
    user.append(message.chat.id)
    get_message_bot = message.text.strip()
    if get_message_bot == "Вернуться к списку блюд":
        markup = start_menu()
        final_message = "Хочешь выбрать что-то ещё?"
    elif get_message_bot in df.iloc[:0]:
        section_stack.clear()
        section_stack.append(get_message_bot)
        markup = gen_markup(df, get_message_bot)
        markup.add(types.KeyboardButton("Вернуться к списку блюд"))
        final_message = gen_menu(df, get_message_bot)
    elif len(get_message_bot) <= 2 and int(get_message_bot) in range(1, max_dish + 1):
        dish = df[section_stack[0]][int(get_message_bot) - 1]
        order_list[dish] = 0
        dish_stack.clear()
        dish_stack.append(dish)
        markup = make_order()
        final_message = f"{dish}\nДобавляем в заказ?"
    elif get_message_bot == "Добавить в заказ":
        markup = number_of_dishes()
        final_message = "Выберите количество"
    elif get_message_bot == "Отмена":
        markup = gen_markup(df, section_stack[0])
        markup.add(types.KeyboardButton("Вернуться к списку блюд"))
        final_message = "Может что-нибудь другое?"
    elif "шт" in get_message_bot:
        number = int(get_message_bot.replace('шт', ''))
        order_list[dish_stack[0]] += number
        markup = start_menu()
        final_message = "Отличный выбор \U0001F44D"
    elif get_message_bot == "Посмотреть заказ":
        markup = start_menu()
        order, text = gen_order(order_list=order_list)
        if len(order) != 0 and len(adrs) != 0:
            final_message = '\n'.join(
				["\U0001F37D <b>Заказ:</b>", f"{text}", "\U0001F4CD<b>Адрес и форма оплаты:</b>", adrs[0]])
        else:
            final_message = "\U000026A0 Проверьте, что вы добавили блюда и указали адрес доставки (/address)"
    elif get_message_bot == "Завершить заказ":
        markup = start_menu()
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(types.InlineKeyboardButton("Заказ отдан курьеру", callback_data="order_checkbox"))
        order, text = gen_order(order_list=order_list)
        if len(order) != 0 and len(adrs) != 0:
            final_message = '\n'.join(
                ["\U0001F37D <b>Заказ:</b>", f"{text}", "\U0001F4CD <b>Адрес и форма оплаты:</b>", adrs[0]])
            order_list.clear()
            order.clear()
            await bot.send_message(admins[0], final_message, parse_mode='html', reply_markup=admin_markup)
        else:
            final_message = "\U000026A0 Проверьте, что вы добавили блюда и указали адрес доставки (/address)"
    else:
        markup = start_menu()
        final_message = "Для совершения заказа пользуйтесь предлагаемыми кнопками и меню \U0001F601"
    await bot.send_message(message.chat.id, final_message, parse_mode='html', reply_markup=markup)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

asyncio.run(bot.polling())
