from flask import Flask, request, jsonify
from .encryption import Encryptor

app = Flask(__name__)
encryptor = Encryptor()

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Encryption Service API",
        "endpoints": {
            "/encrypt": "POST - Encrypt text (JSON body: {'text': 'your text here'})",
            "/decrypt": "POST - Decrypt text (JSON body: {'text': 'encrypted text here'})"
        }
    })

@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    encrypted_text = encryptor.encrypt(data['text'])
    return jsonify({'encrypted_text': encrypted_text})

@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    decrypted_text = encryptor.decrypt(data['text'])
    return jsonify({'decrypted_text': decrypted_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)