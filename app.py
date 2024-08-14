from flask import Flask, request, jsonify, stream_with_context, Response
from flask_httpauth import HTTPTokenAuth
from magika import Magika
import os
import requests

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

TOKEN = os.environ.get('AUTH_TOKEN', 'default-token')

@auth.verify_token
def verify_token(token):
    if token == TOKEN:
        return True
    return None

def get_magika_instance():
    if not hasattr(get_magika_instance, 'instance'):
        get_magika_instance.instance = Magika()
    return get_magika_instance.instance

session = requests.Session()

@app.route('/identify_bytes', methods=['POST'])
@auth.login_required
def identify_bytes():
    content = request.data
    magika_instance = get_magika_instance()
    result = magika_instance.identify_bytes(content)
    return jsonify(result.output)

@app.route('/identify_from_url', methods=['POST'])
@auth.login_required
def identify_from_url():
    data = request.get_json()
    file_url = data.get('url')
    if not file_url:
        return jsonify({"error": "URL is required"}), 400

    def generate():
        try:
            with session.get(file_url, stream=True) as response:
                response.raise_for_status()
                content = b''
                for chunk in response.iter_content(chunk_size=8192):
                    content += chunk
                magika_instance = get_magika_instance()
                result = magika_instance.identify_bytes(content)
                yield jsonify(result.output).get_data(as_text=True)
        except requests.RequestException as e:
            yield jsonify({"error": str(e)}).get_data(as_text=True)

    return Response(stream_with_context(generate()), content_type='application/json')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP"})

if __name__ == '__main__':
    app.run(debug=False, host='::', port=5000)
