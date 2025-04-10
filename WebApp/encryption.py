from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Encryptor:
    def __init__(self):
        # Generate a random key for encryption
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
    
    def encrypt(self, text: str) -> str:
        """
        Encrypt the given text using Fernet symmetric encryption.
        
        Args:
            text (str): The text to encrypt
            
        Returns:
            str: The encrypted text as a base64 encoded string
        """
        # Convert text to bytes and encrypt
        text_bytes = text.encode()
        encrypted_bytes = self.cipher_suite.encrypt(text_bytes)
        
        # Convert to base64 string for easy storage/transmission
        return base64.urlsafe_b64encode(encrypted_bytes).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt the given encrypted text.
        
        Args:
            encrypted_text (str): The encrypted text as a base64 encoded string
            
        Returns:
            str: The decrypted text
        """
        try:
            # Convert from base64 and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            
            # Convert back to string
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt text: {str(e)}")