from app import db, datetime

# Mpesa stkpush response database-table storage
class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    
    checkout_request_id = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(100), nullable=False)
    mpesa_response = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
