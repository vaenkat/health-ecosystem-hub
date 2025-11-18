"""
Hospital orders management schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    PARTIALLY_FULFILLED = "partially_fulfilled"


class OrderUrgency(str, Enum):
    """Order urgency enumeration"""
    NORMAL = "normal"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class OrderCreate(BaseModel):
    """Order creation schema"""
    medication_id: str = Field(..., description="Medication ID")
    ordered_by: str = Field(..., description="Who placed the order")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    urgency: OrderUrgency = Field(OrderUrgency.NORMAL, description="Order urgency")
    notes: Optional[str] = Field(None, max_length=1000, description="Order notes")
    patient_id: Optional[str] = Field(None, description="Associated patient ID (if applicable)")
    prescription_id: Optional[str] = Field(None, description="Associated prescription ID (if applicable)")
    department: Optional[str] = Field(None, max_length=100, description="Requesting department")
    needed_by: Optional[datetime] = Field(None, description="When medication is needed by")
    replacement_for: Optional[str] = Field(None, description="Order this replaces (if any)")
    special_instructions: Optional[str] = Field(None, max_length=500, description="Special handling instructions")
    
    @validator('needed_by')
    def validate_needed_by(cls, v):
        """Validate needed by date is not in the past"""
        if v and v < datetime.now():
            raise ValueError('Needed by date cannot be in the past')
        return v


class OrderUpdate(BaseModel):
    """Order update schema"""
    quantity: Optional[int] = Field(None, ge=1)
    urgency: Optional[OrderUrgency] = None
    status: Optional[OrderStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)
    needed_by: Optional[datetime] = None
    special_instructions: Optional[str] = Field(None, max_length=500)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = Field(None, max_length=500)
    fulfilled_by: Optional[str] = None
    fulfilled_at: Optional[datetime] = None
    fulfilled_quantity: Optional[int] = Field(None, ge=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    total_cost: Optional[Decimal] = Field(None, ge=0)
    
    @validator('needed_by')
    def validate_needed_by(cls, v):
        """Validate needed by date is not in the past"""
        if v and v < datetime.now():
            raise ValueError('Needed by date cannot be in the past')
        return v
    
    @validator('fulfilled_quantity')
    def validate_fulfilled_quantity(cls, v, values):
        """Validate fulfilled quantity doesn't exceed ordered quantity"""
        if v and 'quantity' in values and v > values['quantity']:
            raise ValueError('Fulfilled quantity cannot exceed ordered quantity')
        return v


class OrderResponse(BaseModel):
    """Order response schema"""
    id: str
    medication_id: str
    ordered_by: str
    quantity: int
    urgency: OrderUrgency
    status: OrderStatus
    notes: Optional[str]
    patient_id: Optional[str]
    prescription_id: Optional[str]
    department: Optional[str]
    needed_by: Optional[datetime]
    replacement_for: Optional[str]
    special_instructions: Optional[str]
    created_at: datetime
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    fulfilled_by: Optional[str]
    fulfilled_at: Optional[datetime]
    fulfilled_quantity: Optional[int]
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    
    # Additional fields from joins
    medication_name: Optional[str] = None
    medication_description: Optional[str] = None
    ordered_by_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    fulfilled_by_name: Optional[str] = None
    patient_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrderSearch(BaseModel):
    """Order search parameters"""
    medication_id: Optional[str] = None
    ordered_by: Optional[str] = None
    status: Optional[OrderStatus] = None
    urgency: Optional[OrderUrgency] = None
    patient_id: Optional[str] = None
    prescription_id: Optional[str] = None
    department: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    needed_by_from: Optional[date] = None
    needed_by_to: Optional[date] = None
    search: Optional[str] = Field(None, description="Search in notes, special instructions")


