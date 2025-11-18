"""
Prescription management schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date, timezone
from enum import Enum


class PrescriptionStatus(str, Enum):
    """Prescription status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"
    PAUSED = "paused"
    EXPIRED = "expired"


class DosageForm(str, Enum):
    """Dosage form enumeration"""
    TABLET = "tablet"
    CAPSULE = "capsule"
    LIQUID = "liquid"
    INJECTION = "injection"
    CREAM = "cream"
    OINTMENT = "ointment"
    INHALER = "inhaler"
    PATCH = "patch"
    DROPS = "drops"
    SPRAY = "spray"
    SUPPOSITORY = "suppository"


class PrescriptionCreate(BaseModel):
    """Prescription creation schema"""
    patient_id: str = Field(..., description="Patient ID")
    medication_id: str = Field(..., description="Medication ID")
    prescribed_by: Optional[str] = Field(None, description="Prescribing healthcare provider ID")
    dosage: str = Field(..., min_length=1, max_length=100, description="Dosage amount (e.g., 500mg, 10ml)")
    frequency: str = Field(..., min_length=1, max_length=100, description="How often to take (e.g., twice daily, every 8 hours)")
    start_date: date = Field(..., description="When to start taking medication")
    end_date: Optional[date] = Field(None, description="When to stop taking medication")
    instructions: Optional[str] = Field(None, max_length=500, description="Special instructions")
    status: PrescriptionStatus = Field(PrescriptionStatus.ACTIVE, description="Prescription status")
    quantity: Optional[int] = Field(None, ge=1, description="Total quantity prescribed")
    refills_allowed: Optional[int] = Field(0, ge=0, description="Number of refills allowed")
    refills_used: int = Field(0, ge=0, description="Number of refills used")
    pharmacy_notes: Optional[str] = Field(None, max_length=500, description="Notes for pharmacy")
    is_prn: bool = Field(False, description="Whether medication is taken as needed (PRN)")
    prn_indications: Optional[str] = Field(None, max_length=200, description="When to take PRN medication")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date"""
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('refills_used')
    def validate_refills_used(cls, v, values):
        """Validate refills used doesn't exceed refills allowed"""
        if 'refills_allowed' in values and v > values['refills_allowed']:
            raise ValueError('Refills used cannot exceed refills allowed')
        return v
    
    @validator('prn_indications')
    def validate_prn_indications(cls, v, values):
        """Validate PRN indications for PRN medications"""
        if values.get('is_prn') and not v:
            raise ValueError('PRN indications are required for PRN medications')
        return v


class PrescriptionUpdate(BaseModel):
    """Prescription update schema"""
    dosage: Optional[str] = Field(None, min_length=1, max_length=100)
    frequency: Optional[str] = Field(None, min_length=1, max_length=100)
    end_date: Optional[date] = None
    instructions: Optional[str] = Field(None, max_length=500)
    status: Optional[PrescriptionStatus] = None
    quantity: Optional[int] = Field(None, ge=1)
    refills_allowed: Optional[int] = Field(None, ge=0)
    refills_used: Optional[int] = Field(None, ge=0)
    pharmacy_notes: Optional[str] = Field(None, max_length=500)
    is_prn: Optional[bool] = None
    prn_indications: Optional[str] = Field(None, max_length=200)
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date"""
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class PrescriptionResponse(BaseModel):
    """Prescription response schema"""
    id: str
    patient_id: str
    medication_id: str
    prescribed_by: Optional[str]
    dosage: str
    frequency: str
    start_date: date
    end_date: Optional[date]
    instructions: Optional[str]
    status: PrescriptionStatus
    created_at: datetime
    updated_at: Optional[datetime]
    quantity: Optional[int]
    refills_allowed: Optional[int]
    refills_used: int
    pharmacy_notes: Optional[str]
    is_prn: bool
    prn_indications: Optional[str]
    
    # Additional fields from joins
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    medication_name: Optional[str] = None
    medication_description: Optional[str] = None
    prescriber_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PrescriptionSearch(BaseModel):
    """Prescription search parameters"""
    patient_id: Optional[str] = None
    medication_id: Optional[str] = None
    prescribed_by: Optional[str] = None
    status: Optional[PrescriptionStatus] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_prn: Optional[bool] = None
    search: Optional[str] = Field(None, description="Search in dosage, frequency, instructions")


class MedicationCreate(BaseModel):
    """Medication creation schema"""
    name: str = Field(..., min_length=2, max_length=200, description="Medication name")
    description: Optional[str] = Field(None, max_length=1000, description="Medication description")
    dosage_form: Optional[DosageForm] = Field(None, description="Dosage form")
    manufacturer: Optional[str] = Field(None, max_length=200, description="Manufacturer name")
    strength: Optional[str] = Field(None, max_length=50, description="Strength (e.g., 500mg)")
    ndc_code: Optional[str] = Field(None, max_length=20, description="National Drug Code")
    generic_name: Optional[str] = Field(None, max_length=200, description="Generic name")
    brand_names: Optional[List[str]] = Field(default=[], description="Brand names")
    contraindications: Optional[List[str]] = Field(default=[], description="Contraindications")
    side_effects: Optional[List[str]] = Field(default=[], description="Common side effects")
    drug_interactions: Optional[List[str]] = Field(default=[], description="Known drug interactions")
    pregnancy_category: Optional[str] = Field(None, pattern="^[ABCDX]$", description="Pregnancy category")
    controlled_substance: bool = Field(False, description="Whether it's a controlled substance")
    schedule: Optional[str] = Field(None, pattern="^[IIIIIV]$", description="Controlled substance schedule")
    storage_requirements: Optional[str] = Field(None, max_length=200, description="Storage requirements")
    is_active: bool = Field(True, description="Whether medication is active")


class MedicationUpdate(BaseModel):
    """Medication update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    dosage_form: Optional[DosageForm] = None
    manufacturer: Optional[str] = Field(None, max_length=200)
    strength: Optional[str] = Field(None, max_length=50)
    ndc_code: Optional[str] = Field(None, max_length=20)
    generic_name: Optional[str] = Field(None, max_length=200)
    brand_names: Optional[List[str]] = None
    contraindications: Optional[List[str]] = None
    side_effects: Optional[List[str]] = None
    drug_interactions: Optional[List[str]] = None
    pregnancy_category: Optional[str] = Field(None, pattern="^[ABCDX]$")
    controlled_substance: Optional[bool] = None
    schedule: Optional[str] = Field(None, pattern="^[IIIIIV]$")
    storage_requirements: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class MedicationResponse(BaseModel):
    """Medication response schema"""
    id: str
    name: str
    description: Optional[str]
    dosage_form: Optional[DosageForm]
    manufacturer: Optional[str]
    created_at: datetime
    strength: Optional[str]
    ndc_code: Optional[str]
    generic_name: Optional[str]
    brand_names: Optional[List[str]]
    contraindications: Optional[List[str]]
    side_effects: Optional[List[str]]
    drug_interactions: Optional[List[str]]
    pregnancy_category: Optional[str]
    controlled_substance: bool
    schedule: Optional[str]
    storage_requirements: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class PrescriptionRefill(BaseModel):
    """Prescription refill schema"""
    prescription_id: str
    refill_requested_by: str = Field(..., description="Who requested the refill")
    refill_requested_at: datetime = Field(default_factory=datetime.utcnow)
    pharmacy_id: Optional[str] = Field(None, description="Pharmacy processing the refill")
    notes: Optional[str] = Field(None, max_length=500, description="Refill notes")
    is_approved: Optional[bool] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    denial_reason: Optional[str] = Field(None, max_length=500)
    is_dispensed: bool = Field(False, description="Whether refill has been dispensed")
    dispensed_at: Optional[datetime] = None
    dispensed_by: Optional[str] = None


