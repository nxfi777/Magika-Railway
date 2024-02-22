from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth  # Import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from magika import Magika
import os

app = Flask(__name__)
auth = HTTPBasicAuth()  # Create an instance of HTTPBasicAuth
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
@auth.login_required  # Protect the route with basic authentication
def identify_bytes():
    content = request.data
    result = magika_instance.identify_bytes(content)
    return jsonify({"ct_label": result.output.ct_label})

@app.route('/health', methods=['GET'])
def health_check():
    # Simple health check endpoint remains unprotected
    return jsonify({"status": "UP"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
