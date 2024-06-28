from flask import Flask, render_template, url_for, request, jsonify, session
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps

import requests
import config as cfg
import os
import random
import string
import bcrypt

load_dotenv()

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/GOS/GOS_Flask/instance/database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '123456789'
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "tranngoctonhu2405@gmail.com"
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config['JWT_SECRET_KEY'] = '26432b2e093f44a8afb67de48f77fe6b'  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
jwt = JWTManager(app)

CORS(app) 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary, nullable=False)  # Sử dụng LargeBinary để lưu trữ hash mật khẩu

    def __repr__(self):
        return '<User %r>' % self.email

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
    
class UserSubscribe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    position = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<UserSubscribe user_id={self.user_id} position={self.position}>'
    





# def send_daily_email():
#     with app.app_context():
#         msg = Message("Daily Weather Update",
#                       sender="tranngoctonhu2405@gmail.com",
#                       recipients=["tranngoctonhu245@gmail.com"])
#         msg.body = "Hey how are you? Here's your daily weather update!"
#         mail.send(msg)

def send_daily_email():
    with app.app_context():
        users = User.query.all()
        for user in users:
            user_subscriptions = UserSubscribe.query.filter_by(user_id=user.id).all()
            if user_subscriptions:
                positions = ', '.join(sub.position for sub in user_subscriptions)
                msg = Message("Daily Weather Update",
                              sender="tranngoctonhu2405@gmail.com",
                              recipients=[user.email])
                msg.body = f"Hey how are you? Here's your daily weather update!\nYour subscribed positions: {positions}"
                mail.send(msg)

scheduler = BackgroundScheduler()
# scheduler.add_job(send_daily_email, 'cron', hour=7, minute=0)
scheduler.add_job(send_daily_email, 'interval', seconds=60)
scheduler.start()

def generate_otp(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/')
def index():
    weather_data = request.args.get('weather_data')
    return render_template("index.html", weather_data=weather_data)

@app.route('/checkEmail', methods=['POST'])
def checkEmail():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required!'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Email already exists!'}), 400

    otp = generate_otp()
    msg = Message('Your OTP Code', sender='tranngoctonhu2405@gmail.com', recipients=[email])
    msg.body = f'Your OTP code is {otp}'
    mail.send(msg)

    return jsonify({'message': 'OTP sent to your email!', 'otp': otp})


@app.route('/verifyOTP', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    OTPSent = data.get('OTPSent')
    OTPInput = data.get('OTPInput')

    if(OTPInput==OTPSent):
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Verify successfully!'})
    
    return jsonify({'message': 'Verify failed!'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Tìm kiếm và kiểm tra trong cơ sở dữ liệu
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'message': 'Login successful', 'access_token': access_token}), 200


@app.route('/submit_form', methods=['POST'])
def submit_form():
    data = request.json
    city = data.get('city')
    current = 'current.json'
    forecast = 'forecast.json'

    url = f"{cfg.BASE_URL}{current}?key={cfg.API_KEY}&q={city}&aqi=no"
    response = requests.get(url)
    
    if response.status_code == 200:
        weather_data = response.json()
    else:
        weather_data = {"error": "Could not retrieve data"}

    url = f"{cfg.BASE_URL}{forecast}?key={cfg.API_KEY}&q={city}&days=5&aqi=no&alerts=yes"
    response = requests.get(url)
    
    if response.status_code == 200:
        forecast_data = response.json()
    else:
        forecast_data = {"error": "Could not retrieve data"}
        
    return jsonify({"weather_data": weather_data, "forecast_data": forecast_data})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    position = data.get('position')
    userID = data.get('userID')

    if not position:
        return jsonify({'message': 'Position is required'}), 400

    # Kiểm tra tồn tại user_id và position
    existing_position = UserSubscribe.query.filter_by(user_id=userID, position=position).first()

    if existing_position:
        return jsonify({'message': 'Position already subscribed'}), 400

    new_position = UserSubscribe(user_id=userID, position=position)
    db.session.add(new_position)
    db.session.commit()

    return jsonify({'message': 'Subscription successful', 'userID':userID}), 200

@app.route('/google-login', methods=['POST'])
def google_login():
    token = request.json.get('token')
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request())
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        email = id_info.get('email')

        # Tạo JWT
        access_token = create_access_token(identity=email)

        return jsonify(access_token=access_token), 200
    except ValueError as e:
        return jsonify({'error': 'Invalid token'}), 401
if __name__ == "__main__":
    app.run(debug=True)