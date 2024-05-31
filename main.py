import os
import logging

from stock import get_price
from foreign_stocks import get_foreign_stock_data, get_course_of_currency, get_foreign_stock_data_for_info
from crypto import get_crypto_price
from weaher import get_weather

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import BotCommand


from loguru import logger as log

token_for_TgBot = os.getenv("tg_api_token")
api_token = os.getenv("TKS_API_TOKEN")


bot = Bot(token=token_for_TgBot)
dp = Dispatcher(bot=bot)


# Логирование
logging.basicConfig(level=logging.INFO)

# Функция для установки меню команд
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/ticker", description="Получить цену акции по тикеру"),
        BotCommand(command="/foreign_ticker", description="Получить данные о зарубежных акциях"),
        BotCommand(command="/crypto", description="Получить цену криптовалюты"),
        BotCommand(command="/weather", description="Получить прогноз погоды"),
        BotCommand(command="/info", description="Получить информацию о курсах и погоде")
    ]
    await bot.set_my_commands(commands)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    log.info("Received /start command")
    await message.answer("Привет!")
    await message.answer("Используйте команду /info для получения информации о погоде и курсе валют.")


@dp.message_handler(commands=["ticker"])
async def cmd_ticker(message: types.Message):
    log.info(f"Received /ticker command with args: {message.text}")
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Используйте формат команды: /ticker <тикер акции>")
        return

    ticker = args[-1]
    price = get_price(api_token, ticker)
    await message.answer(f"Цена акции {ticker}: {price} rub")

# Функция для получения данных об акциях через Yahoo Finance API


@dp.message_handler(commands=["foreign_ticker"])
async def foreign_ticker(message: types.Message):
    log.info("Received /foreign command")
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Используйте формат команды: /foreign_ticker <тикер акции>")
        return
    ticker = args[-1]
    latest_data = get_foreign_stock_data(ticker)
    await message.answer(latest_data)


@dp.message_handler(commands=["crypto"])
async def cmd_crypto(message: types.Message):
    log.info(f"Received /crypto command with args: {message.text}")
    args = message.text.split()

    if len(args) != 2:
        await message.answer("Пожалуйста, используйте формат команды: /crypto <id_криптовалюты>")
        return

    currency = args[1].lower()
    price_data = get_crypto_price(currency)
    await message.answer(price_data)

@dp.message_handler(commands=["weather"])
async def cmd_weather(message: types.Message):
    log.info(f"Received /weather command with args: {message.text}")
    args = message.text.split()

    if len(args) != 2:
        await message.answer("Пожалуйста, используйте формат команды: /weather <город>")
        return

    city_name = args[1]
    weather_data = get_weather(city_name)
    await message.answer(weather_data)

# Новая команда /info
@dp.message_handler(commands=["info"])
async def cmd_info(message: types.Message):
    await message.answer("подождать пару сек")
    log.info(f"Received /info command")

    # Получаем данные о криптовалютах
    btc_price = get_crypto_price("bitcoin")
    eth_price = get_crypto_price("ethereum")
    Tether_price = get_crypto_price("usdt")
    Toncoin_price = get_crypto_price("ton")

    # Получаем данные о курсах валют (пример с USD и EUR)
    usd_price = get_course_of_currency("RUB=X")
    eur_price = get_course_of_currency("EURRUB=X")

    # Получаем данные о курсе акции
    AAPL_price = get_foreign_stock_data_for_info("AAPL")
    NVDA_price = get_foreign_stock_data_for_info("NVDA")

    lkoh_price = get_price(api_token, "LKOH")
    sber_price = get_price(api_token, "SBER")

    # Получаем данные о погоде в нескольких городах
    Tver_weather = get_weather("Tver")
    Saint_Petersburg_weather = get_weather("Saint Petersburg")
    Mexico_City_weather = get_weather("Mexico City")

    # Формируем ответное сообщение
    response_message = (
        f"🤑 Курс BTC: {btc_price}\n"
        f"🤑 Курс ETH: {eth_price}\n"
        f"🤑 Курс USDT: {Tether_price}\n"
        f"🤑 Курс TON: {Toncoin_price}\n\n"
        f"💸 Курс USD: {usd_price}\n"
        f"💸 Курс EUR: {eur_price}\n\n"
        f"📈 Курс акций AAPL: {AAPL_price}\n"
        f"📈 Курс акций NVDA: {NVDA_price}\n"
        f"📈 Курс акций LKOH: {lkoh_price}\n"
        f"📈 Курс акций SBER: {sber_price}\n\n"
        f"🌡 Погода в Tver: {Tver_weather}\n"
        f"🌡 Погода в Saint Petersburg: {Saint_Petersburg_weather}\n"
        f"🌡 Погода в Mexico City: {Mexico_City_weather}"
    )

    await message.answer(response_message)
if __name__ == '__main__':
    log.info("Starting bot")

    async def on_startup(dp):
        await set_commands(bot)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)