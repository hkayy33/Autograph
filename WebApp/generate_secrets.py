import secrets
from cryptography.fernet import Fernet

def generate_secrets():
    # Generate a secure random secret key for Flask
    secret_key = secrets.token_hex(32)
    
    # Generate a secure encryption key for Fernet
    encryption_key = Fernet.generate_key().decode()
    
    print("\nGenerated Secrets:")
    print("-----------------")
    print(f"SECRET_KEY={secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print("\nCopy these values to your .env file")
    print("Make sure to keep these secrets secure and never commit them to version control!")

if __name__ == "__main__":
    generate_secrets() 