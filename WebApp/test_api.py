import pytest
from flask import Flask
from .app import app as flask_app
import json

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_encrypt_endpoint(client):
    # Test data
    test_data = {
        'text': 'Hello, World!'
    }
    
    # Make POST request to encrypt endpoint
    response = client.post('/encrypt', json=test_data)
    
    # Check response status code
    assert response.status_code == 200
    
    # Check response format
    data = json.loads(response.data)
    assert 'encrypted_text' in data
    assert isinstance(data['encrypted_text'], str)
    assert len(data['encrypted_text']) > 0

def test_decrypt_endpoint(client):
    # First encrypt some text
    test_data = {
        'text': 'Hello, World!'
    }
    encrypt_response = client.post('/encrypt', json=test_data)
    encrypted_text = json.loads(encrypt_response.data)['encrypted_text']
    
    # Now decrypt the encrypted text
    decrypt_data = {
        'text': encrypted_text
    }
    decrypt_response = client.post('/decrypt', json=decrypt_data)
    
    # Check response status code
    assert decrypt_response.status_code == 200
    
    # Check response format
    data = json.loads(decrypt_response.data)
    assert 'decrypted_text' in data
    assert data['decrypted_text'] == test_data['text']

def test_encrypt_missing_text(client):
    # Test with missing text field
    test_data = {}
    
    # Make POST request to encrypt endpoint
    response = client.post('/encrypt', json=test_data)
    
    # Check response status code
    assert response.status_code == 400
    
    # Check error message
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'No text provided'

def test_decrypt_missing_text(client):
    # Test with missing text field
    test_data = {}
    
    # Make POST request to decrypt endpoint
    response = client.post('/decrypt', json=test_data)
    
    # Check response status code
    assert response.status_code == 400
    
    # Check error message
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'No text provided'

if __name__ == '__main__':
    pytest.main([__file__]) 