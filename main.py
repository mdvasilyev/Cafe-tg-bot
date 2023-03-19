import pandas as pd
import telebot
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types

bot = AsyncTeleBot('6049022584:AAEK8QxoT9kN0E1LTYaNhKNz4NjDdTxIdok')
order_list = {"плов из баранины": 0, "первое блюдо 1": 0}
section_stack = []
dish_stack = []

df = pd.read_excel('dishes.xlsx')

@bot.message_handler(commands=['test'])
async def send_text(message):
	indexes = list(~pd.isna(df['Салаты']))
	slds = df['Салаты'][indexes]
	mes = '\n'.join(slds)
	await bot.send_message(message.chat.id, f"{mes}")

@bot.message_handler(commands=['test2'])
async def send_text(message):
	indexes = list(~pd.isna(df['Горячее']))
	gor = df['Горячее'][indexes]
	mes = '\n'.join(gor)
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
	send_mess = f"Привет, <b>{message.from_user.first_name} {message.from_user.last_name}</b>!\nЯ бот, который поможет " \
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

def salads():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	btn3 = types.KeyboardButton('3')
	btn4 = types.KeyboardButton("Вернуться к списку блюд")
	markup.add(btn1, btn2, btn3)
	markup.add(btn4)
	return markup

def soups():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton("Вернуться к списку блюд")
	markup.add(btn1)
	markup.add(btn2)
	return markup

def main_course():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	btn3 = types.KeyboardButton('3')
	btn4 = types.KeyboardButton('4')
	btn5 = types.KeyboardButton('5')
	btn6 = types.KeyboardButton("6")
	btn7 = types.KeyboardButton("7")
	btn8 = types.KeyboardButton("8")
	btn9 = types.KeyboardButton("Вернуться к списку блюд")
	markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
	markup.add(btn9)
	return markup

def garnish():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	btn3 = types.KeyboardButton('3')
	btn4 = types.KeyboardButton("Вернуться к списку блюд")
	markup.add(btn1, btn2, btn3)
	markup.add(btn4)
	return markup

def pizza():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=6)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	btn3 = types.KeyboardButton('3')
	btn4 = types.KeyboardButton('4')
	btn5 = types.KeyboardButton('5')
	btn6 = types.KeyboardButton('6')
	btn7 = types.KeyboardButton('7')
	btn8 = types.KeyboardButton('8')
	btn9 = types.KeyboardButton('9')
	btn10 = types.KeyboardButton('10')
	btn11 = types.KeyboardButton('11')
	btn12 = types.KeyboardButton('12')
	btn13 = types.KeyboardButton("Вернуться к списку блюд")
	markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12)
	markup.add(btn13)
	return markup

def bakery():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	btn3 = types.KeyboardButton('3')
	btn4 = types.KeyboardButton('4')
	btn5 = types.KeyboardButton('5')
	btn6 = types.KeyboardButton('6')
	btn7 = types.KeyboardButton('7')
	btn8 = types.KeyboardButton("Вернуться к списку блюд")
	markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
	markup.add(btn8)
	return markup

def desserts():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	btn3 = types.KeyboardButton('3')
	btn4 = types.KeyboardButton('4')
	btn5 = types.KeyboardButton("Вернуться к списку блюд")
	markup.add(btn1, btn2, btn3, btn4)
	markup.add(btn5)
	return markup

def drinks():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	btn3 = types.KeyboardButton('3')
	btn4 = types.KeyboardButton("Вернуться к списку блюд")
	markup.add(btn1, btn2, btn3)
	markup.add(btn4)
	return markup

def lunchbox():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	btn3 = types.KeyboardButton('3')
	btn4 = types.KeyboardButton("Вернуться к списку блюд")
	markup.add(btn1, btn2, btn3)
	markup.add(btn4)
	return markup

def make_order():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
	btn1 = types.KeyboardButton('Добавить в заказ')
	btn2 = types.KeyboardButton('Не добавлять в заказ')
	btn3 = types.KeyboardButton('Вернуться ко вторым блюдам')
	btn4 = types.KeyboardButton('Вернуться к списку блюд')
	markup.add(btn1, btn2)
	markup.add(btn3)
	markup.add(btn4)
	return markup

def number_of_dishes():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
	btn1 = types.KeyboardButton('1')
	btn2 = types.KeyboardButton('2')
	btn3 = types.KeyboardButton('Отмена')
	markup.add(btn1, btn2, btn3)
	return markup

