import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pycoingecko import CoinGeckoAPI
from loguru import logger as log

token_for_TgBot = os.getenv("tg_api_token")
api_token = os.getenv("TKS_API_TOKEN")

bot = Bot(token=token_for_TgBot)
dp = Dispatcher(bot=bot)
cg = CoinGeckoAPI()

# Логирование
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    log.info("Received /start command")
    await message.answer("Привет!")


@dp.message_handler(commands=["ticker"])
async def cmd_ticker(message: types.Message):
    log.info(f"Received /ticker command with args: {message.text}")
    args = message.text.split()
    if len(args) != 2:
        await message.answer("илюха, все хуйня, переделывай")
        return

    ticker = args[-1]
    price = get_price(api_token, ticker)
    await message.answer(f"Цена акции по тикеру {ticker}: {price}")


@dp.message_handler(commands=["crypto"])
async def cmd_crypto(message: types.Message):
    log.info(f"Received /crypto command with args: {message.text}")

    # Список популярных криптовалют
    popular_cryptos = ["bitcoin", "ethereum", "ripple", "litecoin", "dogecoin"]

    # Создаем inline клавиатуру с кнопками для выбора криптовалюты
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(crypto.capitalize(), callback_data=f"crypto_{crypto}") for crypto in
               popular_cryptos]
    keyboard.add(*buttons)

    await message.answer("Выберите криптовалюту:", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('crypto_'))
async def process_crypto_callback(callback_query: types.CallbackQuery):
    crypto_id = callback_query.data.split("_")[1]

    try:
        result = cg.get_price(ids=crypto_id, vs_currencies="usd")
        log.info(f"Received price data for {crypto_id}: {result}")

        if crypto_id in result and 'usd' in result[crypto_id]:
            price = result[crypto_id]['usd']
            await bot.send_message(callback_query.from_user.id,
                                   f"Криптовалюта: {crypto_id.capitalize()}\nСтоимость на данный момент: {price}$")
        else:
            await bot.send_message(callback_query.from_user.id,
                                   f"Не удалось получить данные для {crypto_id}. Проверьте правильность тикера.")
    except Exception as e:
        log.error(f"Ошибка при получении данных: {e}")
        await bot.send_message(callback_query.from_user.id,
                               "Произошла ошибка при получении данных. Пожалуйста, попробуйте позже.")


if __name__ == '__main__':
    log.info("Starting bot")
    executor.start_polling(dp, skip_updates=True)
