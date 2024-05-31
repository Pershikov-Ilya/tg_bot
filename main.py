import os
import logging

from stock import get_price
from foreign_stocks import get_foreign_stock_data
from crypto import get_crypto_price

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
        BotCommand(command="/crypto", description="Получить цену криптовалюты")
    ]
    await bot.set_my_commands(commands)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    log.info("Received /start command")
    await message.answer("Привет!")


@dp.message_handler(commands=["ticker"])
async def cmd_ticker(message: types.Message):
    log.info(f"Received /ticker command with args: {message.text}")
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Используйте формат команды: /ticker <тикер акции>")
        return

    ticker = args[-1]
    price = get_price(api_token, ticker)
    await message.answer(f"Цена акции по тикеру {ticker}: {price}")

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


if __name__ == '__main__':
    log.info("Starting bot")

    # Устанавливаем команды при запуске бота
    async def on_startup(dp):
        await set_commands(bot)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)