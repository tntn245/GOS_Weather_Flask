from flask import Flask, json, render_template, url_for, request, redirect, jsonify
from flask_mail import Mail, Message
import datetime as dt
import requests
import config as cfg
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app. config ['MAIL_SERVER'] = 'smtp.gmail.com'
app. config ['MAIL_PORT'] = 465
app. config ['MAIL_USERNAME'] = '21520385@gm.uit.edu.vn'
app. config ['MAIL_PASSWORD'] = os.environ.get('PASSWORD')
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

@app.route('/sendemail', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        msg = Message("Hey", sender='noreply@demo.com',
        recipients=['tranngoctonhu2405@gmail.com'])
        msg.body = "Hey how are you? Is everything okay?"
        mail.send(msg)
        return "Sent email."
    return render_template('sendemail.html')


if __name__ == "__main__":
    app.run(debug=True)
    