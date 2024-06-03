import os
import requests

from func_bot.stock import get_price
from func_bot.foreign_stocks import get_foreign_stock_data, get_course_of_currency, get_foreign_stock_data_for_info
from func_bot.crypto import get_crypto_price
from func_bot.weaher import get_weather

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import BotCommand

from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.models import User
from app.schemas import UserCreate, EventCreate, Event
from app.database import create_user, create_event, get_events_for_user, get_user
import uvicorn

from loguru import logger as log

api_token = os.getenv("TKS_API_TOKEN")
API_KEY = os.getenv("WEATHER_API_KEY")
WEB_APP_URL = 'http://localhost:8000'
token_for_TgBot = "7219911289:AAG8059khjCBJ8gV1FYV11Q7LU7hZvt3OjM"

bot = Bot(token=token_for_TgBot)
dp = Dispatcher(bot=bot)
app = FastAPI()

templates = Jinja2Templates(directory="templates")
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['register'])
async def start(message: types.Message):
    await message.reply(f"Привет! Пожалуйста, зарегистрируйтесь на сайте {WEB_APP_URL}/register")

@dp.message_handler(commands=['addchat'])
async def add_chat(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    response = requests.post(f"{WEB_APP_URL}/add_chat", json={'chat_id': chat_id, 'user_id': user_id})
    if response.status_code == 200:
        await message.reply("Чат успешно добавлен.")
    else:
        await message.reply("Ошибка при добавлении чата.")


@app.post("/register")
async def register_user(username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    try:
        existing_user = await db.execute(select(User).filter(User.username == username))
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")

        new_user = User(username=username, hashed_password=password)  # Замените на хеширование пароля
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return JSONResponse(status_code=201, content={"message": "User registered successfully"})
    except Exception as e:
        log.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/register", response_class=HTMLResponse)
async def get_register_form(request: Request):
    try:
        return templates.TemplateResponse("register.html", {"request": request})
    except Exception as e:
        log.error(f"Error rendering registration form: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}


@app.post("/create_event", response_model=Event)
async def create_event(event: EventCreate, db: AsyncSession = Depends(get_db)):
    return await create_event(db, event)

@app.get("/events", response_model=list[Event])
async def get_events(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_events_for_user(db, user_id)
# Функция для установки меню команд

@dp.message_handler(commands=['login'])
async def login(message: types.Message):
    args = message.get_args().split()
    if len(args) != 2:
        await message.reply("Используйте команду /login <username> <password>")
        return

    username, password = args
    response = requests.post(f"{WEB_APP_URL}/login", json={'username': username, 'password': password})

    if response.status_code == 200:
        await message.reply("Успешный вход в систему!")
        # Сохраните токен или другие данные для дальнейшего использования.
    else:
        await message.reply("Неверное имя пользователя или пароль.")


@dp.message_handler(commands=['addevent'])
async def add_event(message: types.Message):
    args = message.get_args().split(',')

    if len(args) != 4:
        await message.reply("Используйте команду /addevent <title>,<description>,<start_time>,<end_time>")
        return

    title, description, start_time, end_time = args

    # Дополнительно можно добавить проверку формата времени и другие валидации.

    response = requests.post(f"{WEB_APP_URL}/create_event", json={
        'title': title,
        'description': description,
        'start_time': start_time,
        'end_time': end_time,
        'user_id': message.from_user.id  # Здесь предполагается использование идентификатора пользователя из Telegram.
    })

    if response.status_code == 200:
        await message.reply("Событие успешно добавлено.")
    else:
        await message.reply("Ошибка при добавлении события.")

@app.exception_handler(Exception)
async def unicorn_exception_handler(request, exc):
    log.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
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
    await message.answer(f"Цена {ticker}: {price} rub")

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
    weather_data = get_weather(API_KEY, city_name)
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

    uvicorn.run(app, host="0.0.0.0", port=8000)