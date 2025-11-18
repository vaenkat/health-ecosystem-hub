"""
Patient management schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date


class PatientCreate(BaseModel):
    """Patient creation schema"""
    user_id: str = Field(..., description="Associated user ID")
    date_of_birth: Optional[date] = Field(None, description="Patient date of birth")
    blood_type: Optional[str] = Field(None, pattern="^(A|B|AB|O)[+-]$", description="Blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)")
    allergies: Optional[List[str]] = Field(default=[], description="List of allergies")
    emergency_contact: Optional[str] = Field(None, max_length=100, description="Emergency contact name")
    emergency_phone: Optional[str] = Field(None, max_length=20, description="Emergency contact phone")
    medical_history: Optional[List[str]] = Field(default=[], description="Medical history notes")
    current_medications: Optional[List[str]] = Field(default=[], description="Current medications")
    chronic_conditions: Optional[List[str]] = Field(default=[], description="Chronic conditions")
    
    @validator('emergency_phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.replace('-', '').replace(' ', '').replace('+', '').isdigit():
            raise ValueError('Phone number must contain only digits, spaces, hyphens, and plus sign')
        return v


class PatientUpdate(BaseModel):
    """Patient update schema"""
    date_of_birth: Optional[date] = None
    blood_type: Optional[str] = Field(None, pattern="^(A|B|AB|O)[+-]$")
    allergies: Optional[List[str]] = None
    emergency_contact: Optional[str] = Field(None, max_length=100)
    emergency_phone: Optional[str] = Field(None, max_length=20)
    medical_history: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    
    @validator('emergency_phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.replace('-', '').replace(' ', '').replace('+', '').isdigit():
            raise ValueError('Phone number must contain only digits, spaces, hyphens, and plus sign')
        return v


class PatientResponse(BaseModel):
    """Patient response schema"""
    id: str
    user_id: str
    date_of_birth: Optional[date]
    blood_type: Optional[str]
    allergies: Optional[List[str]]
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Additional fields from user profile
    user_email: Optional[str] = None
    user_full_name: Optional[str] = None
    user_phone: Optional[str] = None
    
    class Config:
        from_attributes = True


class PatientProfile(BaseModel):
    """Complete patient profile schema"""
    id: str
    user_id: str
    full_name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    age: Optional[int] = None
    blood_type: Optional[str]
    allergies: Optional[List[str]]
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]
    medical_history: Optional[List[str]]
    current_medications: Optional[List[str]]
    chronic_conditions: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]
    last_visit: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PatientSearch(BaseModel):
    """Patient search parameters"""
    query: Optional[str] = Field(None, description="Search query (name, email, phone)")
    blood_type: Optional[str] = Field(None, pattern="^(A|B|AB|O)[+-]$")
    has_allergies: Optional[bool] = Field(None, description="Filter by allergies presence")
    allergy_type: Optional[str] = Field(None, description="Filter by specific allergy")
    age_min: Optional[int] = Field(None, ge=0, le=150, description="Minimum age")
    age_max: Optional[int] = Field(None, ge=0, le=150, description="Maximum age")
    chronic_condition: Optional[str] = Field(None, description="Filter by chronic condition")


class PatientMedicalRecord(BaseModel):
    """Patient medical record schema"""
    patient_id: str
    record_type: str = Field(..., description="Type of medical record")
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    medications: Optional[List[str]] = None
    notes: Optional[str] = None
    recorded_by: str = Field(..., description="Healthcare provider ID")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    attachments: Optional[List[str]] = Field(default=[], description="File attachments")


class PatientVitalSigns(BaseModel):
    """Patient vital signs schema"""
    patient_id: str
    blood_pressure_systolic: Optional[int] = Field(None, ge=0, le=300)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=0, le=200)
    heart_rate: Optional[int] = Field(None, ge=0, le=300)
    respiratory_rate: Optional[int] = Field(None, ge=0, le=100)
    temperature: Optional[float] = Field(None, ge=20.0, le=45.0)
    oxygen_saturation: Optional[float] = Field(None, ge=0.0, le=100.0)
    weight: Optional[float] = Field(None, ge=0.0, le=500.0)
    height: Optional[float] = Field(None, ge=0.0, le=300.0)
    recorded_by: str = Field(..., description="Healthcare provider ID")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


class PatientAllergy(BaseModel):
    """Patient allergy schema"""
    patient_id: str
    allergen: str = Field(..., description="Allergen name")
    severity: str = Field(..., pattern="^(mild|moderate|severe)$", description="Allergy severity")
    reaction: Optional[str] = Field(None, description="Allergic reaction description")
    onset_date: Optional[date] = Field(None, description="When allergy was first observed")
    diagnosed_by: Optional[str] = Field(None, description="Healthcare provider who diagnosed")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PatientMedication(BaseModel):
    """Patient medication schema"""
    patient_id: str
    medication_name: str = Field(..., description="Medication name")
    dosage: str = Field(..., description="Dosage amount")
    frequency: str = Field(..., description="How often to take")
    route: str = Field(..., description="Administration route (oral, IV, etc.)")
    start_date: date = Field(..., description="When medication was started")
    end_date: Optional[date] = Field(None, description="When medication was stopped")
    prescribed_by: str = Field(..., description="Prescribing healthcare provider")
    reason: Optional[str] = Field(None, description="Reason for medication")
    side_effects: Optional[List[str]] = Field(default=[], description="Known side effects")
    is_active: bool = Field(True, description="Whether medication is currently active")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PatientVisit(BaseModel):
    """Patient visit record schema"""
    patient_id: str
    visit_type: str = Field(..., description="Type of visit (consultation, follow-up, emergency, etc.)")
    department: str = Field(..., description="Department visited")
    healthcare_provider_id: str = Field(..., description="Healthcare provider ID")
    chief_complaint: Optional[str] = Field(None, description="Primary reason for visit")
    diagnosis: Optional[str] = Field(None, description="Diagnosis from visit")
    treatment_plan: Optional[str] = Field(None, description="Treatment plan")
    follow_up_required: bool = Field(False, description="Whether follow-up is needed")
    follow_up_date: Optional[datetime] = Field(None, description="Scheduled follow-up date")
    notes: Optional[str] = Field(None, description="Additional notes")
    visit_date: datetime = Field(default_factory=datetime.utcnow)
    duration_minutes: Optional[int] = Field(None, ge=0, description="Visit duration in minutes")


class PatientSummary(BaseModel):
    """Patient summary for dashboard"""
    patient_id: str
    full_name: str
    age: Optional[int]
    blood_type: Optional[str]
    last_visit: Optional[datetime]
    upcoming_appointments: int = 0
    active_prescriptions: int = 0
    critical_allergies: int = 0
    chronic_conditions: int = 0
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]
