"""
API routes package for Health Ecosystem Hub Backend
"""

from . import auth, patients, appointments, prescriptions, inventory, orders

__all__ = [
    "auth",
    "patients", 
    "appointments",
    "prescriptions",
    "inventory",
    "orders"
]
