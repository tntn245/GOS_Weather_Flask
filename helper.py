from flask import current_app, render_template
from flask_mail import Message
from model import User, UserSubscribe
import random
import string
import requests
import os

def generate_otp(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def getCurrWeather(position):
    # Get curr weather
    url = f"{os.getenv('BASE_URL')}current.json?key={os.getenv('API_KEY')}&q={position}&aqi=no"
    response = requests.get(url)
    
    if response.status_code == 200:
        weather_data = response.json()
    else:
        return "Error"

    return weather_data

def getForecastWeather(position):
    # Get forecast weather
    url = f"{os.getenv('BASE_URL')}forecast.json?key={os.getenv('API_KEY')}&q={position}&days=5&aqi=no&alerts=yes"
    response = requests.get(url)
    
    if response.status_code == 200:
        forecast_data = response.json()
    else:
        return "Error"

    return forecast_data
