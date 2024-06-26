from flask import Flask, json, render_template, url_for, request, redirect, flash
from flask_mail import Mail, Message
# from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import atexit
import datetime as dt
import requests
import config as cfg
import os
from datetime import datetime
import time
import schedule
import threading
import helper

load_dotenv()

app = Flask(__name__)
app. config ['MAIL_SERVER'] = 'smtp.gmail.com'
app. config ['MAIL_PORT'] = 587
app. config ['MAIL_USERNAME'] = 'tranngoctonhu2405@gmail.com'
app. config ['MAIL_PASSWORD'] = 'rkkasigyemmqvmbr'
app.config ['MAIL_USE_TLS'] = False
app.config ['MAIL_USE_SSL'] = True
mail = Mail(app)

def send_periodic_email():
    msg = Message("Hey", sender='tranngoctonhu2405@gmail.com',
            recipients=['tranngoctonhu245@gmail.com'])
    msg.body = "Hey how are you? Is everything okay?"
    mail.send(msg)

def schedule_emails():
    # schedule.every().day.at("09:00").do(send_periodic_email)  # Schedule to run daily at 9 AM
    schedule.every(10).seconds.do(send_periodic_email)
    while True:
        schedule.run_pending()
        time.sleep(1)


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



# @app.route('/sendemail', methods=['GET', 'POST'])
# def sendemail():
#     if request.method == 'POST':
#         msg = Message("Hey", sender='tranngoctonhu2405@gmail.com',
#             recipients=['tranngoctonhu245@gmail.com'])
#         msg.body = "Hey how are you? Is everything okay?"
#         mail.send(msg)
#         return "Success"
#     return render_template('sendemail.html')

# @app.rout('/schedule', methods=['GET', 'POST'])
# def schedule():
#     current_time = datetime.now()
#     schedule.every(5).seconds.do(print(current_time))
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

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
    scheduler_thread = threading.Thread(target=schedule_emails)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    app.run(debug=True)
    