import json
from app import app, db, render_template, request, jsonify
from app.payload_stk import stk_push
from models import Payment
from sqlalchemy import func

@app.route("/donate")
def donate():
    return render_template("donate.html")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        payload = request.get_json()

        resp = stk_push(
            phone_number=payload['PhoneNumber'], 
            amount=payload['Amount'], 
            callback_url=payload['CallBackURL']
        )

        if resp and "CheckoutRequestID" in resp:
            try:
                new_payment = Payment(
                    checkout_request_id=resp['CheckoutRequestID'],
                    phone_number=payload['PhoneNumber'], 
                    amount=payload['Amount'], 
                    reference=payload['Reference'], 
                    mpesa_response=json.dumps(resp)
                )
                db.session.add(new_payment)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Database error while saving payment record: {e}")
        return jsonify(resp)
    return render_template("index.html")

@app.route("/mpesa/callback", methods=["POST"])
def callback():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"ResultCode": 1, "ResultDesc": "Invalid JSON"}), 400

        body = data.get("Body", {})
        callback_data = body.get("stkCallback", {})
        checkout_req_id = callback_data.get("CheckoutRequestID")
        res_code = callback_data.get("ResultCode")

        if not checkout_req_id:
            return jsonify({"ResultCode": 1, "ResultDesc": "Missing CheckoutRequestID"}), 400

        try:
            payment = Payment.query.filter_by(checkout_request_id=checkout_req_id).first_or_404()
            
            payment.mpesa_response = json.dumps(data)

            if res_code == 0:
                payment.status = "success"
            else:
                payment.status = "failed"
            
            db.session.commit()

        except Exception as db_error:
            db.session.rollback()
            print(f"Database error: {db_error}")
            return jsonify({"ResultCode": 1, "ResultDesc": "Internal Database Error"}), 500

    except Exception as e:
        print(f"Request structural error: {e}")
        return jsonify({"ResultCode": 1, "ResultDesc": "Invalid Request Format"}), 400

    return jsonify({"ResultCode": 0, "ResultDesc": "Success"}), 200

@app.route("/api/payment-status/<checkout_id>", methods=["GET"])
def check_payment_status(checkout_id):
    payment = Payment.query.filter_by(checkout_request_id=checkout_id).first()
    if not payment:
        return jsonify({"status": "not_found"}), 404
    saf_message = "Awaiting user interaction..."
    
    if payment.mpesa_response and payment.status != 'pending':
        try:
            raw_json = json.loads(payment.mpesa_response)
            saf_message = raw_json.get("Body", {}).get("stkCallback", {}).get("ResultDesc", "No description provided")
        except Exception:
            saf_message = "Failed to parse transaction message details."

    return jsonify({
        "status": payment.status,
        "message": saf_message
    }), 200

@app.route("/dashboard", methods=["GET"])
def dashboard():
    all_payments = Payment.query.order_by(Payment.id.desc()).all()

    status_counts = db.session.query(
        Payment.status, func.count(Payment.id)
    ).group_by(Payment.status).all()

    status_map = {"success": 0, "failed": 0, "pending": 0}
    for status, count in status_counts:
        if status in status_map:
            status_map[status] = count

    reference_volumes = db.session.query(
        Payment.reference, func.sum(Payment.amount)
    ).filter(Payment.status == 'success').group_by(Payment.reference).limit(6).all()

    bar_labels = [row[0] for row in reference_volumes]
    bar_data = [float(row[1]) for row in reference_volumes]

    return render_template(
        "dash.html",
        payments=all_payments,
        pie_labels=list(status_map.keys()),
        pie_data=list(status_map.values()),
        bar_labels=bar_labels,
        bar_data=bar_data
    )