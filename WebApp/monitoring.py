import os
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from functools import wraps
import time

def setup_monitoring(app):
    """Configure monitoring and logging for the application"""
    
    # Configure Sentry
    sentry_dsn = os.getenv('SENTRY_DSN')
    if sentry_dsn and sentry_dsn != 'your_sentry_dsn_here':
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration()
            ],
            traces_sample_rate=1.0,
            environment=os.getenv('FLASK_ENV', 'development')
        )
        app.logger.info("Sentry monitoring initialized")
    
    # Configure JSON logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    json_handler = RotatingFileHandler('logs/autograph.log', maxBytes=10000000, backupCount=5)
    json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    json_handler.setFormatter(json_formatter)
    app.logger.addHandler(json_handler)
    
    # Configure error logging
    error_handler = RotatingFileHandler('logs/errors.log', maxBytes=10000000, backupCount=5)
    error_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    error_handler.setFormatter(error_formatter)
    error_handler.setLevel(logging.ERROR)
    app.logger.addHandler(error_handler)
    
    # Set overall logging level
    app.logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

def log_security_event(event_type, level, details):
    """Log security-related events"""
    logger = logging.getLogger('security')
    log_func = getattr(logger, level, logger.info)
    log_func(f"Security event: {event_type}", extra={
        'event_type': event_type,
        'details': details
    })

def monitor_performance(f):
    """Decorator to monitor function performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        duration = time.time() - start_time
        
        logger = logging.getLogger('performance')
        logger.info(f"Function {f.__name__} took {duration:.2f} seconds to execute")
        
        return result
    return decorated_function 