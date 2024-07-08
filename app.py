from config import app
from helper import send_daily_email
from routes import app_route
from apscheduler.schedulers.background import BackgroundScheduler


app.register_blueprint(app_route)
                
scheduler = BackgroundScheduler()
# scheduler.add_job(send_daily_email, 'cron', hour=11, minute=33)
scheduler.add_job(send_daily_email, 'interval', seconds=60*60*12)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)