import os
import telebot
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

TOKEN = os.getenv("TOKEN")  # Telegram bot token
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # OpenWeatherMap API key

bot = telebot.TeleBot(TOKEN)  # Create bot instance

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Respond to /start command with a welcome message
    bot.reply_to(message, "Привіт! Я — погодний бот. Напиши /weather <місто>, щоб дізнатися погоду.")

@bot.message_handler(commands=['weather'])
def ask_city(message):
    # Ask user to enter the city name after /weather command
    bot.reply_to(message, "Будь ласка, введи назву міста, щоб дізнатися погоду.")
    bot.register_next_step_handler(message, get_weather)

def get_weather(message):
    city = message.text.strip()  # Get city name from user's message
    weather_info = get_weather_data(city)  # Fetch weather info from API
    bot.send_message(message.chat.id, weather_info)

def get_air_quality(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        aqi = data['list'][0]['main']['aqi']
        aqi_desc = {
            1: "Добра якість повітря 😊",
            2: "Задовільна якість повітря 🙂",
            3: "Помірне забруднення 😐",
            4: "Погана якість повітря 😷",
            5: "Дуже погана якість повітря 🤢"
        }
        return aqi_desc.get(aqi, "Невідома якість повітря")
    else:
        return "Не вдалося отримати дані про якість повітря."

def get_weather_data(city):
    translations = {
        "Clear": "Ясно ☀️",
        "Clouds": "Хмарно ☁️",
        "Rain": "Дощ 🌧️",
        "Drizzle": "Мряка 🌦️",
        "Thunderstorm": "Гроза ⛈️",
        "Snow": "Сніг ❄️",
        "Mist": "Туман 🌫️",
        "Fog": "Туман 🌫️",
        "Haze": "Мряка 🌦️",
        "Sand": "Пісок 🏜️",
        "Tornado": "Торнадо 🌪️"
    }

    # Build weather API URL
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ua"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']  # Current temperature
        main_weather_en = data['weather'][0]['main']  # Weather description
        main_weather_ua = translations.get(main_weather_en, main_weather_en)

        lat = data['coord']['lat']
        lon = data['coord']['lon']
        air_quality = get_air_quality(lat, lon)

        return (f"Погода у місті {city}:\n"
                f"Температура: {temp}°C\n"
                f"Стан: {main_weather_ua}\n"
                f"Якість повітря: {air_quality}")
    else:
        return "Вибач, не можу знайти інформацію про це місто."

bot.polling()
