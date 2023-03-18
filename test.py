from telebot.async_telebot import AsyncTeleBot
from telebot import types
bot = AsyncTeleBot('6049022584:AAEK8QxoT9kN0E1LTYaNhKNz4NjDdTxIdok')

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

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
async def start(message):
	markup = start_menu()
	send_mess = f"Привет, <b>{message.from_user.first_name} {message.from_user.last_name}</b>!\nЯ бот, который поможет " \
				f"тебе сделать заказ"
	await bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=markup)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)


import asyncio
asyncio.run(bot.polling())