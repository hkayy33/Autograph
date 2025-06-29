# Autograph

A secure Flask-based web application with SSL support, advanced error tracking, and invite code management system.

## 🚀 Features

- 🔒 SSL/HTTPS support with self-signed certificates
- 📊 Advanced error tracking and monitoring via Sentry
- 🔑 Invite code management system
- 🛡️ Production-ready security configurations
- 📝 Comprehensive logging system
- 🗄️ SQLAlchemy ORM for database management

## 🛠️ Tech Stack

- **Backend**: Python 3.11 + Flask
- **Database**: SQLAlchemy ORM
- **Monitoring**: Sentry
- **Security**: SSL/TLS with custom certificates
- **Additional Integrations**:
  - Flask integration
  - SQLAlchemy integration
  - Logging integration
  - Threading integration
  - Boto3 integration

## 📋 Prerequisites

- Python 3.11
- Virtual environment (venv)
- SSL certificates (provided in `/WebApp/certs/`)

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone [your-repo-url]
cd Autograph
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `WebApp/.env`:
```env
SENTRY_DSN=your_sentry_dsn_here
# Add other required environment variables
```

5. Navigate to the WebApp directory:
```bash
cd WebApp
```

6. Run the application:
```bash
python app.py --port 5002
```

The application will be available at:
- HTTPS: `https://localhost:5002`

## 🔒 SSL Configuration

The application uses self-signed certificates located in:
- Certificate: `/WebApp/certs/cert.pem`
- Private Key: `/WebApp/certs/key.pem`

**Note**: For development, you can safely proceed past the browser's security warning about the self-signed certificate.

## 🛣️ API Endpoints

### Admin API
- `GET /api/admin/invite-codes` - List all invite codes
- `POST /api/admin/invite-codes` - Create new invite code
- `DELETE /api/admin/invite-codes/{id}` - Delete specific invite code

### Static Resources
- `GET /static/css/styles.css` - Application styles

## 🔍 Monitoring & Debugging

### Sentry Integration
- Real-time error tracking
- Performance monitoring
- Transaction tracking
- Profiling in thread mode
- Multiple integration points

### Logging
- Application logs with multiple levels (DEBUG, INFO, WARNING)
- Structured logging with contextual information
- Separate error logging configuration

## 🔧 Development

### Common Issues
1. **Port Conflicts**: 
   - Default port is 5002
   - Use `--port` flag to specify different port
   ```bash
   python app.py --port 5003
   ```

2. **Certificate Warnings**:
   - Expected with self-signed certificates
   - Safe to proceed in development environment

3. **Missing Favicon**:
   - Known 404 error for `/favicon.ico`
   - Non-critical for functionality

## 🔜 Future Improvements

- [ ] Redis integration for caching
- [ ] Add favicon to prevent 404 errors
- [ ] Implement rate limiting for admin APIs
- [ ] Add API documentation
- [ ] Production-grade SSL certificates


