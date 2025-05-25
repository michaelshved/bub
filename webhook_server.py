from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import time

app = Flask(__name__)

BITSTAMP_API_KEY = "your_api_key"
BITSTAMP_API_SECRET = "your_api_secret"
BITSTAMP_CUSTOMER_ID = "your_customer_id"

def bitstamp_headers(payload, endpoint):
    nonce = str(int(time.time() * 1000))
    message = nonce + BITSTAMP_CUSTOMER_ID + BITSTAMP_API_KEY
    signature = hmac.new(
        BITSTAMP_API_SECRET.encode(),
        msg=message.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

    return {
        'X-BITSTAMP-KEY': BITSTAMP_API_KEY,
        'X-BITSTAMP-SIGNATURE': signature,
        'X-BITSTAMP-NONCE': nonce
    }

def place_order(side, amount, symbol):
    url = f"https://www.bitstamp.net/api/v2/{side}/market/{symbol}/"
    data = {
        'amount': amount
    }
    headers = bitstamp_headers(data, url)
    r = requests.post(url, data=data, headers=headers)
    print(f"Order response: {r.text}")
    return r.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    side = data.get("side", "").lower()
    qty = data.get("qty")
    symbol = data.get("symbol", "btcusd")

    if side in ["buy", "sell"]:
        result = place_order(side, qty, symbol)
        return jsonify({"status": "order placed", "result": result})
    else:
        return jsonify({"error": "Invalid side"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
