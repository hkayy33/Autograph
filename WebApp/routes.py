from flask import jsonify, request, render_template
from .encryption import Encryptor
from .models import Autograph, db
from dotenv import load_dotenv
import os
import random
import string
import instaloader
import re

# Load environment variables
load_dotenv()
encryption_key = os.getenv('ENCRYPTION_KEY')
encryptor = Encryptor(encryption_key)  # Create an instance of the Encryptor

def generate_random_value(length=10):
    """Generate a random string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def extract_caption_from_instagram(instagram_url):
    """Extract the caption from an Instagram post or reel URL"""
    try:
        # Create an instance of Instaloader
        L = instaloader.Instaloader()
        
        # Extract the shortcode from the URL - handle both posts and reels
        post_match = re.search(r'/p/([^/]+)', instagram_url)
        reel_match = re.search(r'/reel/([^/]+)', instagram_url)
        
        if post_match:
            shortcode = post_match.group(1)
            # Load the post using the shortcode
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            # Return the caption or a default message
            return post.caption or "No caption found"
        elif reel_match:
            shortcode = reel_match.group(1)
            # Load the reel using the shortcode
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            # Return the caption or a default message
            return post.caption or "No caption found"
        else:
            return "Invalid Instagram URL format. Please use a post or reel URL."
    except Exception as e:
        print(f"Error extracting caption: {str(e)}")
        return "Error fetching caption. Make sure the URL is for a public post or reel."

def init_app(app):
    @app.route('/')
    def home():
        # Instead of displaying all autographs, just show a welcome page
        return render_template('index.html')

    @app.route('/generate', methods=['GET', 'POST'])
    def generate_code():
        if request.method == 'POST':
            instagram_url = request.form['instagram_url']
            
            # Generate autograph
            autograph = generate_random_value()  # Generate a random autograph
            
            # Store in database
            new_record = Autograph(
                instagram_url=instagram_url,
                encrypted_code=autograph
            )
            db.session.add(new_record)
            db.session.commit()
            
            return render_template('result.html', instagram_url=instagram_url, encrypted_code=autograph)
        
        return render_template('generate.html')

    @app.route('/api/generate', methods=['POST'])
    def generate_autograph():
        try:
            # Get URL from form data
            instagram_url = request.form['instagram_url']
            
            # Generate autograph
            autograph = generate_random_value()  # Generate a random autograph
            
            # Get the original caption
            original_caption = extract_caption_from_instagram(instagram_url)
            
            # Combine caption and autograph
            combined_text = f"{original_caption} {autograph}"
            
            # Store in database
            new_record = Autograph(
                instagram_url=instagram_url,
                encrypted_code=autograph
            )
            db.session.add(new_record)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "autograph": autograph,
                "original_caption": original_caption,
                "combined_text": combined_text
            })
        
        except KeyError:
            return jsonify({"error": "Instagram URL missing"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

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
