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

def encode_to_zero_width(text):
    """
    Encodes text into zero-width characters
    Uses different zero-width characters to represent binary 0 and 1
    """
    # Zero-width characters
    ZERO = '\u200b'  # Zero-width space
    ONE = '\u200c'   # Zero-width non-joiner
    
    binary_representation = ''
    for char in text:
        # Convert each character to its ASCII value and then to 8-bit binary
        binary = format(ord(char), '08b')
        binary_representation += binary
    
    # Convert binary to zero-width characters
    zero_width_text = ''
    for bit in binary_representation:
        if bit == '0':
            zero_width_text += ZERO
        else:
            zero_width_text += ONE
            
    return zero_width_text

def decode_from_zero_width(zero_width_text):
    """
    Decodes zero-width characters back to original text
    """
    # Zero-width characters
    ZERO = '\u200b'  # Zero-width space
    ONE = '\u200c'   # Zero-width non-joiner
    
    # Convert zero-width characters to binary
    binary = ''
    for char in zero_width_text:
        if char == ZERO:
            binary += '0'
        elif char == ONE:
            binary += '1'
    
    # Convert binary to text (8 bits per character)
    text = ''
    for i in range(0, len(binary), 8):
        if i + 8 <= len(binary):
            byte = binary[i:i+8]
            text += chr(int(byte, 2))
    
    return text

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
            
            # Get caption from Instagram
            caption = extract_caption_from_instagram(instagram_url)
            
            # Convert autograph to zero-width characters
            invisible_code = encode_to_zero_width(autograph)
            
            # Combine caption with invisible code
            combined_text = f"{caption}{invisible_code}"
            
            # Store in database
            new_record = Autograph(
                instagram_url=instagram_url,
                encrypted_code=autograph  # Store the original code
            )
            db.session.add(new_record)
            db.session.commit()
            
            return render_template('result.html', 
                                instagram_url=instagram_url, 
                                encrypted_code=autograph,
                                combined_text=combined_text)
        
        return render_template('generate.html')

    @app.route('/api/generate', methods=['POST'])
    def generate_autograph():
        instagram_url = request.form.get('instagram_url')
        
        # Validate URL
        if not instagram_url or not re.match(r'https?://(www\.)?instagram\.com/.+', instagram_url):
            return jsonify({'status': 'error', 'message': 'Invalid Instagram URL'}), 400
        
        try:
            # Check for duplicate URL
            existing_autograph = Autograph.query.filter_by(instagram_url=instagram_url).first()
            if existing_autograph:
                return jsonify({
                    'status': 'duplicate',
                    'message': 'This URL already has an autograph',
                    'autograph_id': existing_autograph.id
                }), 200

            caption = extract_caption_from_instagram(instagram_url)
            if caption == "No caption found":
                caption = ""
            
            # Generate and encode the autograph
            autograph = generate_random_value()
            invisible_code = encode_to_zero_width(autograph)
            
            # Combine caption with invisible code
            combined_text = f"{caption}{invisible_code}"
            
            # Create new autograph
            new_autograph = Autograph(
                instagram_url=instagram_url,
                encrypted_code=autograph
            )
            db.session.add(new_autograph)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'combined_text': combined_text,
                'original_caption': caption,
                'autograph_code': autograph
            })
            
        except Exception as e:
            print(f"Error in generate_autograph: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/verify', methods=['GET', 'POST'])
    def verify_code():
        if request.method == 'POST':
            caption_text = request.form.get('caption_text', '')
            
            # Extract and decode zero-width characters
            zero_width_chars = ''.join(char for char in caption_text if char in ['\u200b', '\u200c'])
            decoded_code = decode_from_zero_width(zero_width_chars)
            
            # Check if the code exists in database
            autograph = Autograph.query.filter_by(encrypted_code=decoded_code).first()
            
            if autograph:
                return render_template('verify_result.html', 
                                    is_authentic=True, 
                                    autograph=autograph,
                                    decoded_code=decoded_code)
            else:
                return render_template('verify_result.html', 
                                    is_authentic=False)
        return render_template('verify.html')

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
