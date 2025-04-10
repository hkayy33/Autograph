# Change these relative imports
from WebApp.app import app
from WebApp.models import Autograph
from WebApp.database import db
from WebApp.encryption import Encryptor
import os
from dotenv import load_dotenv

def test_database():
    # Rest of the code remains the same
    load_dotenv()
    
    with app.app_context():
        db.create_all()
        
        encryptor = Encryptor(os.getenv('ENCRYPTION_KEY'))
        
        test_url = "https://instagram.com/p/test123"
        test_code = "TEST123"
        
        encrypted_code = encryptor.encrypt(test_code)
        
        autograph = Autograph(
            instagram_url=test_url,
            encrypted_code=encrypted_code,
            raw_code=test_code
        )
        
        db.session.add(autograph)
        db.session.commit()
        
        saved_autograph = Autograph.query.filter_by(instagram_url=test_url).first()
        
        if saved_autograph:
            print("✅ Database test successful!")
            print(f"Saved record: {saved_autograph}")
            
            decrypted_code = encryptor.decrypt(saved_autograph.encrypted_code)
            print(f"Original code: {test_code}")
            print(f"Decrypted code: {decrypted_code}")
            
            db.session.delete(saved_autograph)
            db.session.commit()
            print("✅ Test record cleaned up")
        else:
            print("❌ Failed to retrieve the saved record")

if __name__ == "__main__":
    test_database()