@bot.message_handler(content_types=['text'])
async def mess(message):
	get_message_bot = message.text.strip().lower()
	if get_message_bot == "вернуться к списку блюд":
		markup = start_menu()
		final_message = "Хочешь выбрать что-то ещё?"
	elif get_message_bot == "салаты":
		section_stack.append("салаты")
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = salads()
		final_message = "1. Салат «Витаминный», 120г, 65р.\n2. Салат «питерский», 120г, 76р.\n3. Салат цезарь с " \
						"курицей, 167р."
	elif get_message_bot == "супы":
		section_stack.append("супы")
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = soups()
		final_message = "1. Крем-суп из овощей, 300г, 71р."
	elif get_message_bot == "горячее":
		section_stack.append("горячее")
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = main_course()
		final_message = "1. Картопляник с грибами, 1 шт, 109р.\n2. Тефтели, 2 шт, 129р.\n3. Кусочки куриного филе в " \
						"сливочном соусе, 139р.\n4. Плов из курицы, 220г, 156р.\n5. Макароны по флотски, 133р.\n6. " \
						"Шаурма с курицей, 400г, 183р.\n7. Гуляш из говядины, 130г, 192р. " \
						"169р."
	elif get_message_bot == "гарнир":
		section_stack.append("гарнир")
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = garnish()
		final_message = "1. Картофельное пюре, 150г, 65р.\n2. Гречка, 150г, 55р.\n3. Запеченая картошка, 70р."
	elif get_message_bot == "пицца и хачапури из печи":
		section_stack.append("пицца и хачапури из печи")
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = pizza()
		final_message = "1. Пицца «Пепперони», 500г (целая), 430р.\n2. Пицца «Пепперони», 1 кусок, 55р.\n3. Пицца " \
						"«Цыпленок Чеддер», 500г (целая), 440р.\n4. Пицца «Цыпленок Чеддер», 1 кусок, 56р.\n5. Пицца " \
						"«Бекон пармезан», 500г (целая), 450р.\n6. Пицца «Бекон пармезан», 1 кусок, 57р.\n7. Пицца " \
						"«Четыре сыра», 500г (целая), 450р.\n8. Пицца «Четыре сыра», 1 кусок, 57р.\n9. Пицца " \
						"«Супермясная», 500г (целая), 490р.\n10. Пицца «Супермясная», 1 кусок, 62р.\n11. Пицца 50/50 (" \
						"на выбор), 500г (целая), 450р.\n12. Хачапури, 300г, 256р."
	elif get_message_bot == "выпечка":
		section_stack.append("выпечка")
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = bakery()
		final_message = "1. Слойка с ветчиной и сыром, 75р.\n2. Сосиска в тесте, 67р.\n3. Улитка с творогом, 71р.\n4. " \
						"Запеканка, 109р.\n5. Слойка с вишней, 65р.\n6. Штрудель с яблоком, 109р.\n7. Сосиска в " \
						"слоёном тесте с сыром, 82р."
	elif get_message_bot == "десерты":
		section_stack.append("десерты")
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = desserts()
		final_message = "1. Чизкейк, 113р.\n2. Ред вильвет, 137р.\n3. Брауни, 157р.\n4. Сметанник, 137р."
	elif get_message_bot == "напитки":
		section_stack.append("напитки")
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = drinks()
		final_message = "1. Вода 0.5л, 60р.\n2. Компот ягодный литр, 100р.\n3. Липтон 0.5 (персик, лимон и зеленый), 73р."
	elif get_message_bot == "ланчбоксы":
		section_stack.append("ланчбоксы")
		if len(section_stack) != 1:
			section_stack.pop(0)
		markup = lunchbox()
		final_message = "1. Суповой, 14р. (при заказе супа)\n2. Большой, 16р. (при заказе горячих блюд)\n3. Маленький, " \
						"6р. (при заказе блюд и выпечки, которая не может поместиться в пакеты)"
	elif get_message_bot == "1":
		dish_stack.append("плов из баранины")
		if len(dish_stack) != 1:
			dish_stack.pop(0)
		markup = make_order()
		final_message = "Добавляем в заказ?"
	elif get_message_bot == "добавить в заказ":
		markup = number_of_dishes()
		final_message = "Выберите количество"
	elif get_message_bot == "не добавлять в заказ":
		markup = start_menu()
		final_message = "Может что-нибудь другое?"
	elif get_message_bot == "отмена":
		if section_stack[0] == "салаты":
			markup = salads()
		elif section_stack[0] == "супы":
			markup = soups()
		elif section_stack[0] == "горячее":
			markup = main_course()
		elif section_stack[0] == "гарнир":
			markup = garnish()
		elif section_stack[0] == "пицца и хачапури из печи":
			markup = pizza()
		elif section_stack[0] == "выпечка":
			markup = bakery()
		elif section_stack[0] == "десерты":
			markup = desserts()
		elif section_stack[0] == "напитки":
			markup = drinks()
		elif section_stack[0] == "ланчибоксы":
			markup = lunchbox()
		final_message = "Может что-нибудь другое?"
	elif get_message_bot == "1 шт":
		order_list[dish_stack[0]] += 1
		markup = start_menu()
		final_message = "Отличный выбор"
	elif get_message_bot == "2 шт":
		order_list[dish_stack[0]] += 2
		markup = start_menu()
		final_message = "Отличный выбор"
	elif get_message_bot == "завершить заказ":
		markup = start_menu()
		text = f"{[[i.capitalize(), order_list[i]] for i in order_list if order_list[i] != 0]}"
		final_message = f"Вы заказали:\n{text}"
	else:
		markup = start_menu()
		final_message = "Я весьма интровертичен и люблю только принимать ваши заказы \U0001F601"
	await bot.send_message(message.chat.id, final_message, parse_mode='html', reply_markup=markup)

asyncio.run(bot.polling())
