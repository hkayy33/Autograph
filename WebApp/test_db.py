from WebApp.app import app
from WebApp.models import Autograph
from WebApp.database import db
from WebApp.encryption import Encryptor
import os
import time
from dotenv import load_dotenv
from cryptography.fernet import Fernet

def test_database():
    # Load environment variables
    load_dotenv()
    
    with app.app_context():
        db.create_all()  # Ensure the table exists
        
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key:
            print("No encryption key found in .env file. Generating a new one...")
            encryption_key = Fernet.generate_key().decode()
            print(f"Generated key: {encryption_key}")
            print("Add this key to your .env file as ENCRYPTION_KEY=<key>")
        
        encryptor = Encryptor(encryption_key)
        
        # Create a unique URL and code using timestamp to avoid conflicts
        timestamp = int(time.time())
        test_url = f"https://instagram.com/p/test{timestamp}"
        test_code = f"TEST{timestamp}"
        
        encrypted_code = encryptor.encrypt(test_code)
        
        print(f"Adding new record:")
        print(f"Instagram URL: {test_url}")
        print(f"Raw Code: {test_code}")
        print(f"Encrypted Code: {encrypted_code}")
        
        autograph = Autograph(
            instagram_url=test_url,
            encrypted_code=encrypted_code,
            raw_code=test_code
        )
        
        try:
            db.session.add(autograph)
            db.session.commit()
            print("✅ Record added successfully!")
        except Exception as e:
            print(f"❌ Error occurred: {str(e)}")
            db.session.rollback()
            return  # Exit if we couldn't add the record
        
        saved_autograph = Autograph.query.filter_by(instagram_url=test_url).first()
        
        if saved_autograph:
            print("✅ Database test successful!")
            print(f"Saved record ID: {saved_autograph.id}")
            print(f"Saved Instagram URL: {saved_autograph.instagram_url}")
            
            decrypted_code = encryptor.decrypt(saved_autograph.encrypted_code)
            print(f"Original code: {test_code}")
            print(f"Decrypted code: {decrypted_code}")
            
            if test_code == decrypted_code:
                print("✅ Encryption/decryption test passed!")
            else:
                print("❌ Encryption/decryption test failed!")
            
            # Comment out these lines to keep the test data in the database
            # db.session.delete(saved_autograph)
            # db.session.commit()
            # print("✅ Test record cleaned up")
        else:
            print("❌ Failed to retrieve the saved record")
            
        # Print all records in the database for verification
        print("\nAll records in database:")
        all_records = Autograph.query.all()
        for record in all_records:
            print(f"ID: {record.id}, URL: {record.instagram_url}, Raw Code: {record.raw_code}")

if __name__ == "__main__":
    test_database()
    print("\nTest completed. Check your database for the new record.")

# Generate a new key for reference (comment out if not needed)
# key = Fernet.generate_key()
# print("New key generated (for reference):", key.decode())