class OrderApproval(BaseModel):
    """Order approval schema"""
    order_id: str = Field(..., description="Order ID to approve")
    approved_by: str = Field(..., description="Who is approving the order")
    approved_quantity: Optional[int] = Field(None, ge=1, description="Approved quantity (if different from requested)")
    notes: Optional[str] = Field(None, max_length=500, description="Approval notes")
    estimated_fulfillment_date: Optional[datetime] = Field(None, description="Estimated fulfillment date")
    
    @validator('approved_quantity')
    def validate_approved_quantity(cls, v):
        """Validate approved quantity is positive"""
        if v and v < 1:
            raise ValueError('Approved quantity must be at least 1')
        return v


class OrderRejection(BaseModel):
    """Order rejection schema"""
    order_id: str = Field(..., description="Order ID to reject")
    rejected_by: str = Field(..., description="Who is rejecting the order")
    rejection_reason: str = Field(..., max_length=500, description="Reason for rejection")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional rejection notes")
    suggest_alternative: bool = Field(False, description="Whether to suggest alternative medication")
    alternative_medication_id: Optional[str] = Field(None, description="Alternative medication ID")


class OrderFulfillment(BaseModel):
    """Order fulfillment schema"""
    order_id: str = Field(..., description="Order ID to fulfill")
    fulfilled_by: str = Field(..., description="Who is fulfilling the order")
    fulfilled_quantity: int = Field(..., ge=1, description="Quantity actually fulfilled")
    batch_number: Optional[str] = Field(None, max_length=50, description="Batch number of fulfilled medication")
    expiry_date: Optional[date] = Field(None, description="Expiry date of fulfilled medication")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Unit cost")
    total_cost: Optional[Decimal] = Field(None, ge=0, description="Total cost")
    notes: Optional[str] = Field(None, max_length=1000, description="Fulfillment notes")
    fulfillment_method: str = Field("pickup", pattern="^(pickup|delivery|transfer)$", description="How order is fulfilled")
    delivery_address: Optional[str] = Field(None, max_length=500, description="Delivery address")
    tracking_number: Optional[str] = Field(None, max_length=100, description="Tracking number if delivered")
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v):
        """Validate expiry date is not in the past"""
        if v and v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v


class OrderModification(BaseModel):
    """Order modification schema"""
    order_id: str = Field(..., description="Order ID to modify")
    modified_by: str = Field(..., description="Who is modifying the order")
    modification_reason: str = Field(..., max_length=500, description="Reason for modification")
    new_quantity: Optional[int] = Field(None, ge=1, description="New quantity")
    new_urgency: Optional[OrderUrgency] = None
    new_needed_by: Optional[datetime] = None
    new_notes: Optional[str] = Field(None, max_length=1000)
    new_special_instructions: Optional[str] = Field(None, max_length=500)
    
    @validator('new_needed_by')
    def validate_new_needed_by(cls, v):
        """Validate new needed by date is not in the past"""
        if v and v < datetime.now():
            raise ValueError('New needed by date cannot be in the past')
        return v


class OrderSummary(BaseModel):
    """Order summary for dashboard"""
    total_orders: int
    pending_orders: int
    approved_orders: int
    rejected_orders: int
    fulfilled_orders: int
    cancelled_orders: int
    urgent_orders: int
    emergency_orders: int
    overdue_orders: int
    orders_today: int
    orders_this_week: int
    orders_this_month: int
    average_fulfillment_time: Optional[float] = None  # in hours
    total_value: Optional[Decimal] = None
    top_medications: List[dict] = Field(default=[], description="Most ordered medications")
    top_departments: List[dict] = Field(default=[], description="Top ordering departments")


class OrderBatch(BaseModel):
    """Batch order schema"""
    orders: List[OrderCreate] = Field(..., min_items=1, description="List of orders in batch")
    batch_name: str = Field(..., max_length=100, description="Batch name/identifier")
    ordered_by: str = Field(..., description="Who placed the batch order")
    notes: Optional[str] = Field(None, max_length=1000, description="Batch order notes")
    priority: OrderUrgency = Field(OrderUrgency.NORMAL, description="Overall batch priority")
    needed_by: Optional[datetime] = Field(None, description="When batch is needed by")


