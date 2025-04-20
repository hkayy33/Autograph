import re
import bleach
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def validate_instagram_url(url):
    """
    Validates an Instagram URL:
    - Must be a valid URL format
    - Must be from instagram.com domain
    - Must follow Instagram post URL pattern
    """
    if not url:
        return False, "URL cannot be empty"
        
    try:
        # Parse URL
        parsed = urlparse(url)
        
        # Check domain
        if not parsed.netloc.endswith('instagram.com'):
            return False, "URL must be from instagram.com"
            
        # Check URL pattern (instagram.com/p/POSTID or instagram.com/reel/POSTID)
        pattern = r'^https?://(?:www\.)?instagram\.com/(?:p|reel)/[\w-]+/?$'
        if not re.match(pattern, url):
            return False, "Invalid Instagram post URL format"
            
        return True, "Valid Instagram URL"
        
    except Exception:
        return False, "Invalid URL format"

def validate_caption(caption):
    """
    Validates an Instagram caption:
    - Must not be empty
    - Must be within length limits
    - Must not contain dangerous HTML/script tags
    - Must only contain allowed special characters
    """
    if not caption:
        return False, "Caption cannot be empty"
        
    if len(caption) > 2200:  # Instagram's caption limit
        return False, "Caption exceeds maximum length of 2200 characters"
        
    try:
        # Define allowed HTML tags and attributes
        allowed_tags = ['p', 'br', 'b', 'i', 'em', 'strong', 'a']
        allowed_attributes = {
            'a': ['href', 'title', 'target']
        }
        
        # Sanitize HTML content
        sanitized_caption = bleach.clean(
            caption,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        
        # Check for remaining malicious patterns
        if contains_malicious_patterns(sanitized_caption):
            return False, "Caption contains potentially malicious content"
            
        # Allow only specific special characters and emojis
        allowed_pattern = r'^[\w\s\.,!?@#$%&*()_+\-=\[\]{}|;:\'"\\/±§`~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×÷\u2600-\u26FF\u2700-\u27BF\u2B50\u2B55\u2600-\u26FF\u2700-\u27BF\u2B50\u2B55\U0001F300-\U0001F9FF]+$'
        if not re.match(allowed_pattern, sanitized_caption, re.UNICODE):
            return False, "Caption contains invalid characters"
            
        return True, sanitized_caption
        
    except Exception as e:
        logger.error(f"Error validating caption: {e}")
        return False, "Error validating caption"

def contains_malicious_patterns(text):
    """
    Check for potentially malicious patterns in text.
    Returns True if malicious patterns are found.
    """
    malicious_patterns = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+=".*?"',  # Event handlers
        r'data:text/html',  # Data URLs
        r'vbscript:',  # VBScript
        r'expression\(.*?\)',  # CSS expressions
    ]

    for pattern in malicious_patterns:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            return True

    return False 