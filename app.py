import os
from flask import Flask, send_from_directory

# Initialize Flask app
app = Flask(__name__, static_folder='frontend')

# Serve frontend files


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"MailoBot server running on http://localhost:{port}")
    print("To use with Rasa, make sure to start the Rasa server with:")
    print("  - rasa run --enable-api --cors \"*\"")
    app.run(debug=True, port=port)
