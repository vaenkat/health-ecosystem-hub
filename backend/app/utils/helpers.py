"""
Helper utilities for Health Ecosystem Hub Backend
"""

import uuid
import hashlib
import secrets
import time
from datetime import datetime, date
from typing import Any, Dict, List, Optional
import json
import re


def generate_id() -> str:
    """Generate a unique UUID string"""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """Generate a short unique ID"""
    return secrets.token_hex(length // 2)[:length]


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_random_token(length: int = 32) -> str:
    """Generate a random token"""
    return secrets.token_urlsafe(length)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def parse_datetime(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse string to datetime"""
    try:
        return datetime.strptime(date_string, format_str)
    except ValueError:
        return None


def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date"""
    today = date.today()
    age = today.year - birth_date.year
    
    # Adjust age if birthday hasn't occurred this year yet
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency"""
    return f"{currency} {amount:,.2f}"


def format_phone_number(phone: str) -> str:
    """Format phone number consistently"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Format as (XXX) XXX-XXXX if 10 digits
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) > 10:
        return digits[-10:]  # Last 10 digits
    else:
        return digits


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_string(text: str) -> str:
    """Clean and normalize string"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s\-\.,]', '', text)
    
    return text.strip()


def serialize_data(data: Any) -> str:
    """Serialize data to JSON string"""
    try:
        return json.dumps(data, default=str, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot serialize data: {str(e)}")


def deserialize_data(json_string: str) -> Any:
    """Deserialize JSON string to data"""
    try:
        return json.loads(json_string)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot deserialize JSON: {str(e)}")


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary"""
    return data.get(key, default)


def safe_get_nested(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Safely get nested value from dictionary"""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Filter dictionary to only include specified keys"""
    return {k: v for k, v in data.items() if k in keys}


def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}


def flatten_dict(data: Dict[str, Any], separator: str = "_") -> Dict[str, Any]:
    """Flatten nested dictionary"""
    def _flatten(obj, parent_key=''):
        items = {}
        for k, v in obj.items():
            new_key = f"{parent_key}{separator}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(_flatten(v, new_key))
            else:
                items[new_key] = v
        return items
    
    return _flatten(data)


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks"""
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i + chunk_size])
    return chunks


def paginate_list(items: List[Any], page: int, page_size: int) -> Dict[str, Any]:
    """Paginate list"""
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "items": items[start:end],
        "page": page,
        "page_size": page_size,
        "total": len(items),
        "total_pages": (len(items) + page_size - 1) // page_size,
        "has_next": end < len(items),
        "has_prev": page > 1
    }


def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return (part / total) * 100


def round_to_nearest(value: float, nearest: float = 0.5) -> float:
    """Round to nearest value"""
    return round(value / nearest) * nearest


def get_timestamp() -> int:
    """Get current timestamp"""
    return int(time.time())


def get_iso_timestamp() -> str:
    """Get current ISO timestamp"""
    return datetime.utcnow().isoformat() + 'Z'


def days_between(start_date: date, end_date: date) -> int:
    """Calculate days between two dates"""
    return abs((end_date - start_date).days)


def add_days_to_date(start_date: date, days: int) -> date:
    """Add days to date"""
    return start_date + datetime.timedelta(days=days)


def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is valid UUID"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data showing only first and last few characters"""
    if len(data) <= visible_chars * 2:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars * 2) + data[-visible_chars:]


def generate_filename(prefix: str, extension: str = ".txt") -> str:
    """Generate filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}{extension}"


def extract_domain(email: str) -> str:
    """Extract domain from email address"""
    try:
        return email.split('@')[1].lower()
    except IndexError:
        return ""


def is_valid_url(url: str) -> bool:
    """Check if string is valid URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip address
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove path separators
    filename = filename.replace('/', '').replace('\\', '')
    
    # Remove special characters except letters, numbers, dots, hyphens, underscores
    filename = re.sub(r'[^\w\-.]', '', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip(' .')
    
    # Ensure it's not empty
    if not filename:
        filename = f"file_{int(time.time())}"
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename"""
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    mime_types = {
        'txt': 'text/plain',
        'html': 'text/html',
        'css': 'text/css',
        'js': 'application/javascript',
        'json': 'application/json',
        'xml': 'application/xml',
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed'
    }
    
    return mime_types.get(extension, 'application/octet-stream')


def create_response_dict(success: bool = True, message: str = "", data: Any = None, 
                     error_code: str = None, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create standardized response dictionary"""
    response = {
        "success": success,
        "message": message,
        "timestamp": get_timestamp()
    }
    
    if data is not None:
        response["data"] = data
    
    if error_code:
        response["error_code"] = error_code
    
    if details:
        response["details"] = details
    
    return response


def create_error_response(message: str, error_code: str = "ERROR", details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    return create_response_dict(
        success=False,
        message=message,
        error_code=error_code,
        details=details
    )


def create_success_response(message: str = "Operation successful", data: Any = None) -> Dict[str, Any]:
    """Create standardized success response"""
    return create_response_dict(
        success=True,
        message=message,
        data=data
    )


def deep_merge_dict(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result


def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get nested value using dot notation path"""
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """Set nested value using dot notation path"""
    keys = path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def convert_to_snake_case(text: str) -> str:
    """Convert text to snake_case"""
    # Insert underscore before capital letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    # Insert underscore before capital letters that follow lowercase letters or numbers
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    # Replace spaces and hyphens with underscores
    s3 = re.sub(r'[-\s]+', '_', s2)
    # Convert to lowercase
    return s3.lower()


def convert_to_camel_case(text: str) -> str:
    """Convert text to camelCase"""
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def validate_json_structure(data: Any, required_keys: List[str] = None) -> tuple[bool, Optional[str]]:
    """Validate JSON structure"""
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    if required_keys:
        for key in required_keys:
            if key not in data:
                return False, f"Missing required key: {key}"
    
    return True, None


def create_search_query(search_term: str, search_fields: List[str]) -> Dict[str, Any]:
    """Create search query for database"""
    if not search_term or not search_fields:
        return {}
    
    # Create OR condition for search fields
    or_conditions = []
    for field in search_fields:
        or_conditions.append({
            f"{field}.ilike": f"%{search_term}%"
        })
    
    return {
        "or": or_conditions
    }


def calculate_page_offset(page: int, page_size: int) -> int:
    """Calculate database offset for pagination"""
    return (page - 1) * page_size


def format_list_response(items: List[Any], page: int, page_size: int, total: int = None) -> Dict[str, Any]:
    """Format paginated list response"""
    if total is None:
        total = len(items)
    
    total_pages = (total + page_size - 1) // page_size
    start_index = (page - 1) * page_size
    end_index = min(start_index + page_size, total)
    
    return {
        "items": items[start_index:end_index],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
