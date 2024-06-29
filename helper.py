from flask import current_app
from flask_mail import Message
from model import User, UserSubscribe
import random
import string
import os

def generate_otp(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def send_daily_email(main):
    with main.app_context():
        users = User.query.all()
        for user in users:
            user_subscriptions = UserSubscribe.query.filter_by(user_id=user.id).all()
            if user_subscriptions:
                positions = ', '.join(sub.position for sub in user_subscriptions)
                msg = Message("Daily Weather Update",
                              sender= os.getenv('MAIL_USERNAME'),
                              recipients=[user.email])
                msg.body = f"Hey how are you? Here's your daily weather update!\nYour subscribed positions: {positions}"
                mail = current_app.config['mail']
                mail.send(msg)

