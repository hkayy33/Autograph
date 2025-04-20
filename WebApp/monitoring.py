import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from dotenv import load_dotenv
from functools import wraps
import time

load_dotenv()

def setup_monitoring(app):
    """Configure monitoring and alerts for the application"""
    
    # Configure Sentry with advanced settings
    sentry_dsn = os.getenv('SENTRY_DSN')
    if sentry_dsn and sentry_dsn != 'your_sentry_dsn_here':
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        
        # Initialize Sentry with all integrations
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
                logging_integration
            ],
            traces_sample_rate=1.0,
            environment=os.getenv('FLASK_ENV', 'production'),
            
            # Configure alert rules
            before_send=before_send_event,
            
            # Performance monitoring
            enable_tracing=True,
            profiles_sample_rate=1.0,
            
            # Additional context
            send_default_pii=False,
            debug=app.debug
        )
        
        # Set default tags
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag('server_name', os.getenv('SERVER_NAME', 'unknown'))
            scope.set_tag('deployment', os.getenv('DEPLOYMENT_ID', 'unknown'))
        
        # Set up custom alert rules
        configure_sentry_alerts()
        
        app.logger.info("Sentry monitoring initialized with advanced configuration")
    
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

    return app

def before_send_event(event, hint):
    """Process and filter events before sending to Sentry"""
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Ignore certain types of errors
        if isinstance(exc_value, (KeyboardInterrupt, SystemExit)):
            return None
        
        # Add additional context for database errors
        if 'sqlalchemy' in str(exc_type).lower():
            event['tags']['database_error'] = True
            event['fingerprint'] = ['database-error', str(exc_type)]
    
    # Add severity level based on error type
    if event.get('level') == 'error':
        if any(critical_term in str(event).lower() for critical_term in 
            ['security', 'breach', 'unauthorized', 'permission denied']):
            event['level'] = 'fatal'
    
    return event

def configure_sentry_alerts():
    """Configure custom alert rules for Sentry"""
    try:
        # These would normally be configured in Sentry's UI, but documented here
        alert_rules = {
            'high_error_rate': {
                'name': 'High Error Rate Alert',
                'trigger': {
                    'timeWindow': '10m',
                    'errorCount': 100
                }
            },
            'authentication_failures': {
                'name': 'Authentication Failure Alert',
                'trigger': {
                    'timeWindow': '5m',
                    'errorCount': 10,
                    'errorType': 'AuthenticationError'
                }
            },
            'database_errors': {
                'name': 'Database Error Alert',
                'trigger': {
                    'timeWindow': '5m',
                    'errorCount': 5,
                    'errorType': 'DatabaseError'
                }
            },
            'api_latency': {
                'name': 'API Latency Alert',
                'trigger': {
                    'timeWindow': '5m',
                    'threshold': '2s'
                }
            }
        }
        
        # Log alert configuration
        logging.info("Sentry alert rules configured", extra={'rules': alert_rules})
        
    except Exception as e:
        logging.error(f"Failed to configure Sentry alerts: {str(e)}")

def monitor_performance(f):
    """Decorator to monitor function performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Track performance in Sentry
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("performance_monitoring", f.__name__)
                scope.set_extra("execution_time", execution_time)
                
                # Alert on slow operations
                if execution_time > 2.0:  # 2 seconds threshold
                    sentry_sdk.capture_message(
                        f"Slow operation detected in {f.__name__}",
                        level="warning",
                        extras={
                            "execution_time": execution_time,
                            "function": f.__name__
                        }
                    )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Capture exception with performance context
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("performance_monitoring", f.__name__)
                scope.set_extra("execution_time", execution_time)
                scope.set_extra("failed_operation", True)
                sentry_sdk.capture_exception(e)
            
            raise
            
    return decorated_function

def capture_security_event(event_type, details, level='error'):
    """Capture security-related events in Sentry"""
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("event_type", "security")
        scope.set_tag("security_event", event_type)
        scope.set_level(level)
        
        sentry_sdk.capture_message(
            f"Security Event: {event_type}",
            extras={
                "details": details,
                "timestamp": time.time()
            }
        )

def track_user_action(action_type, user_id=None, details=None):
    """Track important user actions"""
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("action_type", action_type)
        if user_id:
            scope.set_user({"id": user_id})
        
        sentry_sdk.capture_message(
            f"User Action: {action_type}",
            level="info",
            extras={
                "details": details,
                "timestamp": time.time()
            }
        )

def log_security_event(event_type, level, details):
    """Log security-related events"""
    logger = logging.getLogger('security')
    log_func = getattr(logger, level, logger.info)
    log_func(f"Security event: {event_type}", extra={
        'event_type': event_type,
        'details': details
    }) 