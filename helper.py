from flask import current_app, render_template
from flask_mail import Message
from model import User, UserSubscribe
from apscheduler.schedulers.background import BackgroundScheduler
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

def send_daily_email():
    with current_app.app_context():
        # users = User.query.all()
        users = User.query.filter_by(id=1).first()
        for user in users:
            user_subscriptions = UserSubscribe.query.filter_by(user_id=user.id).all()
            if user_subscriptions:
                for sub in user_subscriptions:
                    pos = sub.position
                    weather_data = getCurrWeather(pos) 
                    forecast_data = getForecastWeather(pos)

                    if weather_data != "Error" and forecast_data != "Error":
                        msg = Message(f"Daily Weather in {pos}",
                                    sender= os.getenv('MAIL_USERNAME'),
                                    recipients=[user.email])
                        msg.body = f"Hey how are you? Here's your daily weather update!\nYour subscribed positions: {pos}"

                        data = {
                            'header': 'Current weather',
                            'weather_data' : weather_data,
                            'forecast_data': forecast_data
                        }
                        msg.html = render_template("index.html", data=data)

                        current_app.extensions['mail'].send(msg)
