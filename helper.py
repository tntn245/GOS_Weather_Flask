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

def send_daily_email(main):
    with main.app_context():
        users = User.query.all()
        for user in users:
            user_subscriptions = UserSubscribe.query.filter_by(user_id=user.id).all()
            if user_subscriptions:
                positions = ', '.join(sub.position for sub in user_subscriptions)
                msg = Message(f"Daily Weather in {positions}",
                              sender= os.getenv('MAIL_USERNAME'),
                              recipients=[user.email])
                msg.body = f"Hey how are you? Here's your daily weather update!\nYour subscribed positions: {positions}"

                data = {
                    'header': 'Current weather',
                    'weather_data' : getCurrWeather(positions),
                    'forecast_data': getForecastWeather(positions)
                }
                msg.html = render_template("index.html", data=data)

                mail = current_app.config['mail']
                mail.send(msg)

