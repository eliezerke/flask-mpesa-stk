from dotenv import load_dotenv
from datetime import datetime
import requests
import base64
import os

load_dotenv()

URL = os.getenv("URL")
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
TRANSACTION_TYPE = os.getenv("TRANSACTION_TYPE")

def access_token():
    endpoint_url = f"{URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        endpoint_url, 
        auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET)
    )
    
    response_data = response.json()
    
    if "access_token" in response_data:
        return response_data["access_token"]
    else:
        raise Exception(f"Failed to fetch token. Response: {response_data}")


def stk_push(phone_number: str = None, amount: int = 0, callback_url: str = None):
    access_t = access_token()

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode('ascii')).decode('utf-8')

    data = {
        'BusinessShortCode': MPESA_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': TRANSACTION_TYPE,
        'Amount': amount,
        'PartyA': phone_number,
        'PartyB': MPESA_SHORTCODE,
        'PhoneNumber': phone_number,
        'CallBackURL': callback_url,          
        'AccountReference': "eliezerkenya, co",
        'TransactionDesc': "Online payment - api",
    }

    headers = {
        'Authorization': 'Bearer ' + access_t,
        'Content-type': 'application/json'
    }
    
    res = requests.post(f"{URL}/mpesa/stkpush/v1/processrequest", json=data, headers=headers)
    return res.json()