class OrderTracking(BaseModel):
    """Order tracking schema"""
    order_id: str = Field(..., description="Order ID")
    status: OrderStatus = Field(..., description="Current status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str = Field(..., description="Who updated the status")
    notes: Optional[str] = Field(None, max_length=500, description="Status update notes")
    location: Optional[str] = Field(None, max_length=200, description="Current location of order")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class OrderAnalytics(BaseModel):
    """Order analytics schema"""
    date_from: date = Field(..., description="Analysis start date")
    date_to: date = Field(..., description="Analysis end date")
    department: Optional[str] = Field(None, description="Filter by department")
    medication_id: Optional[str] = Field(None, description="Filter by medication")
    urgency_filter: Optional[OrderUrgency] = Field(None, description="Filter by urgency")
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        """Validate date range"""
        if 'date_from' in values and v <= values['date_from']:
            raise ValueError('End date must be after start date')
        return v


class OrderAnalyticsResponse(BaseModel):
    """Order analytics response schema"""
    total_orders: int
    total_quantity: int
    total_value: Decimal
    average_order_value: Decimal
    fulfillment_rate: float  # percentage
    average_fulfillment_time_hours: float
    orders_by_status: dict[str, int]
    orders_by_urgency: dict[str, int]
    orders_by_department: List[dict]
    top_medications: List[dict]
    daily_order_trend: List[dict]
    fulfillment_time_trend: List[dict]


class OrderNotification(BaseModel):
    """Order notification schema"""
    order_id: str = Field(..., description="Order ID")
    notification_type: str = Field(..., pattern="^(created|approved|rejected|fulfilled|cancelled|urgent|overdue)$", description="Type of notification")
    recipient_id: str = Field(..., description="Notification recipient ID")
    recipient_role: str = Field(..., description="Recipient role")
    message: str = Field(..., max_length=1000, description="Notification message")
    is_sent: bool = Field(False, description="Whether notification has been sent")
    sent_at: Optional[datetime] = None
    preferred_channel: str = Field("email", pattern="^(email|sms|push|in_app)$", description="Preferred notification channel")


class OrderTemplate(BaseModel):
    """Order template schema"""
    name: str = Field(..., min_length=2, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    medication_id: str = Field(..., description="Default medication ID")
    default_quantity: int = Field(..., ge=1, description="Default quantity")
    default_urgency: OrderUrgency = Field(OrderUrgency.NORMAL, description="Default urgency")
    default_department: Optional[str] = Field(None, max_length=100, description="Default department")
    default_notes: Optional[str] = Field(None, max_length=1000, description="Default notes")
    default_special_instructions: Optional[str] = Field(None, max_length=500, description="Default special instructions")
    created_by: str = Field(..., description="Who created the template")
    is_active: bool = Field(True, description="Whether template is active")
    usage_count: int = Field(0, ge=0, description="How many times template has been used")
    last_used: Optional[datetime] = None


class OrderIntegration(BaseModel):
    """External system integration schema"""
    order_id: str = Field(..., description="Order ID")
    external_system: str = Field(..., max_length=50, description="External system name")
    external_id: str = Field(..., max_length=100, description="External system order ID")
    integration_type: str = Field(..., pattern="^(erp|ems|pharmacy|lab)$", description="Type of integration")
    sync_direction: str = Field(..., pattern="^(inbound|outbound|bidirectional)$", description="Sync direction")
    last_sync: Optional[datetime] = None
    sync_status: str = Field("pending", pattern="^(pending|success|error|retry)$", description="Sync status")
    error_message: Optional[str] = Field(None, max_length=1000, description="Error message if sync failed")
    retry_count: int = Field(0, ge=0, description="Number of retry attempts")
    auto_sync: bool = Field(True, description="Whether to auto-sync changes")
