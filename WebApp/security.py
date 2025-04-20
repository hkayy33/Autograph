from flask import request, redirect

def configure_security(app):
    """Configure security features for the Flask application"""
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        # Prevent browsers from incorrectly detecting non-scripts as scripts
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Only allow your site to frame itself
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Enable HSTS with a 1 year duration
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Set secure cookie attributes
        if 'Set-Cookie' in response.headers:
            response.headers['Set-Cookie'] += '; HttpOnly; SameSite=Lax'
        
        # For APIs and AJAX requests, we need to be careful with CSP
        # Only apply strict CSP to HTML responses to avoid breaking APIs
        if response.mimetype == 'text/html':
            # Content Security Policy - Strict but allows necessary resources
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "img-src 'self' data:; "
                "font-src 'self' https://cdnjs.cloudflare.com; "
                "connect-src 'self'; "
                "frame-ancestors 'self'; "
                "form-action 'self'; "
                "base-uri 'self'; "
                "object-src 'none'; "
                "media-src 'self'; "
                "frame-src 'self';"
            )
        
        return response
    
    @app.before_request
    def redirect_to_https():
        """Redirect HTTP requests to HTTPS in production"""
        # Only redirect in production environment
        if not app.debug and not app.testing:
            if request.headers.get('X-Forwarded-Proto') == 'http':
                url = request.url.replace('http://', 'https://', 1)
                app.logger.info(f'Redirecting HTTP request to HTTPS: {url}')
                return redirect(url, code=301)
    
    return app 