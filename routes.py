from flask import Blueprint, render_template, request, jsonify, current_app
from flask_mail import Message
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask_jwt_extended import create_access_token
from model import db, User, UserSubscribe
from helper import generate_otp, getCurrWeather, getForecastWeather
from extension import mail

import requests
import os

app_route = Blueprint('app', __name__)

@app_route.route('/')
def index():
    weather_data = request.args.get('weather_data')
    return render_template("index.html", data=weather_data)

@app_route.route('/checkEmail', methods=['POST'])
def checkEmail():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required!'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Email already exists!'}), 400

    otp = generate_otp()
    msg = Message('Your OTP Code', sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    msg.body = f'Your OTP code is {otp}'
    mail.send(msg)

    return jsonify({'message': 'OTP sent to your email!', 'otp': otp})


@app_route.route('/verifyOTP', methods=['POST'])
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

@app_route.route('/login', methods=['POST'])
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

@app_route.route('/submit_form', methods=['POST'])
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
    
@app_route.route('/getID', methods=['POST'])
def getID():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'id': user.id}), 200

@app_route.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    position = data.get('position')
    userID = data.get('userID')

    if not position:
        return jsonify({'message': 'Position is required'}), 400

    # Check user_id & position
    existing_position = UserSubscribe.query.filter_by(user_id=userID, position=position).first()

    if existing_position:
        return jsonify({'message': 'Position already subscribed'}), 200

    new_position = UserSubscribe(user_id=userID, position=position)
    db.session.add(new_position)
    db.session.commit()

    return jsonify({'message': 'Subscription successful', 'userID':userID}), 200

@app_route.route('/loadUserSub', methods=['POST'])
def load_user_subscriptions():
    data = request.get_json()
    userID = data.get('userID')

    if userID is None:
        return jsonify({'error': 'User ID is required'}), 400

    user_subscriptions = UserSubscribe.query.filter_by(user_id=userID).all()
    positions = [sub.position for sub in user_subscriptions]

    return jsonify({'positions': positions}), 200

@app_route.route('/unsubscribe', methods=['POST'])
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
    
@app_route.route('/sendemail', methods=['POST'])
def sendemail():
    data = request.json
    position = data.get('position')
    userID = data.get('userID')

    user = User.query.filter_by(id=userID).first()
    if user:
        weather_data = getCurrWeather(position) 
        forecast_data = getForecastWeather(position)

        if weather_data != "Error" and forecast_data != "Error":
            msg = Message(f"Daily Weather in {position}",
                        sender= os.getenv('MAIL_USERNAME'),
                        recipients=[user.email])
            msg.body = f"Hey how are you? Here's your daily weather update!\nYour subscribed positions: {position}"

            data = {
                'header': 'Current weather',
                'weather_data' : weather_data,
                'forecast_data': forecast_data
            }
            msg.html = render_template("index.html", data=data)

            current_app.extensions['mail'].send(msg)
            return jsonify({'message': 'Send email successful'}), 200

        return jsonify({'message': 'Error fetch weather data'}), 400
    
    return jsonify({'message': 'Error request'}), 400
    
@app_route.route('/google-login', methods=['POST'])
def google_login():
    data = request.get_json()
    credential = data.get('obj')
    email = data.get('email')

    if credential:
        # Check email existed
        user = User.query.filter_by(email=email).first()

        if not user:
            new_user = User(email=email)
            new_user.set_password('')
            db.session.add(new_user)
            db.session.commit()
        
        access_token = create_access_token(identity=user.email)
        return jsonify({'message': 'Login successful', 'access_token': access_token}), 200
    
    return jsonify({"error": "Could not retrieve email"}), 400
    