from flask import Flask
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
from model import db, User, UserSubscribe
from routes import app_route
from helper import send_daily_email
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
mail = Mail(app)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

def send_daily_email():
    with app.app_context():
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
scheduler.add_job(send_daily_email, 'cron', hour=12, minute=0)
# scheduler.add_job(send_daily_email, 'interval', seconds=10)
scheduler.start()


CORS(app) 
    
app.register_blueprint(app_route)

if __name__ == "__main__":
    app.run(debug=True)