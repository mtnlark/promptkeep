import re

def sanitize_filename(title: str) -> str:
    """Sanitize a title to create a valid filename"""
    # Convert to lowercase
    title = title.lower()
    
    # Replace invalid characters with hyphens
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '-', title)
    
    # Replace spaces with hyphens
    sanitized = sanitized.replace(' ', '-')
    
    # Remove consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    
    # Limit length to 100 characters
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized 