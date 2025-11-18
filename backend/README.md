# Health Ecosystem Hub Backend

A comprehensive FastAPI backend for healthcare management system with real-time capabilities.

## 🚀 Features

### Core Functionality
- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Patient Management**: Complete patient profiles and medical records
- **Appointment Scheduling**: Healthcare appointment management with reminders
- **Prescription Management**: Digital prescriptions with drug interaction checking
- **Inventory Management**: Real-time pharmacy stock tracking and alerts
- **Order Processing**: Hospital-pharmacy order workflow management
- **Real-time Communication**: WebSocket-based notifications and updates
- **Security**: Rate limiting, request logging, and input validation
- **Data Validation**: Comprehensive input validation and sanitization

### 🏗 Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT tokens with role-based authorization
- **Real-time**: WebSocket connections
- **Containerization**: Docker with multi-stage builds
- **Security**: CORS, rate limiting, SQL injection protection
- **Validation**: Pydantic schemas with custom validators

### 📁 Project Structure

```
health-ecosystem-hub/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Supabase database integration
│   │   ├── api/                         # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Authentication endpoints
│   │   │   ├── patients.py           # Patient management endpoints (TODO)
│   │   │   ├── appointments.py       # Appointment endpoints (TODO)
│   │   │   ├── prescriptions.py      # Prescription endpoints (TODO)
│   │   │   ├── inventory.py          # Inventory endpoints (TODO)
│   │   │   └── orders.py             # Order endpoints (TODO)
│   │   ├── middleware/                    # Custom middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Authentication middleware
│   │   │   ├── logging.py            # Request/response logging
│   │   │   └── rate_limit.py        # Rate limiting
│   │   ├── schemas/                       # Pydantic data models
│   │   │   ├── __init__.py
│   │   ├── common.py              # Common schemas
│   │   │   ├── auth.py               # Authentication schemas
│   │   │   ├── patients.py           # Patient schemas
│   │   │   ├── appointments.py       # Appointment schemas
│   │   │   ├── prescriptions.py      # Prescription schemas
│   │   │   ├── inventory.py          # Inventory schemas
│   │   │   └── orders.py             # Order schemas
│   │   └── utils/                        # Utility functions
│   │       ├── __init__.py
│   │       ├── exceptions.py          # Custom exceptions
│   │       ├── validators.py         # Input validation
│   │       ├── websocket.py          # Real-time WebSocket management
│   │       └── helpers.py             # Helper functions
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
└── README.md
```

## 🔧 Setup Instructions

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Supabase account and project

### Environment Setup

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Update environment variables**:
   ```bash
   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_role_key
   
   # Application Configuration
   APP_NAME=Health Ecosystem Hub Backend
   APP_VERSION=1.0.0
   DEBUG=true
   HOST=0.0.0.0
   PORT=8000
   
   # Security
   SECRET_KEY=your_secret_key_here_at_least_32_characters_long
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # CORS
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   
   # Database (optional, if not using Supabase)
   DATABASE_URL=postgresql://username:password@localhost:5432/health_ecosystem
   ```

### Running the Application

#### Development Mode
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main
```

#### Docker Mode
```bash
# Build the image
docker build -t health-ecosystem-backend .

# Run with Docker Compose
docker-compose up -d

# Or run standalone container
docker run -p 8000:8000 -e SUPABASE_URL=your_url \
  -e SUPABASE_KEY=your_key \
  -e SECRET_KEY=your_secret \
  health-ecosystem-backend
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

### 🔐 API Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/profile` - Update user profile

#### Patients (TODO)
- `GET /api/v1/patients` - List patients
- `POST /api/v1/patients` - Create patient
- `GET /api/v1/patients/{id}` - Get patient details
- `PUT /api/v1/patients/{id}` - Update patient

#### Appointments (TODO)
- `GET /api/v1/appointments` - List appointments
- `POST /api/v1/appointments` - Create appointment
- `GET /api/v1/appointments/{id}` - Get appointment details
- `PUT /api/v1/appointments/{id}` - Update appointment

#### Prescriptions (TODO)
- `GET /api/v1/prescriptions` - List prescriptions
- `POST /api/v1/prescriptions` - Create prescription
- `GET /api/v1/prescriptions/{id}` - Get prescription details
- `PUT /api/v1/prescriptions/{id}` - Update prescription

#### Inventory (TODO)
- `GET /api/v1/inventory` - List inventory items
- `POST /api/v1/inventory` - Create inventory item
- `GET /api/v1/inventory/{id}` - Get inventory details
- `PUT /api/v1/inventory/{id}` - Update inventory

#### Orders (TODO)
- `GET /api/v1/orders` - List orders
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders/{id}` - Get order details
- `PUT /api/v1/orders/{id}` - Update order

## 🔌 WebSocket Endpoints

- `WS /ws/{user_id}` - Real-time updates for connected users

### 🛡 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Authorization**: Patient, Hospital Staff, Pharmacy Staff, Admin roles
- **Rate Limiting**: Configurable requests per minute
- **Input Validation**: Comprehensive validation for all inputs
- **SQL Injection Protection**: Parameterized queries
- **CORS Configuration**: Proper cross-origin resource sharing
- **Request Logging**: Detailed logging for security monitoring

### 📊 Monitoring & Health Checks

- **Health Endpoints**: `/health` and `/health/detailed`
- **Structured Logging**: Request/response logging with correlation IDs
- **Performance Metrics**: Request timing and database query monitoring
- **Error Handling**: Comprehensive error responses with proper HTTP status codes

## 🧪 Development Workflow

1. **Local Development**: Use the provided Python environment
2. **Database Migrations**: Supabase handles schema migrations automatically
3. **Testing**: Use the built-in FastAPI testing tools
4. **Code Quality**: Follow PEP 8 and type hints throughout

## 📦 Production Deployment

### Environment Variables Required
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anon key
- `SUPABASE_SERVICE_KEY`: Supabase service role key (recommended)
- `SECRET_KEY`: At least 32 characters for JWT signing

### Docker Configuration
- Multi-stage builds supported
- Health checks included
- Non-root user for security
- Proper signal handling for graceful shutdown

## 🔮 Integration Points

### Frontend Integration
- The backend provides RESTful APIs that work with the existing React frontend
- WebSocket endpoints for real-time updates
- Compatible with the existing Supabase database schema
- JWT tokens for secure frontend authentication

### External Services
- Email integration for password reset (SMTP configuration)
- Pharmacy API integration for inventory management
- Lab API integration for medical records

## 📝 Database Schema

The backend is designed to work with the existing Supabase database schema:

- **Users & Profiles**: User management with role assignment
- **Patients**: Patient medical records and demographics
- **Appointments**: Healthcare appointment scheduling
- **Prescriptions**: Digital prescription management
- **Inventory**: Pharmacy stock tracking and management
- **Orders**: Hospital-pharmacy order processing
- **Lab Reports**: Medical test results and records

## 🚀 Next Steps

1. **Complete API Endpoints**: Implement remaining CRUD operations for patients, appointments, prescriptions, inventory, and orders
2. **Business Logic**: Add service layer for complex business operations
3. **Real-time Features**: Implement WebSocket notifications for appointments, inventory alerts, order updates
4. **Testing**: Add comprehensive unit tests and integration tests
5. **Documentation**: Create detailed API documentation and deployment guides
6. **Monitoring**: Set up application monitoring and alerting

## 📞 Support

For issues and questions:
- Check the application logs for detailed error messages
- Review the API documentation at `/docs` endpoint
- Ensure all environment variables are properly configured
- Verify Supabase connection and permissions

---

**Built with ❤️ for healthcare professionals**
