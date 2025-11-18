"""
Inventory management schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class InventoryStatus(str, Enum):
    """Inventory status enumeration"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    EXPIRED = "expired"
    RECALLED = "recalled"


class TransactionType(str, Enum):
    """Inventory transaction type enumeration"""
    STOCK_IN = "stock_in"
    STOCK_OUT = "stock_out"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"
    RETURN = "return"
    EXPIRED = "expired"
    DAMAGED = "damaged"


class InventoryCreate(BaseModel):
    """Inventory creation schema"""
    medication_id: str = Field(..., description="Medication ID")
    quantity: int = Field(..., ge=0, description="Current quantity in stock")
    reorder_level: int = Field(..., ge=0, description="Reorder level (when to reorder)")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="Unit price")
    batch_number: Optional[str] = Field(None, max_length=50, description="Batch number")
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    location: Optional[str] = Field(None, max_length=100, description="Storage location")
    supplier: Optional[str] = Field(None, max_length=200, description="Supplier name")
    storage_conditions: Optional[str] = Field(None, max_length=500, description="Special storage requirements")
    minimum_quantity: int = Field(0, ge=0, description="Minimum quantity to maintain")
    maximum_quantity: Optional[int] = Field(None, ge=0, description="Maximum quantity to store")
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v):
        """Validate expiry date is not in the past"""
        if v and v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v
    
    @validator('maximum_quantity')
    def validate_max_quantity(cls, v, values):
        """Validate maximum quantity is greater than minimum"""
        if v and 'minimum_quantity' in values and v <= values['minimum_quantity']:
            raise ValueError('Maximum quantity must be greater than minimum quantity')
        return v


class InventoryUpdate(BaseModel):
    """Inventory update schema"""
    quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    batch_number: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=100)
    supplier: Optional[str] = Field(None, max_length=200)
    storage_conditions: Optional[str] = Field(None, max_length=500)
    minimum_quantity: Optional[int] = Field(None, ge=0)
    maximum_quantity: Optional[int] = Field(None, ge=0)
    status: Optional[InventoryStatus] = None
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v):
        """Validate expiry date is not in the past"""
        if v and v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v


class InventoryResponse(BaseModel):
    """Inventory response schema"""
    id: str
    medication_id: str
    quantity: int
    reorder_level: int
    unit_price: Optional[Decimal]
    batch_number: Optional[str]
    expiry_date: Optional[date]
    location: Optional[str]
    supplier: Optional[str]
    storage_conditions: Optional[str]
    minimum_quantity: int
    maximum_quantity: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Additional fields from joins
    medication_name: Optional[str] = None
    medication_description: Optional[str] = None
    dosage_form: Optional[str] = None
    manufacturer: Optional[str] = None
    status: Optional[str] = None  # Calculated status based on quantity and expiry
    
    class Config:
        from_attributes = True


class InventorySearch(BaseModel):
    """Inventory search parameters"""
    medication_id: Optional[str] = None
    medication_name: Optional[str] = None
    supplier: Optional[str] = None
    location: Optional[str] = None
    batch_number: Optional[str] = None
    status: Optional[InventoryStatus] = None
    expiry_date_from: Optional[date] = None
    expiry_date_to: Optional[date] = None
    low_stock_only: bool = Field(False, description="Filter only low stock items")
    expired_only: bool = Field(False, description="Filter only expired items")
    search: Optional[str] = Field(None, description="Search in medication name, batch number, supplier")


class InventoryTransaction(BaseModel):
    """Inventory transaction schema"""
    inventory_id: str = Field(..., description="Inventory item ID")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    quantity_change: int = Field(..., description="Quantity change (positive for stock in, negative for stock out)")
    reference_id: Optional[str] = Field(None, description="Reference to order, prescription, etc.")
    reference_type: Optional[str] = Field(None, description="Type of reference (order, prescription, etc.)")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for transaction")
    performed_by: str = Field(..., description="Who performed the transaction")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    old_quantity: int = Field(..., ge=0, description="Quantity before transaction")
    new_quantity: int = Field(..., ge=0, description="Quantity after transaction")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Unit cost for stock in transactions")
    total_cost: Optional[Decimal] = Field(None, ge=0, description="Total cost for stock in transactions")


class InventoryTransactionResponse(BaseModel):
    """Inventory transaction response schema"""
    id: str
    inventory_id: str
    transaction_type: TransactionType
    quantity_change: int
    reference_id: Optional[str]
    reference_type: Optional[str]
    reason: Optional[str]
    performed_by: str
    notes: Optional[str]
    transaction_date: datetime
    old_quantity: int
    new_quantity: int
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    
    # Additional fields from joins
    medication_name: Optional[str] = None
    performed_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    """Stock adjustment schema"""
    inventory_id: str = Field(..., description="Inventory item ID")
    adjustment_type: str = Field(..., pattern="^(increase|decrease|set)$", description="Type of adjustment")
    quantity: int = Field(..., description="Adjustment quantity")
    reason: str = Field(..., max_length=500, description="Reason for adjustment")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    performed_by: str = Field(..., description="Who performed the adjustment")
    adjustment_date: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('quantity')
    def validate_quantity(cls, v, values):
        """Validate quantity based on adjustment type"""
        if values.get('adjustment_type') == 'decrease' and v < 0:
            raise ValueError('Quantity must be positive for decrease adjustments')
        elif values.get('adjustment_type') == 'increase' and v < 0:
            raise ValueError('Quantity must be positive for increase adjustments')
        elif values.get('adjustment_type') == 'set' and v < 0:
            raise ValueError('Quantity must be non-negative for set adjustments')
        return v


