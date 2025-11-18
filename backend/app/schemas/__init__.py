"""
Pydantic schemas for data validation and serialization
"""

from .auth import *
from .patients import *
from .appointments import *
from .prescriptions import *
from .inventory import *
from .orders import *
from .common import *

__all__ = [
    # Auth schemas
    "LoginRequest",
    "LoginResponse",
    "UserCreate",
    "UserResponse",
    
    # Patient schemas
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    
    # Appointment schemas
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    
    # Prescription schemas
    "PrescriptionCreate",
    "PrescriptionUpdate",
    "PrescriptionResponse",
    
    # Inventory schemas
    "InventoryCreate",
    "InventoryUpdate",
    "InventoryResponse",
    
    # Order schemas
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    
    # Common schemas
    "BaseResponse",
    "ErrorResponse",
    "PaginatedResponse",
]
