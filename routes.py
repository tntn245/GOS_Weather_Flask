from flask import Blueprint, render_template, request, jsonify, current_app
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
from model import db, User, UserSubscribe
from helper import generate_otp

import requests
import os

app = Blueprint('app', __name__)

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
    mail = current_app.config['mail']
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

    # Check email existed
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'message': 'Login successful', 'access_token': access_token}), 200


@app.route('/submit_form', methods=['POST'])
def submit_form():
    data = request.json
    position = data.get('position')
    current = 'current.json'
    forecast = 'forecast.json'

    # Get curr weather
    url = f"{os.getenv('BASE_URL')}{current}?key={os.getenv('API_KEY')}&q={position}&aqi=no"
    response = requests.get(url)
    
    if response.status_code == 200:
        weather_data = response.json()
    else:
        return jsonify({"error": "Could not retrieve current data"}), 400

    # Get forecast weather
    url = f"{os.getenv('BASE_URL')}{forecast}?key={os.getenv('API_KEY')}&q={position}&days=5&aqi=no&alerts=yes"
    response = requests.get(url)
    
    if response.status_code == 200:
        forecast_data = response.json()
    else:
        return jsonify({"error": "Could not retrieve forecast data"}), 400

    # Return result            
    return jsonify({"weather_data": weather_data, "forecast_data": forecast_data})
    

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    position = data.get('position')
    userID = data.get('userID')

    if not position:
        return jsonify({'message': 'Position is required'}), 400

    # Check user_id & position
    existing_position = UserSubscribe.query.filter_by(user_id=userID, position=position).first()

    if existing_position:
        return jsonify({'message': 'Position already subscribed'}), 400

    new_position = UserSubscribe(user_id=userID, position=position)
    db.session.add(new_position)
    db.session.commit()

    return jsonify({'message': 'Subscription successful', 'userID':userID}), 200

@app.route('/loadUserSub', methods=['POST'])
def load_user_subscriptions():
    data = request.get_json()
    userID = data.get('userID')

    if userID is None:
        return jsonify({'error': 'User ID is required'}), 400

    user_subscriptions = UserSubscribe.query.filter_by(user_id=userID).all()
    positions = [sub.position for sub in user_subscriptions]

    return jsonify({'positions': positions}), 200

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.json
    position = data.get('position')
    userID = data.get('userID')

    # Check user_id & position
    if not position or not userID:
        return jsonify({"error": "Missing position or userID"}), 400

    # Delete record in UserSubscribe
    try:
        subscription = UserSubscribe.query.filter_by(user_id=userID, position=position).first()

        if subscription:
            db.session.delete(subscription)
            db.session.commit()
            return jsonify({"message": "Unsubscribed successfully"}), 200
        else:
            return jsonify({"error": "Subscription not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/google-login', methods=['POST'])
def google_login():
    token = request.json.get('token')
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request())
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        email = id_info.get('email')

        # Create JWT
        access_token = create_access_token(identity=email)

        return jsonify(access_token=access_token), 200
    except ValueError as e:
        return jsonify({'error': 'Invalid token'}), 401

