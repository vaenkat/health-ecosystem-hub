"""
Appointment management schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status enumeration"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no-show"
    RESCHEDULED = "rescheduled"


class AppointmentType(str, Enum):
    """Appointment type enumeration"""
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    SURGERY = "surgery"
    LAB_TEST = "lab_test"
    IMAGING = "imaging"
    VACCINATION = "vaccination"
    CHECKUP = "checkup"
    THERAPY = "therapy"


class AppointmentCreate(BaseModel):
    """Appointment creation schema"""
    patient_id: str = Field(..., description="Patient ID")
    staff_id: Optional[str] = Field(None, description="Healthcare staff ID")
    appointment_date: datetime = Field(..., description="Appointment date and time")
    department: str = Field(..., description="Department name")
    appointment_type: AppointmentType = Field(AppointmentType.CONSULTATION, description="Type of appointment")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for appointment")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    duration_minutes: Optional[int] = Field(30, ge=15, le=480, description="Appointment duration in minutes")
    is_virtual: bool = Field(False, description="Whether appointment is virtual")
    virtual_meeting_link: Optional[str] = Field(None, description="Virtual meeting link")
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$", description="Appointment priority")
    
    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        """Validate appointment date is not in the past"""
        if v < datetime.now():
            raise ValueError('Appointment date cannot be in the past')
        return v
    
    @validator('virtual_meeting_link')
    def validate_virtual_link(cls, v, values):
        """Validate virtual meeting link for virtual appointments"""
        if values.get('is_virtual') and not v:
            raise ValueError('Virtual meeting link is required for virtual appointments')
        return v


class AppointmentUpdate(BaseModel):
    """Appointment update schema"""
    staff_id: Optional[str] = None
    appointment_date: Optional[datetime] = None
    department: Optional[str] = None
    appointment_type: Optional[AppointmentType] = None
    status: Optional[AppointmentStatus] = None
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    is_virtual: Optional[bool] = None
    virtual_meeting_link: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    
    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        """Validate appointment date is not in the past"""
        if v and v < datetime.now():
            raise ValueError('Appointment date cannot be in the past')
        return v


class AppointmentResponse(BaseModel):
    """Appointment response schema"""
    id: str
    patient_id: str
    staff_id: Optional[str]
    appointment_date: datetime
    department: str
    appointment_type: AppointmentType
    status: AppointmentStatus
    reason: Optional[str]
    notes: Optional[str]
    duration_minutes: int
    is_virtual: bool
    virtual_meeting_link: Optional[str]
    priority: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Additional fields from joins
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    staff_name: Optional[str] = None
    staff_email: Optional[str] = None
    
    class Config:
        from_attributes = True


class AppointmentSearch(BaseModel):
    """Appointment search parameters"""
    patient_id: Optional[str] = None
    staff_id: Optional[str] = None
    department: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    appointment_type: Optional[AppointmentType] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_virtual: Optional[bool] = None
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    search: Optional[str] = Field(None, description="Search in reason and notes")


class AppointmentAvailability(BaseModel):
    """Appointment availability schema"""
    staff_id: str
    date: date
    available_slots: List[datetime]
    booked_slots: List[datetime]
    working_hours_start: str  # HH:MM format
    working_hours_end: str    # HH:MM format
    break_start: Optional[str] = None
    break_end: Optional[str] = None


class AppointmentReschedule(BaseModel):
    """Appointment reschedule schema"""
    new_appointment_date: datetime = Field(..., description="New appointment date and time")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for rescheduling")
    notify_patient: bool = Field(True, description="Whether to notify patient")
    notify_staff: bool = Field(True, description="Whether to notify staff")
    
    @validator('new_appointment_date')
    def validate_new_appointment_date(cls, v):
        """Validate new appointment date is not in the past"""
        if v < datetime.now():
            raise ValueError('New appointment date cannot be in the past')
        return v


class AppointmentCancel(BaseModel):
    """Appointment cancellation schema"""
    reason: Optional[str] = Field(None, max_length=500, description="Reason for cancellation")
    cancellation_fee_applied: bool = Field(False, description="Whether cancellation fee applies")
    notify_patient: bool = Field(True, description="Whether to notify patient")
    notify_staff: bool = Field(True, description="Whether to notify staff")


class AppointmentReminder(BaseModel):
    """Appointment reminder schema"""
    appointment_id: str
    reminder_type: str = Field(..., pattern="^(email|sms|push|call)$", description="Reminder type")
    reminder_time: datetime = Field(..., description="When to send reminder")
    message: Optional[str] = Field(None, description="Custom reminder message")
    is_sent: bool = Field(False, description="Whether reminder has been sent")
    sent_at: Optional[datetime] = None


class AppointmentFeedback(BaseModel):
    """Appointment feedback schema"""
    appointment_id: str
    patient_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback: Optional[str] = Field(None, max_length=1000, description="Patient feedback")
    wait_time_rating: Optional[int] = Field(None, ge=1, le=5, description="Wait time rating")
    staff_rating: Optional[int] = Field(None, ge=1, le=5, description="Staff rating")
    facility_rating: Optional[int] = Field(None, ge=1, le=5, description="Facility rating")
    would_recommend: Optional[bool] = Field(None, description="Would recommend to others")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AppointmentSummary(BaseModel):
    """Appointment summary for dashboard"""
    total_appointments: int
    scheduled_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    upcoming_appointments: int
    today_appointments: int
    week_appointments: int
    month_appointments: int
    average_wait_time: Optional[int] = None  # in minutes
    no_show_rate: float  # percentage
    cancellation_rate: float  # percentage
    patient_satisfaction: Optional[float] = None  # average rating


class WorkingHours(BaseModel):
    """Staff working hours schema"""
    staff_id: str
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Sunday, 6=Saturday)")
    start_time: str = Field(..., pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Start time HH:MM")
    end_time: str = Field(..., pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="End time HH:MM")
    break_start: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Break start time HH:MM")
    break_end: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Break end time HH:MM")
    is_available: bool = Field(True, description="Whether staff is available on this day")


class AppointmentConflict(BaseModel):
    """Appointment conflict detection schema"""
    staff_id: str
    requested_time: datetime
    duration_minutes: int
    conflicts_with: List[str] = Field(default=[], description="List of conflicting appointment IDs")
    available_alternatives: List[datetime] = Field(default=[], description="Alternative time slots")
