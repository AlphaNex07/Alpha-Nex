import os
from werkzeug.utils import secure_filename

# Alpha Nex Utility Functions
# Contains helper functions for file handling, XP calculations, and validation

ALLOWED_EXTENSIONS = {
    'video': ['mp4', 'avi', 'mov', 'wmv'],
    'audio': ['mp3', 'wav', 'aac', 'm4a'],
    'document': ['pdf', 'doc', 'docx', 'txt'],
    'code': ['py', 'js', 'html', 'css', 'java', 'cpp', 'c'],
    'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp']
}

def allowed_file(filename):
    """
    Check if file extension is allowed for upload.
    Supports multiple categories: video, audio, documents, code, images.
    """
    if not filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return True
    
    return False

def get_file_size(file):
    """Get file size in bytes."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer
    return size

def calculate_xp_reward(action_type):
    """
    Calculate XP reward for different user actions.
    Supports: upload, review, quality_bonus, daily_login.
    """
    rewards = {
        'upload': 20,
        'review': 10,
        'quality_bonus': 5,
        'daily_login': 5
    }
    return rewards.get(action_type, 0)

def format_file_size(bytes_size):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def get_file_category(filename):
    """Determine file category based on extension."""
    if not filename or '.' not in filename:
        return 'unknown'
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return category
    
    return 'unknown'

def sanitize_filename(filename):
    """Sanitize and secure filename."""
    return secure_filename(filename)

def is_valid_image(file_path):
    """Check if file is a valid image."""
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def calculate_deletion_penalty_hours(upload_time, deletion_time):
    """Calculate hours past free deletion window."""
    free_window_hours = 48
    upload_plus_free = upload_time + timedelta(hours=free_window_hours)
    
    if deletion_time <= upload_plus_free:
        return 0
    
    penalty_time = deletion_time - upload_plus_free
    return penalty_time.total_seconds() / 3600

def validate_content_description(description):
    """Validate content description for minimum quality."""
    if not description or len(description.strip()) < 10:
        return False, "Description must be at least 10 characters long."
    
    # Check for spam patterns
    spam_indicators = ['free money', 'click here', 'guaranteed', 'act now']
    description_lower = description.lower()
    
    for indicator in spam_indicators:
        if indicator in description_lower:
            return False, f"Description contains potentially spammy content: '{indicator}'"
    
    return True, "Description is valid."
