"""
Configuration settings for the Health Ecosystem Hub Backend
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # --- ADD ALL THESE ---
    smtp_host: str
    smtp_port: int
    smtp_user: str  # Or you can just use str
    smtp_password: str
    email_from: str # Or you can just use str

    max_file_size: int
    upload_dir: str

    requests_per_minute: int
    burst_size: int

    pharmacy_api_key: str
    lab_api_key: str
    
    # Application
    app_name: str = "Health Ecosystem Hub Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: Optional[str] = None
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: list[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "https://your-production-domain.com"
    ]
    
    # Redis (for caching and real-time features)
    redis_url: str = "redis://localhost:6379"
    
    # Database
    database_url: Optional[str] = None
    
    # WebSocket
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Validate required settings
required_settings = ["supabase_url", "supabase_key", "secret_key"]
for setting in required_settings:
    if not getattr(settings, setting):
        raise ValueError(f"Required setting '{setting}' is missing")

# Print configuration (without sensitive data)
if settings.debug:
    print("=== Health Ecosystem Hub Backend Configuration ===")
    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.app_version}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Supabase URL: {settings.supabase_url}")
    print(f"Server: {settings.host}:{settings.port}")
    print("================================================")
