from flask import Flask, json, render_template, url_for, request, redirect, jsonify
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import datetime as dt
import requests
import config as cfg
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app. config ['MAIL_SERVER'] = 'smtp.gmail.com'
app. config ['MAIL_PORT'] = 587
app. config ['MAIL_USERNAME'] = 'tranngoctonhu2405@gmail.com'
app. config ['MAIL_PASSWORD'] = 'rkkasigyemmqvmbr'
app.config ['MAIL_USE_TLS'] = False
app.config ['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/')
def index():
    weather_data = request.args.get('weather_data')
    return render_template("index.html", weather_data=weather_data)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    city = request.form['city']
    endpoint = 'forecast.json'
    
    url = f"{cfg.BASE_URL}{endpoint}?key={cfg.API_KEY}&q={city}&days=4&aqi=no&alerts=yes"
    response = requests.get(url)
    
    if response.status_code == 200:
        weather_data = response.json()
    else:
        weather_data = {"error": "Could not retrieve data"}
    
    return render_template("index.html", weather_data=weather_data)

# def send_daily_email():
#     with app.app_context():
#         msg = Message(
#             "Daily Email",
#             sender=cfg.EMAIL_USER,
#             recipients=["recipient@example.com"]
#         )
#         msg.body = "This is your daily email!"
#         mail.send(msg)

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=send_daily_email, trigger="interval", days=1)
# scheduler.start()

# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())

@app.route('/sendemail', methods=['GET', 'POST'])
def sendemail():
    if request.method == 'POST':
        msg = Message("Hey", sender='tranngoctonhu2405@gmail.com',
            recipients=['tranngoctonhu245@gmail.com'])
        msg.body = "Hey how are you? Is everything okay?"
        mail.send(msg)
        return "Success"
    return render_template('sendemail.html')


if __name__ == "__main__":
    app.run(debug=True)
    