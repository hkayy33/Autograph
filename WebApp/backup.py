#!/usr/bin/env python
"""Database backup script for Autograph"""
import os
import subprocess
import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='logs/backup.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('backup')

def create_database_backup():
    """Create a PostgreSQL database backup"""
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Get database URL from environment
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Parse database connection info
        # Format: postgresql://username:password@hostname:port/dbname
        db_parts = db_url.replace('postgresql://', '').split('/')
        db_connection = db_parts[0].split('@')
        db_name = db_parts[1].split('?')[0]  # Remove any query parameters
        
        if '@' in db_url:
            db_auth = db_connection[0].split(':')
            db_host = db_connection[1].split(':')
            
            db_user = db_auth[0]
            db_pass = db_auth[1] if len(db_auth) > 1 else ''
            db_hostname = db_host[0]
            db_port = db_host[1] if len(db_host) > 1 else '5432'
        else:
            # Handle case where there's no auth info
            db_hostname = db_connection[0].split(':')[0]
            db_port = db_connection[0].split(':')[1] if ':' in db_connection[0] else '5432'
            db_user = ''
            db_pass = ''
        
        # Set environment variables for pg_dump
        env = os.environ.copy()
        if db_pass:
            env['PGPASSWORD'] = db_pass
        
        # Backup filename
        backup_file = f"{backup_dir}/autograph_db_{timestamp}.sql"
        
        # Create backup using pg_dump
        cmd = [
            'pg_dump',
            '-h', db_hostname,
            '-p', db_port,
            '-U', db_user,
            '-F', 'c',  # Custom format (compressed)
            '-b',  # Include large objects
            '-v',  # Verbose
            '-f', backup_file,
            db_name
        ]
        
        logger.info(f"Creating database backup: {backup_file}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Backup failed: {result.stderr}")
            raise Exception(f"Database backup failed: {result.stderr}")
        
        logger.info(f"Backup created successfully: {backup_file}")
        return backup_file
    
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise

def cleanup_old_backups(max_backups=10):
    """Delete old backups to save space"""
    try:
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return
        
        # List all backup files
        backups = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) 
                  if f.startswith('autograph_db_') and f.endswith('.sql')]
        
        # Sort by modification time (oldest first)
        backups.sort(key=lambda x: os.path.getmtime(x))
        
        # Delete old backups
        while len(backups) > max_backups:
            old_backup = backups.pop(0)  # Get oldest backup
            logger.info(f"Removing old backup: {old_backup}")
            os.remove(old_backup)
    
    except Exception as e:
        logger.error(f"Error cleaning up old backups: {str(e)}")

def main():
    """Main backup function"""
    try:
        logger.info("Starting database backup process")
        
        # Create database backup
        backup_file = create_database_backup()
        
        # Cleanup old backups
        cleanup_old_backups()
        
        logger.info("Backup process completed successfully")
    
    except Exception as e:
        logger.error(f"Backup process failed: {str(e)}")

if __name__ == "__main__":
    main() 