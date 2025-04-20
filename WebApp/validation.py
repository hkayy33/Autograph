import re
import bleach
from urllib.parse import urlparse, parse_qs
import logging
from flask import current_app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_instagram_post_id(url):
    """Extract the Instagram post ID from a URL.
    
    Args:
        url (str): Instagram post URL
        
    Returns:
        str: Post ID if found, None otherwise
    """
    try:
        # Match pattern /p/XXXXXX/ or /reel/XXXXXX/ in the URL
        match = re.search(r'/(?:p|reel)/([^/]+)/', url)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        logger.error(f"Error extracting Instagram post ID: {e}")
        return None

def validate_instagram_url(url):
    """Validate Instagram URL format and check if it's a valid post/reel URL."""
    if not url:
        return False, "Please provide an Instagram URL. Example: https://www.instagram.com/p/ABC123xyz/ or https://www.instagram.com/reel/ABC123xyz/"
    
    # Remove @ symbol if present at the start
    url = url.lstrip('@')
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc.endswith('instagram.com'):
            return False, "Please provide a valid Instagram URL. Example: https://www.instagram.com/p/ABC123xyz/ or https://www.instagram.com/reel/ABC123xyz/"
        
        if not re.match(r'^https://.*instagram\.com/(?:p|reel)/[^/]+/?.*$', url):
            return False, "Please provide a valid Instagram post or reel URL. Examples:\nhttps://www.instagram.com/p/ABC123xyz/\nhttps://www.instagram.com/reel/ABC123xyz/"
            
        post_id = extract_instagram_post_id(url)
        if not post_id:
            return False, "Could not extract post ID from URL. Please make sure you're using a direct post or reel URL."
            
        return True, post_id
            
    except Exception as e:
        logger.error(f"Error validating Instagram URL: {e}")
        return False, "Invalid URL format. Please provide a URL like: https://www.instagram.com/p/ABC123xyz/ or https://www.instagram.com/reel/ABC123xyz/"

def validate_caption(caption):
    """
    Validates an Instagram caption:
    - Can be empty
    - If not empty, must be within length limits
    - Must not contain dangerous HTML/script tags
    - Must only contain allowed special characters
    """
    if not caption:
        return True, ""  # Allow empty captions
        
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

def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks"""
    if text is None:
        return ""
    
    # Define allowed tags and attributes
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'span']
    allowed_attrs = {
        '*': ['class', 'style'],
        'span': ['class', 'style']
    }
    
    # Clean the text using bleach
    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True,
        strip_comments=True
    )

def sanitize_instagram_handle(handle):
    """Sanitize Instagram handle input"""
    if not handle:
        return ""
    
    # Remove @ symbol if present
    handle = handle.lstrip('@')
    
    # Only allow alphanumeric characters, dots, and underscores
    handle = re.sub(r'[^a-zA-Z0-9._]', '', handle)
    
    return handle.lower()

def sanitize_url(url):
    """Sanitize URL input"""
    if not url:
        return ""
    
    # Basic URL validation
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Remove any script tags or other potentially dangerous content
    return bleach.clean(url, tags=[], attributes=[], strip=True)

def sanitize_caption(caption):
    """Sanitize Instagram caption input"""
    if not caption:
        return ""
    
    # Define allowed tags and attributes for captions
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    allowed_attrs = {'*': ['class']}
    
    # Clean the caption
    return bleach.clean(
        caption,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True,
        strip_comments=True
    ) 