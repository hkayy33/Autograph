import subprocess
import os
from pathlib import Path

def install_certbot():
    """Install certbot using brew on macOS"""
    try:
        # Check if certbot is installed
        subprocess.run(['certbot', '--version'], capture_output=True)
        print("Certbot is already installed")
    except FileNotFoundError:
        print("Installing Certbot...")
        try:
            subprocess.run(['brew', 'install', 'certbot'], check=True)
            print("Certbot installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing Certbot: {e}")
            return False
    return True

def setup_lets_encrypt(domain):
    """
    Set up Let's Encrypt SSL certificate for the domain
    
    Args:
        domain (str): Domain name for the certificate
    """
    try:
        # Create directory for certificates if it doesn't exist
        cert_dir = Path('certificates')
        cert_dir.mkdir(exist_ok=True)
        
        # Request certificate
        cmd = [
            'sudo', 'certbot', 'certonly',
            '--standalone',  # Use standalone mode
            '-d', domain,    # Domain
            '--agree-tos',   # Agree to terms
            '--non-interactive',  # Non-interactive mode
            '--cert-path', str(cert_dir)  # Certificate path
        ]
        
        subprocess.run(cmd, check=True)
        print(f"SSL certificate obtained successfully for {domain}")
        
        # Print certificate locations
        print("\nCertificate locations:")
        print(f"Cert: /etc/letsencrypt/live/{domain}/fullchain.pem")
        print(f"Key: /etc/letsencrypt/live/{domain}/privkey.pem")
        
    except subprocess.CalledProcessError as e:
        print(f"Error obtaining SSL certificate: {e}")
        return False
    return True

def setup_auto_renewal():
    """Set up automatic certificate renewal"""
    try:
        # Add cron job for automatic renewal
        cron_cmd = '0 0 1 * * certbot renew --quiet'
        with open('/tmp/certbot_cron', 'w') as f:
            f.write(cron_cmd + '\n')
        
        subprocess.run(['sudo', 'crontab', '/tmp/certbot_cron'], check=True)
        os.remove('/tmp/certbot_cron')
        
        print("Automatic certificate renewal configured")
        return True
    except Exception as e:
        print(f"Error setting up auto-renewal: {e}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='SSL Certificate Setup')
    parser.add_argument('--domain', required=True, help='Domain name for the certificate')
    args = parser.parse_args()
    
    if install_certbot():
        if setup_lets_encrypt(args.domain):
            setup_auto_renewal() 