import requests
import os
from loguru import logger as log

API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city_name: str) -> str:
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        return f"{city_name}: {weather_description}, температура: {temperature}°C"
    else:
        return "Не удалось получить данные о погоде. Проверьте название города."
