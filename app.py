from flask import Flask, render_template
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
from model import db, User, UserSubscribe
from routes import app_route
from flask import Blueprint, render_template, request, jsonify, current_app
from helper import getCurrWeather, getForecastWeather,  generate_otp
from extension import mail
import os

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db.init_app(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail.init_app(app)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

def send_daily_email():
    with app.app_context():
        users = User.query.all()
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

                        mail.send(msg)
                
scheduler = BackgroundScheduler()
# scheduler.add_job(send_daily_email, 'cron', hour=11, minute=33)
scheduler.add_job(send_daily_email, 'interval', seconds=60*60*12)
scheduler.start()


CORS(app) 

app.register_blueprint(app_route)

if __name__ == "__main__":
    app.run(debug=True)