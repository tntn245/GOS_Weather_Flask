from flask import Flask, render_template, url_for, request, jsonify
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import datetime as dt
import requests
import config as cfg
import os

load_dotenv()

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "tranngoctonhu2405@gmail.com"
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def send_daily_email():
    with app.app_context():
        msg = Message("Daily Weather Update",
                      sender="tranngoctonhu2405@gmail.com",
                      recipients=["tranngoctonhu245@gmail.com"])
        msg.body = "Hey how are you? Here's your daily weather update!"
        mail.send(msg)

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_email, 'cron', hour=7, minute=0)
# scheduler.add_job(send_daily_email, 'interval', seconds=10)
scheduler.start()

@app.route('/')
def index():
    weather_data = request.args.get('weather_data')
    return render_template("index.html", weather_data=weather_data)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    # city = request.form['city']
    # current = 'current.json'
    # forecast = 'forecast.json'

    # url = f"{cfg.BASE_URL}{current}?key={cfg.API_KEY}&q={city}&aqi=no"
    # response = requests.get(url)

    # url = f"{cfg.BASE_URL}{forecast}?key={cfg.API_KEY}&q={city}&days=4&aqi=no&alerts=yes"
    url = "http://api.weatherapi.com/v1/current.json?key=3754d6efcabd4f4892d44831242706&q=London&aqi=no"
    response = requests.get(url)
    
    if response.status_code == 200:
        weather_data = response.json()
    else:
        weather_data = {"error": "Could not retrieve data"}
    
    return render_template("index.html", weather_data=weather_data)

@app.route('/sendemail', methods=['GET', 'POST'])
def sendemail():
    if request.method == 'POST':
        msg = Message("Hey", sender='tranngoctonhu2405@gmail.com',
            recipients=['tranngoctonhu245@gmail.com'])
        msg.body = "Hey how are you? Is everything okay?"
        mail.send(msg)
        return "Success"
    return render_template('sendemail.html')

@app.route('/google-login', methods=['POST'])
def google_login():
    token = request.json.get('token')
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request())
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        email = id_info.get('email')
        return {'email': email}, 200
    except ValueError as e:
        return {'error': 'Invalid token'}, 401

if __name__ == "__main__":
    app.run(debug=True)