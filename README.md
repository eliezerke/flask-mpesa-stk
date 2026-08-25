# Flask M-Pesa STK Push
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![M-Pesa](https://img.shields.io/badge/M--Pesa-Daraja%20API-green?logo=safaricom&logoColor=white)](https://developer.safaricom.co.ke/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/eliezerke/flask-mpesa-stk?style=social)](https://github.com/eliezerke/flask-mpesa-stk)

A lightweight Flask application that integrates **Safaricom Daraja API** for M-Pesa STK Push (Lipa Na M-Pesa Online) payments. It supports payment initiation, callback handling, real-time status polling, transaction storage in SQLite, and a simple dashboard with analytics.
## Features

- Initiate M-Pesa STK Push requests
- Handle Safaricom payment callbacks
- Store transactions in SQLite with status tracking (`pending` / `success` / `failed`)
- Real-time payment status polling endpoint
- Clean checkout UI with form validation and loading states
- Dashboard with payment history, status breakdown (pie chart), and successful volume by reference (bar chart)
- Environment-based configuration via `.env`

## Project Structure

```
flask-mpesa-stk/
├── app/
│   ├── __init__.py          # Flask app & SQLAlchemy setup
│   ├── config.py            # App configuration
│   ├── payload_stk.py       # Access token + STK Push logic
│   ├── routes.py            # API & page routes
│   └── templates/
│       ├── index.html       # Main checkout page
│       ├── donate.html      # Donation-style UI (demo)
│       └── dash.html        # Transactions dashboard
├── models.py                # Payment SQLAlchemy model
├── push.py                  # Entry point (creates tables + runs app)
└── .gitignore
```

## Prerequisites

- Python 3.8+
- A [Safaricom Developer Portal](https://developer.safaricom.co.ke/) account
- Consumer Key & Consumer Secret
- Lipa Na M-Pesa Online Passkey
- Business Shortcode (sandbox: `174379`)
- A publicly reachable callback URL (use [ngrok](https://ngrok.com/), Cloudflare Tunnel, etc. for local testing)

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/eliezerke/flask-mpesa-stk.git
cd flask-mpesa-stk
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# or
venv\Scripts\activate           # Windows
```

3. **Install dependencies**

```bash
pip install flask flask-sqlalchemy python-dotenv requests
```

4. **Create a `.env` file** in the project root:

```env
URL=https://sandbox.safaricom.co.ke
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_PASSKEY=your_passkey
MPESA_SHORTCODE=174379
TRANSACTION_TYPE=CustomerPayBillOnline
```

> For production, change `URL` to `https://api.safaricom.co.ke` and use your live credentials.

## Running the App

```bash
python push.py
```

The server starts at `http://127.0.0.1:5000` (debug mode enabled).

On first run it automatically creates the SQLite database (`mpesa.db`) and the `payment` table.

## Routes

| Method | Endpoint                          | Description                                      |
|--------|-----------------------------------|--------------------------------------------------|
| GET    | `/`                               | Checkout page (form to initiate STK Push)        |
| POST   | `/`                               | Initiate STK Push (JSON body)                    |
| GET    | `/donate`                         | Donation-style UI demo                           |
| POST   | `/mpesa/callback`                 | Safaricom callback handler                       |
| GET    | `/api/payment-status/<checkout_id>` | Poll payment status by CheckoutRequestID       |
| GET    | `/dashboard`                      | Transactions dashboard with charts               |

### Initiate Payment (POST `/`)

**Request body (JSON):**

```json
{
  "PhoneNumber": "2547XXXXXXXX",
  "Amount": 1,
  "Reference": "Invoice #1234",
  "CallBackURL": "https://your-public-url/mpesa/callback"
}
```

**Successful response** includes `CheckoutRequestID`, which is stored and used for status polling.

### Callback (`/mpesa/callback`)

Safaricom posts the result here. The app updates the corresponding payment record to `success` or `failed`.

### Status Polling

```
GET /api/payment-status/<CheckoutRequestID>
```

Returns:

```json
{
  "status": "success",
  "message": "The service request is processed successfully."
}
```

## Database Model

```python
class Payment(db.Model):
    id                   # Primary key
    checkout_request_id  # Unique CheckoutRequestID from Daraja
    phone_number
    amount
    reference
    mpesa_response       # Full JSON response / callback
    status               # pending | success | failed
```

## Local Testing Tips

1. Expose your local server with a tunnel so Safaricom can reach the callback:

```bash
ngrok http 5000
# Use the HTTPS URL as CallBackURL, e.g. https://xxxx.ngrok.io/mpesa/callback
```

2. Use the sandbox test phone numbers and credentials provided in the Safaricom Developer Portal.
3. Phone numbers **must** be in the format `254XXXXXXXXX` (no leading `0` or `+`).

## Security Notes

- Never commit your `.env` file (already ignored).
- Change the hardcoded `SECRET_KEY` in `app/config.py` for production.
- Use HTTPS in production and restrict callback access if possible.
- Consider adding rate limiting and stronger phone/amount validation for production use.

## License

This project is open source. Feel free to use, modify, and distribute.

---

Built with Flask + Safaricom Daraja API.
```
