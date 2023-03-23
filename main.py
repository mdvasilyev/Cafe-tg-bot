import pandas as pd
import telebot
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types

bot = AsyncTeleBot('6049022584:AAEK8QxoT9kN0E1LTYaNhKNz4NjDdTxIdok')
n_of_dishes = range(1, 21)
order_list = {}
section_stack = []
dish_stack = []
superadmin = [1208161291]
admins = [1208161291, 659350346, 669249622]

df = pd.read_excel('dishes.xlsx')
max_dish = len(df)
test_df = pd.read_csv('Book1.csv')

@bot.message_handler(commands=['test'])
async def send_text(message):
	l = list(test_df['Name'])
	# mes = ' '.join(l)
	mes = '\n'.join(l)
	# indexes = list(~pd.isna(df['Салаты']))
	# slds = df['Салаты'][indexes]
	# mes = '\n'.join(slds)
	await bot.send_message(message.chat.id, f"{mes}")

async def setup_bot_commands():
	bot_commands = [
		telebot.types.BotCommand("/start", "main menu"),
		telebot.types.BotCommand("/vk", "link to vk"),
		telebot.types.BotCommand("/phone", "call us via phone")
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
	await bot.send_message(message.chat.id, "Нажмите на кнопку ниже и посетите нашу группу Вк", parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['phone'])
async def phone(message):
	await bot.send_message(message.chat.id, "Вы можете связаться с нами по телефону: <i>+7(123)456-78-90</i>", parse_mode='html')

@bot.message_handler(commands=['admin'])
async def phone(message):
	is_admin = message.from_user.id
	if is_admin in admins:
		send_mess = 'Вы админ'
	else:
		send_mess = 'Вы не админ'
	await bot.send_message(message.chat.id, send_mess, parse_mode='html')

@bot.message_handler(commands=['add'])
async def phone(message):
	send_mess = f'{message.from_user.id}'
	await bot.send_message(message.chat.id, send_mess, parse_mode='html')

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
	btn9 = types.KeyboardButton('Ланчбоксы')
	btn10 = types.KeyboardButton('Завершить заказ')
	markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
	markup.add(btn10)
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
	get_message_bot = message.text.strip()
	if get_message_bot == "Вернуться к списку блюд":
		markup = start_menu()
		final_message = "Хочешь выбрать что-то ещё?"
	elif get_message_bot in df.iloc[:0]:
		section_stack.append(get_message_bot)
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = gen_markup(df, get_message_bot)
		markup.add(types.KeyboardButton("Вернуться к списку блюд"))
		final_message = gen_menu(df, get_message_bot)
	elif len(get_message_bot) <= 2 and int(get_message_bot) in range(1, max_dish + 1):
		dish = df[section_stack[0]][int(get_message_bot) - 1]
		order_list[dish] = 0
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
		number = get_message_bot.replace('шт', '')
		order_list[dish_stack[0]] += number
		markup = start_menu()
		final_message = "Отличный выбор"
	elif get_message_bot == "Завершить заказ":
		markup = start_menu()
		text = f"{[[i, order_list[i]] for i in order_list if order_list[i] != 0]}"
		final_message = f"Вы заказали:\n{text}"
	else:
		markup = start_menu()
		final_message = "Я весьма интровертичен и люблю только принимать ваши заказы \U0001F601"
	await bot.send_message(message.chat.id, final_message, parse_mode='html', reply_markup=markup)

asyncio.run(bot.polling())
