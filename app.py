from flask import Flask
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
from model import db, User, UserSubscribe
from routes import app
from helper import send_daily_email
import os

load_dotenv()

main = Flask(__name__)

main.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
main.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
main.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db.init_app(main)

main.config['MAIL_SERVER'] = 'smtp.gmail.com'
main.config['MAIL_PORT'] = 465
main.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
main.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
main.config['MAIL_USE_TLS'] = False
main.config['MAIL_USE_SSL'] = True
mail = Mail(main)

main.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
main.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(main)

def send_daily_email():
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
                mail.send(msg)
                
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_email, 'cron', hour=13, minute=50)
# scheduler.add_job(send_daily_email, 'interval', seconds=10)
scheduler.start()


CORS(main) 
    
main.register_blueprint(app)

if __name__ == "__main__":
    main.run(debug=True)