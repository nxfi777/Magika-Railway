from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from magika import Magika
import os
import requests

app = Flask(__name__)
auth = HTTPBasicAuth()
magika_instance = Magika()

users = {
    os.environ['USER']: generate_password_hash(os.environ['PASS']),
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@app.route('/identify_bytes', methods=['POST'])
@auth.login_required # Basic Auth
def identify_bytes():
    content = request.data
    result = magika_instance.identify_bytes(content)
    return jsonify(result.output)

@app.route('/identify_from_url', methods=['POST'])
@auth.login_required
def identify_from_url():
    data = request.get_json()
    file_url = data.get('url')
    if not file_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Raises a HTTPError if the response status code is 4XX/5XX
        content = response.content
        result = magika_instance.identify_bytes(content)
        return jsonify(result.output)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    # Simple health check endpoint remains unprotected
    return jsonify({"status": "UP"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
