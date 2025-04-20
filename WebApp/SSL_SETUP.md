# SSL Setup Guide

## Development Environment

1. **Using Self-Signed Certificates**
   ```bash
   # Generate self-signed certificates
   cd /Users/hassan/Autograph/WebApp
   mkdir -p certificates
   openssl req -x509 -newkey rsa:4096 -nodes -out certificates/cert.pem -keyout certificates/key.pem -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
   ```

2. **Update .env Configuration**
   ```
   SSL_ENABLED=True
   SSL_CERT_PATH=/Users/hassan/Autograph/WebApp/certificates/cert.pem
   SSL_KEY_PATH=/Users/hassan/Autograph/WebApp/certificates/key.pem
   ```

3. **Run Development Server**
   ```bash
   python app.py
   ```

## Production Environment

1. **Install Required Software**
   ```bash
   # Install Nginx
   sudo apt update
   sudo apt install nginx

   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Set Up Domain**
   - Ensure your domain points to your server's IP address
   - Configure DNS A record for your domain

3. **Generate Let's Encrypt Certificate**
   ```bash
   # Run the SSL setup script
   python ssl_setup.py --domain your-domain.com
   ```

4. **Generate DH Parameters**
   ```bash
   # Make the script executable
   chmod +x generate_dhparam.sh
   
   # Run the script
   sudo ./generate_dhparam.sh
   ```

5. **Configure Nginx**
   ```bash
   # Copy Nginx configuration
   sudo cp nginx.conf /etc/nginx/nginx.conf
   
   # Update domain name in configuration
   sudo sed -i 's/your-domain.com/actual-domain.com/g' /etc/nginx/nginx.conf
   
   # Test configuration
   sudo nginx -t
   
   # Restart Nginx
   sudo systemctl restart nginx
   ```

6. **Update Production Environment**
   ```
   SSL_ENABLED=True
   SSL_CERT_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
   SSL_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem
   ```

7. **Start Application**
   ```bash
   # Using Gunicorn
   gunicorn -w 4 -b 127.0.0.1:5001 app:app
   ```

## Security Considerations

1. **Certificate Renewal**
   - Let's Encrypt certificates are valid for 90 days
   - Automatic renewal is configured via cron job
   - Monitor renewal process in `/var/log/letsencrypt/`

2. **SSL Configuration**
   - Only TLS 1.2 and 1.3 are enabled
   - Strong cipher suite configuration
   - Perfect Forward Secrecy with DH parameters
   - HSTS enabled
   - Security headers configured

3. **Monitoring**
   - Check SSL certificate expiration
   - Monitor SSL/TLS handshake errors in Nginx logs
   - Regular security audits

## Troubleshooting

1. **Certificate Issues**
   ```bash
   # Check certificate validity
   openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -text -noout
   
   # Test SSL connection
   openssl s_client -connect your-domain.com:443 -tls1_2
   ```

2. **Nginx Issues**
   ```bash
   # Check Nginx error logs
   sudo tail -f /var/log/nginx/error.log
   
   # Test Nginx configuration
   sudo nginx -t
   ```

3. **Common Problems**
   - Certificate renewal failures
   - Nginx configuration errors
   - Permission issues with certificate files
   - SSL handshake failures

## Maintenance

1. **Regular Tasks**
   - Monitor certificate expiration
   - Check Nginx logs for SSL/TLS issues
   - Update SSL configuration when new vulnerabilities are discovered
   - Keep Nginx and Certbot updated

2. **Backup**
   - Regularly backup SSL certificates and private keys
   - Store backups securely
   - Document renewal and backup procedures 