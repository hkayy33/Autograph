from flask import Flask, request, jsonify, render_template
from .encryption import Encryptor
from .models import db
from dotenv import load_dotenv
import os
import instaloader

# Load environment variables
load_dotenv()  
encryption_key = os.getenv('ENCRYPTION_KEY')  # Get the encryption key from the .env file
encryptor = Encryptor(encryption_key)  # Pass the key to the Encryptor

# Create the Flask application instance
app = Flask(__name__)

# Configure the application
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

with app.app_context():
    db.create_all()  # Create database tables

@app.route('/')
def home():
    return jsonify({"status": "OK"})  # Simple health check route

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

@app.route('/generate', methods=['POST'])
def generate_autograph():
    try:
        # Get URL from form data
        instagram_url = request.form['instagram_url']
        
        # Generate autograph (no raw_code needed)
        autograph = generate_random_value()  # Replace with your autograph generation logic
        
        # Store in database
        new_record = Autograph(
            instagram_url=instagram_url,
            encrypted_code=autograph
        )
        db.session.add(new_record)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "autograph": autograph
        })
    
    except KeyError:
        return jsonify({"error": "Instagram URL missing"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_caption_from_instagram(instagram_url):
    # Create an instance of Instaloader
    L = instaloader.Instaloader()

    # Extract the shortcode from the URL
    shortcode = instagram_url.split('/p/')[1].split('/')[0]

    # Load the post using the shortcode
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    # Return the caption
    return post.caption or "No caption found."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)