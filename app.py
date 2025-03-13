import os
import requests
from flask import Flask, request, jsonify, send_from_directory

# Initialize Flask app
app = Flask(__name__, static_folder='frontend')

# Serve frontend files

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# API endpoint to forward messages to Rasa

@app.route('/api/message', methods=['POST'])
def message():
    try:
        # Get data from request
        data = request.json
        user_message = data.get('message', '')
        sender_id = data.get('sender', 'user')

        # Forward message to Rasa server
        rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
        rasa_payload = {
            'message': user_message,
            'sender': sender_id
        }

        # Send request to Rasa
        rasa_response = requests.post(rasa_url, json=rasa_payload)
        rasa_data = rasa_response.json()

        # Return response to client
        return jsonify({
            'success': True,
            'messages': rasa_data
        })
    except Exception as e:
        # Fallback response if Rasa is not available
        print(f"Error communicating with Rasa: {str(e)}")
        return jsonify({
            'success': True,
            'messages': [{
                'recipient_id': 'user',
                'text': "I'm currently in development mode. This message is a fallback response since the Rasa server might not be running. In production, I'll be able to process your request properly."
            }]
        })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"MailoBot server running on http://localhost:{port}")
    print("To use with Rasa, make sure to start the Rasa server with:")
    print("  - rasa run --enable-api --cors \"*\"")
    app.run(debug=True, port=port)
