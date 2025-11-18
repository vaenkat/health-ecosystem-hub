"""
Validation utilities for Health Ecosystem Hub Backend
"""

import re
from typing import Optional, Any
from datetime import datetime, date
from app.utils.exceptions import ValidationError


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common phone number formatting characters
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's all digits and reasonable length
    return clean_phone.isdigit() and 7 <= len(clean_phone) <= 15


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength"""
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 100:
        return False, "Password must be less than 100 characters long"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"|,.<>/?]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak patterns
    weak_patterns = [
        r'123', r'password', r'qwerty', r'abc', r'admin',
        r'letmein', r'welcome', r'login'
    ]
    
    for pattern in weak_patterns:
        if re.search(pattern, password.lower()):
            return False, f"Password contains common weak pattern: {pattern}"
    
    return True, None


def validate_name(name: str, field_name: str = "Name") -> tuple[bool, Optional[str]]:
    """Validate person name"""
    if not name or not isinstance(name, str):
        return False, f"{field_name} is required"
    
    if len(name.strip()) < 2:
        return False, f"{field_name} must be at least 2 characters long"
    
    if len(name) > 100:
        return False, f"{field_name} must be less than 100 characters long"
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
    
    return True, None


def validate_date_of_birth(dob: date) -> tuple[bool, Optional[str]]:
    """Validate date of birth"""
    if not isinstance(dob, date):
        return False, "Invalid date format"
    
    today = date.today()
    min_date = today.replace(year=today.year - 120)  # 120 years ago
    
    if dob > today:
        return False, "Date of birth cannot be in the future"
    
    if dob < min_date:
        return False, "Date of birth cannot be more than 120 years ago"
    
    return True, None


def validate_blood_type(blood_type: str) -> tuple[bool, Optional[str]]:
    """Validate blood type"""
    if not blood_type:
        return True, None  # Optional field
    
    valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    if blood_type not in valid_types:
        return False, f"Invalid blood type. Must be one of: {', '.join(valid_types)}"
    
    return True, None


def validate_medical_license(license_number: str) -> tuple[bool, Optional[str]]:
    """Validate medical license number"""
    if not license_number or not isinstance(license_number, str):
        return False, "License number is required"
    
    if len(license_number.strip()) < 5:
        return False, "License number must be at least 5 characters long"
    
    if len(license_number) > 50:
        return False, "License number must be less than 50 characters long"
    
    # Check for alphanumeric characters and common separators
    if not re.match(r'^[a-zA-Z0-9\s\-]+$', license_number):
        return False, "License number can only contain letters, numbers, spaces, and hyphens"
    
    return True, None


def validate_quantity(quantity: Any, field_name: str = "Quantity") -> tuple[bool, Optional[str]]:
    """Validate quantity field"""
    try:
        qty = float(quantity)
        
        if qty < 0:
            return False, f"{field_name} cannot be negative"
        
        if qty > 999999:
            return False, f"{field_name} cannot be greater than 999,999"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"


def validate_price(price: Any, field_name: str = "Price") -> tuple[bool, Optional[str]]:
    """Validate price field"""
    try:
        price_float = float(price)
        
        if price_float < 0:
            return False, f"{field_name} cannot be negative"
        
        if price_float > 999999.99:
            return False, f"{field_name} cannot be greater than 999,999.99"
        
        # Check for reasonable decimal places (max 2)
        if isinstance(price, str) and '.' in str(price):
            decimal_places = len(str(price).split('.')[1])
            if decimal_places > 2:
                return False, f"{field_name} cannot have more than 2 decimal places"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"


def validate_medication_name(name: str) -> tuple[bool, Optional[str]]:
    """Validate medication name"""
    if not name or not isinstance(name, str):
        return False, "Medication name is required"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Medication name must be at least 2 characters long"
    
    if len(name) > 200:
        return False, "Medication name must be less than 200 characters long"
    
    # Check for valid characters (letters, numbers, spaces, hyphens)
    if not re.match(r"^[a-zA-Z0-9\s\-]+$", name):
        return False, "Medication name can only contain letters, numbers, spaces, and hyphens"
    
    return True, None


def validate_dosage(dosage: str) -> tuple[bool, Optional[str]]:
    """Validate dosage string"""
    if not dosage or not isinstance(dosage, str):
        return False, "Dosage is required"
    
    dosage = dosage.strip()
    
    if len(dosage) < 1:
        return False, "Dosage cannot be empty"
    
    if len(dosage) > 100:
        return False, "Dosage must be less than 100 characters long"
    
    # Basic dosage pattern (numbers, units, common abbreviations)
    if not re.match(r'^[0-9]+\s*(mg|g|ml|mcg|ug|tablet|capsule|pill|dose|tsp|tbsp)?$', dosage.lower()):
        return False, "Dosage format is invalid. Example: 500mg, 1 tablet, 2 tsp"
    
    return True, None


def validate_frequency(frequency: str) -> tuple[bool, Optional[str]]:
    """Validate frequency string"""
    if not frequency or not isinstance(frequency, str):
        return False, "Frequency is required"
    
    frequency = frequency.strip()
    
    if len(frequency) < 2:
        return False, "Frequency cannot be empty"
    
    if len(frequency) > 100:
        return False, "Frequency must be less than 100 characters long"
    
    # Common frequency patterns
    valid_patterns = [
        r'daily', r'once daily', r'qd', r'bid', r'twice daily', r'tid', r'qid',
        r'every \d+ hours?', r'as needed', r'prn', r'weekly', r'monthly'
    ]
    
    frequency_lower = frequency.lower()
    for pattern in valid_patterns:
        if re.search(pattern, frequency_lower):
            return True, None
    
    return False, "Invalid frequency format. Examples: twice daily, every 8 hours, as needed"


def validate_allergies(allergies: list) -> tuple[bool, Optional[str]]:
    """Validate allergies list"""
    if not isinstance(allergies, list):
        return False, "Allergies must be a list"
    
    if len(allergies) > 50:
        return False, "Cannot have more than 50 allergies"
    
    for allergy in allergies:
        if not isinstance(allergy, str):
            return False, "Each allergy must be a string"
        
        allergy = allergy.strip()
        if len(allergy) < 2:
            return False, "Each allergy must be at least 2 characters long"
        
        if len(allergy) > 100:
            return False, "Each allergy must be less than 100 characters long"
    
    return True, None


def validate_address(address: str) -> tuple[bool, Optional[str]]:
    """Validate address"""
    if not address or not isinstance(address, str):
        return False, "Address is required"
    
    address = address.strip()
    
    if len(address) < 5:
        return False, "Address must be at least 5 characters long"
    
    if len(address) > 500:
        return False, "Address must be less than 500 characters long"
    
    # Check for valid characters (letters, numbers, spaces, common punctuation)
    if not re.match(r"^[a-zA-Z0-9\s\-\.,#]+$", address):
        return False, "Address contains invalid characters"
    
    return True, None


def validate_uuid(uuid_string: str) -> tuple[bool, Optional[str]]:
    """Validate UUID string"""
    if not uuid_string or not isinstance(uuid_string, str):
        return False, "UUID is required"
    
    # UUID v4 pattern
    uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    
    if not re.match(uuid_pattern, uuid_string):
        return False, "Invalid UUID format"
    
    return True, None


def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, Optional[str]]:
    """Validate that all required fields are present"""
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == '':
            return False, f"Required field '{field}' is missing or empty"
    
    return True, None


def validate_field_lengths(data: dict, field_limits: dict) -> tuple[bool, Optional[str]]:
    """Validate field length limits"""
    for field, max_length in field_limits.items():
        if field in data and data[field] and len(str(data[field])) > max_length:
            return False, f"Field '{field}' exceeds maximum length of {max_length} characters"
    
    return True, None


def validate_enum_field(value: str, valid_values: list, field_name: str = "Field") -> tuple[bool, Optional[str]]:
    """Validate enum field"""
    if not value or value not in valid_values:
        return False, f"{field_name} must be one of: {', '.join(valid_values)}"
    
    return True, None


def sanitize_string(text: str, max_length: int = None) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Remove extra whitespace
    sanitized = ' '.join(sanitized.split())
    
    # Trim to max length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_date_range(start_date: date, end_date: date) -> tuple[bool, Optional[str]]:
    """Validate date range"""
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        return False, "Invalid date format"
    
    if start_date >= end_date:
        return False, "Start date must be before end date"
    
    return True, None


def validate_future_date(date_to_check: date) -> tuple[bool, Optional[str]]:
    """Validate that date is not in the distant future"""
    if not isinstance(date_to_check, date):
        return False, "Invalid date format"
    
    today = date.today()
    max_future = today.replace(year=today.year + 10)  # 10 years in future
    
    if date_to_check > max_future:
        return False, "Date cannot be more than 10 years in the future"
    
    return True, None
