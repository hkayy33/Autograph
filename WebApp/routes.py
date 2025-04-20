from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from WebApp.encryption import Encryptor
from WebApp.models import db, Autograph, InviteCode
from flask_login import login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
import os
import random
import string
import instaloader
import re
from .validation import validate_instagram_url, validate_caption

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

def extract_post_id(url):
    """Extract the post/reel ID from an Instagram URL"""
    match = re.search(r'/(p|reel)/([^/?]+)', url)
    return match.group(2) if match else None

def init_app(app):
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        next_page = request.args.get('next')
        
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin'))
            return redirect(next_page or url_for('generate_code'))

        if request.method == 'POST':
            instagram_handle = request.form.get('instagram_handle', '').strip()
            code = request.form.get('code', '').strip()

            if not instagram_handle or not code:
                flash('Please enter both Instagram handle and invite code.', 'error')
                return render_template('login.html')

            user = InviteCode.authenticate(instagram_handle, code)
            if user:
                login_user(user, remember=True)
                flash('Login successful!', 'success')
                if user.is_admin:
                    return redirect(url_for('admin'))
                return redirect(next_page or url_for('generate_code'))
            else:
                flash('Invalid credentials or code already used.', 'error')
                return render_template('login.html')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

    @app.route('/admin')
    @login_required
    def admin():
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('generate_code'))
        return render_template('admin.html')

    @app.route('/verify', methods=['GET', 'POST'])
    def verify_code():
        if request.method == 'POST':
            instagram_url = request.form.get('instagram_url')
            caption = request.form.get('caption')
            
            if not instagram_url and not caption:
                return render_template('verify.html', error="Please provide either an Instagram URL or caption")
            
            try:
                if instagram_url:
                    # Extract caption from Instagram URL
                    caption = extract_caption_from_instagram(instagram_url)
                    if not caption:
                        return render_template('verify.html', error="Could not extract caption from URL")
                
                print(f"DEBUG: Verifying caption: {caption}")
                
                # Extract zero-width characters from caption
                zero_width_chars = ''.join(char for char in caption if char in ['\u200b', '\u200c'])
                if not zero_width_chars:
                    print("DEBUG: No hidden code found in caption")
                    return render_template('verify.html', error="No hidden code found in the caption")
                
                print(f"DEBUG: Found zero-width characters")
                
                # Decode the zero-width characters to get the original random code
                decoded_code = decode_from_zero_width(zero_width_chars)
                print(f"DEBUG: Decoded code from caption: {decoded_code}")
                
                # Split the decoded code into chunks of 10 characters (our random code length)
                code_chunks = [decoded_code[i:i+10] for i in range(0, len(decoded_code), 10)]
                print(f"DEBUG: Code chunks found: {code_chunks}")
                
                # Extract post ID from the provided URL
                input_post_id = extract_post_id(instagram_url)
                print(f"DEBUG: Post ID from URL: {input_post_id}")
                
                if not input_post_id:
                    return render_template('verify.html', error="Invalid Instagram URL format")
                
                # Find all autographs
                autographs = Autograph.query.all()
                
                # Find matching autograph by comparing post IDs
                found_valid_code = False
                matching_url = None
                
                for autograph in autographs:
                    stored_post_id = extract_post_id(autograph.instagram_url)
                    print(f"DEBUG: Comparing post IDs - Input: {input_post_id}, Stored: {stored_post_id}")
                    
                    # Check if the code matches
                    if autograph.encryption_code in code_chunks:
                        print("DEBUG: Found matching code!")
                        found_valid_code = True
                        matching_url = autograph.instagram_url
                        
                        # If post IDs match, this is a valid verification
                        if stored_post_id == input_post_id:
                            print("DEBUG: Post IDs match!")
                            return render_template('verify.html', 
                                                success=True,
                                                autograph=autograph,
                                                instagram_url=instagram_url)
                
                if found_valid_code:
                    # We found a valid code but in the wrong post
                    return render_template('verify.html', 
                                        error=f"SUSPICIOUS: A valid autograph was found, but it belongs to a different post. Original post: {matching_url}",
                                        is_suspicious=True)
                
                print("DEBUG: Verification failed")
                return render_template('verify.html', 
                                    error="The autograph could not be verified. Please ensure you are using the correct Instagram post URL.")
                
            except Exception as e:
                print(f"Error in verify_code: {str(e)}")
                return render_template('verify.html', error="An error occurred during verification")
        
        return render_template('verify.html')

    @app.route('/authenticate', methods=['GET', 'POST'])
    def authenticate():
        if request.method == 'POST':
            # Check which verification method is being used
            instagram_url = request.form.get('instagram_url', '')
            caption_text = request.form.get('caption_text', '')
            
            # If Instagram URL is provided, fetch the caption
            if instagram_url:
                try:
                    caption_text = extract_caption_from_instagram(instagram_url)
                    if caption_text == "No caption found" or caption_text.startswith("Error fetching"):
                        flash("Unable to extract caption from the provided URL", "danger")
                        return render_template('authenticate.html')
                except Exception as e:
                    flash(f"Error fetching caption: {str(e)}", "danger")
                    return render_template('authenticate.html')
            
            # Extract and decode zero-width characters
            zero_width_chars = ''.join(char for char in caption_text if char in ['\u200b', '\u200c'])
            
            if not zero_width_chars:
                return render_template('authenticate_result.html', 
                                    is_authentic=False, 
                                    reason="No authentication code found in the content")
            
            try:
                decoded_code = decode_from_zero_width(zero_width_chars)
                
                # Check if the code exists in database
                autograph = Autograph.query.filter_by(encryption_code=decoded_code).first()
                
                if autograph:
                    return render_template('authenticate_result.html', 
                                        is_authentic=True, 
                                        autograph=autograph,
                                        decoded_code=decoded_code,
                                        instagram_url=autograph.instagram_url)
                else:
                    return render_template('authenticate_result.html', 
                                        is_authentic=False,
                                        reason="Authentication code not found in our records",
                                        decoded_code=decoded_code)
            except Exception as e:
                flash(f"Error decoding authentication code: {str(e)}", "danger")
                return render_template('authenticate_result.html', 
                                    is_authentic=False,
                                    reason=f"Error decoding: {str(e)}")
                
        return render_template('authenticate.html')

    @app.route('/generate', methods=['GET', 'POST'])
    @login_required
    def generate_code():
        if request.method == 'POST':
            instagram_url = request.form.get('instagram_url', '').strip()
            caption = request.form.get('caption', '').strip()

            # Validate Instagram URL
            url_valid, url_message = validate_instagram_url(instagram_url)
            if not url_valid:
                flash(url_message, 'error')
                return render_template('generate.html')

            # Validate and sanitize caption
            caption_valid, caption_result = validate_caption(caption)
            if not caption_valid:
                flash(caption_result, 'error')
                return render_template('generate.html')

            try:
                # Use the sanitized caption
                encrypted_caption = encryptor.encrypt(caption_result)
                autograph = Autograph(instagram_url=instagram_url, encryption_code=encrypted_caption)
                db.session.add(autograph)
                db.session.commit()
                flash('Autograph generated successfully!', 'success')
                return redirect(url_for('view_code', id=autograph.id))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while generating the autograph.', 'error')
                return render_template('generate.html')

        return render_template('generate.html')

    @app.route('/api/generate', methods=['POST'])
    def generate_autograph():
        try:
            print("DEBUG: Starting generate_autograph")
            if not request.is_json:
                print("DEBUG: Request is not JSON")
                return jsonify({
                    'error': 'Invalid request format',
                    'message': 'Please send the request with Content-Type: application/json'
                }), 415
            
            data = request.get_json()
            instagram_url = data.get('instagram_url')
            print(f"DEBUG: Received instagram_url: {instagram_url}")
            
            if not instagram_url:
                print("DEBUG: No instagram_url provided")
                return jsonify({
                    'error': 'Missing required field',
                    'message': 'Instagram URL is required'
                }), 400
            
            # Get caption from Instagram
            caption = extract_caption_from_instagram(instagram_url)
            print(f"DEBUG: Extracted caption: {caption}")
            
            # Check if an autograph already exists for this URL
            existing_autograph = Autograph.query.filter_by(instagram_url=instagram_url).first()
            print(f"DEBUG: Existing autograph check result: {existing_autograph}")
            
            if existing_autograph:
                print("DEBUG: Found existing autograph")
                return jsonify({
                    'error': 'Duplicate autograph',
                    'message': 'An autograph has already been generated for this Instagram post',
                    'existing_id': existing_autograph.id
                }), 400
            
            # Generate random code
            random_code = generate_random_value()
            print(f"DEBUG: Generated random code: {random_code}")
            
            # Convert code to zero-width characters
            invisible_code = encode_to_zero_width(random_code)
            print(f"DEBUG: Converted to invisible code")
            
            # Combine caption with invisible code
            combined_text = f"{caption}{invisible_code}"
            print(f"DEBUG: Created combined text")
            
            # Create new autograph
            autograph = Autograph(
                instagram_url=instagram_url,
                encryption_code=random_code
            )
            
            print("DEBUG: About to add to database")
            db.session.add(autograph)
            db.session.commit()
            print("DEBUG: Successfully committed to database")
            
            return jsonify({
                'success': True,
                'message': 'Autograph generated successfully',
                'autograph_id': autograph.id,
                'encrypted_code': random_code,
                'combined_text': combined_text
            })
            
        except Exception as e:
            print(f"DEBUG: Error in generate_autograph: {str(e)}")
            db.session.rollback()
            return jsonify({
                'error': 'Server error',
                'message': str(e)
            }), 500

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

    @app.route('/api/admin/invite-codes', methods=['GET'])
    @login_required
    def list_invite_codes():
        print("Accessing list_invite_codes endpoint")
        if not current_user.is_admin:
            print("Access denied: User is not admin")
            return jsonify({'error': 'Access denied'}), 403
        try:
            print("Fetching invite codes from database...")
            codes = InviteCode.query.order_by(InviteCode.created_at.desc()).all()
            print(f"Found {len(codes)} invite codes")
            
            result = []
            for code in codes:
                try:
                    code_data = {
                        'id': code.id,
                        'code': code.code,
                        'instagram_handle': code.instagram_handle,
                        'is_used': code.is_used,
                        'created_at': code.created_at.isoformat() if code.created_at else None,
                        'used_at': code.used_at.isoformat() if code.used_at else None
                    }
                    result.append(code_data)
                except Exception as e:
                    print(f"Error processing code {code.id}: {str(e)}")
                    continue
            
            print("Successfully prepared response")
            return jsonify(result)
        except Exception as e:
            print(f"Error in list_invite_codes: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return jsonify({'error': f'Failed to load invite codes. Error: {str(e)}'}), 500

    @app.route('/api/admin/invite-codes', methods=['POST'])
    @login_required
    def create_invite_code():
        if not current_user.is_admin:
            return jsonify({'error': 'Access denied'}), 403
        data = request.get_json()
        if not data or 'instagram_handle' not in data:
            return jsonify({'error': 'Instagram handle is required'}), 400

        handle = data['instagram_handle'].strip().lower()
        if handle.startswith('@'):
            handle = handle[1:]

        # Generate a unique invite code
        code = 'INV-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        new_code = InviteCode(
            code=code,
            instagram_handle=handle,
            is_used=False
        )
        
        try:
            db.session.add(new_code)
            db.session.commit()
            return jsonify({
                'id': new_code.id,
                'code': new_code.code,
                'instagram_handle': new_code.instagram_handle,
                'is_used': new_code.is_used,
                'created_at': new_code.created_at.isoformat(),
                'used_at': None
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/invite-codes/<int:code_id>', methods=['DELETE'])
    @login_required
    def delete_invite_code(code_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Access denied'}), 403
        code = InviteCode.query.get_or_404(code_id)
        try:
            db.session.delete(code)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
