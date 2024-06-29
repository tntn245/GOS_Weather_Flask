from app import main, db

with main.app_context():
    db.drop_all()
    db.create_all()
