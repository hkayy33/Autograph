import re
from urllib.parse import urlparse

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
        
    # Check for HTML/Script tags
    if re.search(r'<[^>]*>|<script|javascript:', caption, re.IGNORECASE):
        return False, "Caption contains invalid HTML or script content"
        
    # Allow only specific special characters and emojis
    allowed_pattern = r'^[\w\s\.,!?@#$%&*()_+\-=\[\]{}|;:\'"\\/±§`~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×÷\u2600-\u26FF\u2700-\u27BF\u2B50\u2B55\u2600-\u26FF\u2700-\u27BF\u2B50\u2B55\U0001F300-\U0001F9FF]+$'
    if not re.match(allowed_pattern, caption, re.UNICODE):
        return False, "Caption contains invalid characters"
        
    return True, "Valid caption" 