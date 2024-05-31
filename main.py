import os
import logging

from stock import get_price

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
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
        await message.answer("неудачно")
        return

    ticker = args[-1]
    price = get_price(api_token, ticker)
    await message.answer(f"Цена акции по тикеру {ticker}: {price}")


@dp.message_handler(commands=["crypto"])
async def cmd_crypto(message: types.Message):
    log.info(f"Received /crypto command with args: {message.text}")
    args = message.text.split()

    if len(args) != 2:
        await message.answer("Пожалуйста, используйте формат команды: /crypto <id_криптовалюты>")
        return

    currency = args[1].lower()

    # Получаем список всех криптовалют и их идентификаторов
    try:
        coins_list = cg.get_coins_list()
        coin_id = None
        for coin in coins_list:
            if coin['symbol'] == currency or coin['id'] == currency:
                coin_id = coin['id']
                break

        if not coin_id:
            await message.answer(f"Не удалось найти криптовалюту с тикером {currency}. Проверьте правильность тикера.")
            return

        result = cg.get_price(ids=coin_id, vs_currencies="usd")
        log.info(f"Received price data for {currency} (ID: {coin_id}): {result}")

        if coin_id in result and 'usd' in result[coin_id]:
            price = result[coin_id]['usd']
            await message.answer(f"Криптовалюта: {currency}\nСтоимость на данный момент: {price}$")
        else:
            await message.answer(f"Не удалось получить данные для {currency}. Проверьте правильность тикера.")
    except Exception as e:
        log.error(f"Ошибка при получении данных: {e}")
        await message.answer("Произошла ошибка при получении данных. Пожалуйста, попробуйте позже.")



if __name__ == '__main__':
    log.info("Starting bot")
    executor.start_polling(dp, skip_updates=True)
