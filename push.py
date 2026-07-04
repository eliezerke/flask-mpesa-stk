from app import app
from models import *
from app import routes

with app.app_context():
    db.create_all()

if __name__== '__main__':
    app.run(debug=True)