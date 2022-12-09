import requests
import datetime
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
import random
from bs4 import BeautifulSoup as b
# import keyboards as kb

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

class Weather:

    URL = 'https://www.anekdot.ru/last/good/'

    bot = Bot(token=tg_bot_token)
    dp = Dispatcher(bot)

    @staticmethod
    def parser(url):
        r = requests.get(url)
        soup = b(r.text, 'html.parser')
        anekdots = soup.find_all('div', class_='text')
        clear_anekdots = [i.text for i in anekdots]
        return clear_anekdots

    def __init__(self):
        self.list_of_jokes = random.shuffle(Weather.parser(Weather.URL))

    @dp.message_handler( commands=["start"])
    async def start_command(self, message: types.Message):

        start_buttons = ['Санкт-Петербург', 'Анекдот', 'Москва', 'Саратов', 'Оренбург']
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*start_buttons)
        await message.answer(
            "Привет! \n\nНапиши мне название города и я пришлю сводку погоды! \n\nИли лучше анедотик прислать?",
            reply_markup=keyboard)

    @dp.message_handler(Text(equals=['Анекдот']))
    async def jokes(self, message: types.Message):
        await self.bot.send_message(message.chat.id, self.list_of_jokes[0])
        del self.list_of_jokes[0]

    # @dp.message_handler(Text(equals=['Санкт-Петербург']))
    @dp.message_handler()
    async def get_weather(self, message: types.Message):

        code_to_smile = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }

        try:
            r = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
            )
            data = r.json()

            city = data["name"]
            cur_weather = data["main"]["temp"]

            weather_description = data["weather"][0]["main"]
            if weather_description in code_to_smile:
                wd = code_to_smile[weather_description]
            else:
                wd = "Посмотри в окно, не пойму что там за погода!"

            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind = data["wind"]["speed"]
            sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
            sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
            length_of_the_day = datetime.datetime.fromtimestamp(
                data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
                data["sys"]["sunrise"])

            await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                                f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
                                f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                                f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
                                f"***Хорошего дня!***"
                                )
        except:
            await message.reply("\U00002620 Проверьте название города \U00002620")


if __name__ == '__main__':
    executor.start_polling(Weather.dp)