class StockTransfer(BaseModel):
    """Stock transfer schema"""
    from_inventory_id: str = Field(..., description="Source inventory ID")
    to_inventory_id: str = Field(..., description="Destination inventory ID")
    quantity: int = Field(..., ge=1, description="Quantity to transfer")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for transfer")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    transferred_by: str = Field(..., description="Who performed the transfer")
    transfer_date: datetime = Field(default_factory=datetime.utcnow)
    approved_by: Optional[str] = Field(None, description="Who approved the transfer")
    approved_at: Optional[datetime] = None


class InventoryAlert(BaseModel):
    """Inventory alert schema"""
    inventory_id: str = Field(..., description="Inventory item ID")
    alert_type: str = Field(..., pattern="^(low_stock|out_of_stock|expiring_soon|expired|recall)$", description="Type of alert")
    message: str = Field(..., max_length=1000, description="Alert message")
    severity: str = Field(..., pattern="^(low|medium|high|critical)$", description="Alert severity")
    threshold_value: Optional[int] = Field(None, description="Threshold that triggered alert")
    current_value: Optional[int] = Field(None, description="Current value")
    days_until_expiry: Optional[int] = Field(None, description="Days until expiry (for expiry alerts)")
    is_resolved: bool = Field(False, description="Whether alert has been resolved")
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryReport(BaseModel):
    """Inventory report schema"""
    report_type: str = Field(..., pattern="^(stock_level|expiry_report|usage_report|valuation_report)$", description="Type of report")
    date_from: Optional[date] = Field(None, description="Report start date")
    date_to: Optional[date] = Field(None, description="Report end date")
    medication_ids: Optional[List[str]] = Field(None, description="Specific medications to include")
    include_zero_stock: bool = Field(False, description="Include items with zero stock")
    generated_by: str = Field(..., description="Who generated the report")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    parameters: Optional[dict] = Field(default={}, description="Additional report parameters")


class InventorySummary(BaseModel):
    """Inventory summary for dashboard"""
    total_items: int
    total_value: Decimal
    low_stock_items: int
    out_of_stock_items: int
    expiring_items: int  # Expiring within 30 days
    expired_items: int
    items_below_reorder_level: int
    total_transactions_today: int
    stock_out_rate: float  # Percentage
    most_used_medications: List[dict] = Field(default=[], description="Most used medications")
    suppliers_count: int
    locations_count: int


class Supplier(BaseModel):
    """Supplier schema"""
    name: str = Field(..., min_length=2, max_length=200, description="Supplier name")
    contact_person: Optional[str] = Field(None, max_length=100, description="Contact person")
    email: Optional[str] = Field(None, max_length=200, description="Supplier email")
    phone: Optional[str] = Field(None, max_length=20, description="Supplier phone")
    address: Optional[str] = Field(None, max_length=500, description="Supplier address")
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax identification number")
    license_number: Optional[str] = Field(None, max_length=50, description="Business license number")
    payment_terms: Optional[str] = Field(None, max_length=200, description="Payment terms")
    lead_time_days: Optional[int] = Field(None, ge=0, description="Average lead time in days")
    minimum_order: Optional[Decimal] = Field(None, ge=0, description="Minimum order amount")
    is_active: bool = Field(True, description="Whether supplier is active")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


class PurchaseOrder(BaseModel):
    """Purchase order schema"""
    supplier_id: str = Field(..., description="Supplier ID")
    order_number: str = Field(..., max_length=50, description="Purchase order number")
    order_date: date = Field(..., description="Order date")
    expected_delivery_date: date = Field(..., description="Expected delivery date")
    items: List[dict] = Field(..., description="List of ordered items")
    total_amount: Decimal = Field(..., ge=0, description="Total order amount")
    status: str = Field("pending", pattern="^(pending|confirmed|shipped|delivered|cancelled)$", description="Order status")
    notes: Optional[str] = Field(None, max_length=1000, description="Order notes")
    ordered_by: str = Field(..., description="Who placed the order")
    approved_by: Optional[str] = Field(None, description="Who approved the order")
    approved_at: Optional[datetime] = None
    
    @validator('expected_delivery_date')
    def validate_delivery_date(cls, v, values):
        """Validate delivery date is after order date"""
        if 'order_date' in values and v <= values['order_date']:
            raise ValueError('Expected delivery date must be after order date')
        return v


class InventoryForecast(BaseModel):
    """Inventory forecast schema"""
    inventory_id: str = Field(..., description="Inventory item ID")
    forecast_period_days: int = Field(..., ge=1, le=365, description="Forecast period in days")
    predicted_usage: int = Field(..., ge=0, description="Predicted usage for period")
    recommended_order_quantity: Optional[int] = Field(None, ge=0, description="Recommended order quantity")
    stock_out_risk: str = Field(..., pattern="^(low|medium|high)$", description="Risk of stock out")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence level of forecast")
    forecast_date: datetime = Field(default_factory=datetime.utcnow)
    factors_considered: List[str] = Field(default=[], description="Factors considered in forecast")


class ExpiryTracking(BaseModel):
    """Expiry tracking schema"""
    inventory_id: str = Field(..., description="Inventory item ID")
    expiry_date: date = Field(..., description="Expiry date")
    days_until_expiry: int = Field(..., description="Days until expiry")
    batch_number: Optional[str] = Field(None, max_length=50, description="Batch number")
    quantity: int = Field(..., ge=0, description="Quantity expiring")
    action_required: str = Field(..., pattern="^(none|monitor|return|dispose)$", description="Action required")
    notification_sent: bool = Field(False, description="Whether expiry notification has been sent")
    last_notified_at: Optional[datetime] = None
