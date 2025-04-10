import pytest
import requests
import json
from flask_sqlalchemy import SQLAlchemy

BASE_URL = 'http://localhost:5002'

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

def test_encrypt_endpoint():
    # Test data
    test_data = {
        'text': 'Hello, World!'
    }
    
    # Make POST request to encrypt endpoint
    response = requests.post(f'{BASE_URL}/encrypt', json=test_data)
    
    # Check response status code
    assert response.status_code == 200
    
    # Check response format
    data = response.json()
    assert 'encrypted_text' in data
    assert isinstance(data['encrypted_text'], str)
    assert len(data['encrypted_text']) > 0

def test_decrypt_endpoint():
    # First encrypt some text
    test_data = {
        'text': 'Hello, World!'
    }
    encrypt_response = requests.post(f'{BASE_URL}/encrypt', json=test_data)
    encrypted_text = encrypt_response.json()['encrypted_text']
    
    # Now decrypt the encrypted text
    decrypt_data = {
        'text': encrypted_text
    }
    decrypt_response = requests.post(f'{BASE_URL}/decrypt', json=decrypt_data)
    
    # Check response status code
    assert decrypt_response.status_code == 200
    
    # Check response format
    data = decrypt_response.json()
    assert 'decrypted_text' in data
    assert data['decrypted_text'] == test_data['text']

def test_encrypt_missing_text():
    # Test with missing text field
    test_data = {}
    
    # Make POST request to encrypt endpoint
    response = requests.post(f'{BASE_URL}/encrypt', json=test_data)
    
    # Check response status code
    assert response.status_code == 400
    
    # Check error message
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'No text provided'

def test_decrypt_missing_text():
    # Test with missing text field
    test_data = {}
    
    # Make POST request to decrypt endpoint
    response = requests.post(f'{BASE_URL}/decrypt', json=test_data)
    
    # Check response status code
    assert response.status_code == 400
    
    # Check error message
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'No text provided'

if __name__ == '__main__':
    pytest.main([__file__]) 