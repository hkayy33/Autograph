from flask import Flask, request, jsonify, render_template
from .encryption import Encryptor
from WebApp.models import db
from WebApp import create_app
from dotenv import load_dotenv
import os

app = create_app()
load_dotenv()  # Load environment variables
encryption_key = os.getenv('ENCRYPTION_KEY')  # Get the encryption key from the .env file
encryptor = Encryptor(encryption_key)  # Pass the key to the Encryptor

with app.app_context():
    db.create_all()

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

@app.route('/generate', methods=['GET', 'POST'])
def generate_code():
    if request.method == 'POST':
        instagram_url = request.form['instagram_url']
        raw_code = request.form['raw_code']
        
        # Encrypt the raw code
        encrypted_code = encryptor.encrypt(raw_code)
        
        return render_template('result.html', instagram_url=instagram_url, encrypted_code=encrypted_code, raw_code=raw_code)
    
    return render_template('generate.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)