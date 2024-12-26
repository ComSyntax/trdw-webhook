
from flask import Flask, request, jsonify
import ccxt

app = Flask(__name__)

# KuCoin API Keys (замени на свои)
API_KEY = '676b17f32f92840001f327df'
API_SECRET = '59631742'
API_PASSWORD = 'aa6d3098-f441-400a-9c13-c1318558c23c'

# Initialize CCXT KuCoin client
exchange = ccxt.kucoin({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'password': API_PASSWORD,
})

# Active positions tracker
active_positions = []

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        action = data.get('action')
        symbol = data.get('symbol')
        size = data.get('size')
        price = data.get('price')
        leverage = data.get('leverage', None)

        # Check active positions limit
        if len(active_positions) >= 2:
            return jsonify({'error': 'Active positions limit reached'}), 400

        # Set leverage if provided
        if leverage:
            exchange.set_leverage(leverage, symbol)

        # Create order
        if action == 'buy' or action == 'sell':
            order_type = 'limit' if price else 'market'
            order = exchange.create_order(symbol, order_type, action, size, price)
            active_positions.append(order['id'])
            return jsonify({'status': 'success', 'orderId': order['id'], 'leverage': leverage})
        else:
            return jsonify({'error': 'Invalid action'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/close_position', methods=['POST'])
def close_position():
    try:
        data = request.json
        order_id = data.get('orderId')

        # Cancel order
        exchange.cancel_order(order_id)
        active_positions.remove(order_id)
        return jsonify({'status': 'success', 'message': 'Order cancelled'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