class PrescriptionInteraction(BaseModel):
    """Drug interaction check schema"""
    prescription_id: str
    medication_id: str
    interacting_medication_id: str
    interaction_type: str = Field(..., description="Type of interaction")
    severity: str = Field(..., pattern="^(minor|moderate|major|contraindicated)$", description="Interaction severity")
    description: str = Field(..., description="Interaction description")
    recommendation: Optional[str] = Field(None, description="Recommendation for managing interaction")
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class PrescriptionAdherence(BaseModel):
    """Prescription adherence tracking schema"""
    prescription_id: str
    patient_id: str
    date: date = Field(..., description="Date of adherence record")
    doses_scheduled: int = Field(..., ge=0, description="Number of doses scheduled for the day")
    doses_taken: int = Field(..., ge=0, description="Number of doses actually taken")
    adherence_percentage: float = Field(..., ge=0, le=100, description="Adherence percentage")
    notes: Optional[str] = Field(None, max_length=500, description="Notes about adherence")
    recorded_by: Optional[str] = None  # Could be patient or caregiver
    # NEW, MODERN FIX
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PrescriptionSummary(BaseModel):
    """Prescription summary for dashboard"""
    total_prescriptions: int
    active_prescriptions: int
    expired_prescriptions: int
    prescriptions_expiring_this_week: int
    refills_needed: int
    adherence_rate: Optional[float] = None
    common_medications: List[dict] = Field(default=[], description="Most prescribed medications")
    patients_with_active_prescriptions: int
    controlled_substance_prescriptions: int


class MedicationSearch(BaseModel):
    """Medication search parameters"""
    name: Optional[str] = Field(None, description="Search by medication name")
    generic_name: Optional[str] = None
    manufacturer: Optional[str] = None
    dosage_form: Optional[DosageForm] = None
    controlled_substance: Optional[bool] = None
    is_active: Optional[bool] = Field(True, description="Filter by active status")
    ndc_code: Optional[str] = None
    search: Optional[str] = Field(None, description="General search term")


class DrugInteractionCheck(BaseModel):
    """Drug interaction check request schema"""
    medication_ids: List[str] = Field(..., min_items=2, description="List of medication IDs to check for interactions")
    patient_id: Optional[str] = Field(None, description="Patient ID for context")
    include_allergies: bool = Field(True, description="Include allergy interactions")
    include_conditions: bool = Field(True, description="Include condition-based interactions")


class DrugInteractionResult(BaseModel):
    """Drug interaction check result schema"""
    has_interactions: bool
    interactions: List[PrescriptionInteraction]
    severity_summary: dict[str, int] = Field(default={}, description="Count of interactions by severity")
    recommendations: List[str] = Field(default=[], description="General recommendations")
    checked_at: datetime = Field(default_factory=datetime.utcnow)
