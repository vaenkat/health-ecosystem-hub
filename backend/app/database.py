"""
Database connection and configuration for Supabase integration
"""

from supabase import create_client, Client
from app.config import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase client wrapper with enhanced functionality"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.service_client: Optional[Client] = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Supabase clients"""
        try:
            # Regular client (uses public key)
            self.client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            
            # Service client (uses service role key for admin operations)
            if settings.supabase_service_key:
                self.service_client = create_client(
                    settings.supabase_url,
                    settings.supabase_service_key
                )
            else:
                logger.warning("Service role key not provided, admin operations will be limited")
                
            logger.info("Supabase clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase clients: {str(e)}")
            raise
    
    def get_client(self, use_service_role: bool = False) -> Client:
        """Get appropriate Supabase client"""
        if use_service_role and self.service_client:
            return self.service_client
        elif self.client:
            return self.client
        else:
            raise RuntimeError("Supabase client not initialized")
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            client = self.get_client()
            response = client.table('profiles').select('count').execute()
            return response.data is not None
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    async def execute_query(
        self, 
        table: str, 
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute database query with error handling"""
        try:
            client = self.get_client(kwargs.pop('use_service_role', False))
            query = getattr(client.table(table), operation)
            result = query(**kwargs).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data) if result.data else 0
            }
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }


# Create global Supabase client instance
supabase_client = SupabaseClient()


# Database helper functions
async def get_table_data(
    table: str,
    select: str = "*",
    filters: Optional[Dict[str, Any]] = None,
    use_service_role: bool = False
) -> Dict[str, Any]:
    """Get data from a table with optional filters"""
    try:
        client = supabase_client.get_client(use_service_role)
        query = client.table(table).select(select)
        
        if filters:
            for column, value in filters.items():
                if isinstance(value, list):
                    query = query.in_(column, value)
                elif isinstance(value, dict) and 'operator' in value:
                    operator = value['operator']
                    query = getattr(query, operator)(column, value['value'])
                else:
                    query = query.eq(column, value)
        
        result = query.execute()
        
        return {
            "success": True,
            "data": result.data,
            "count": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get data from {table}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": []
        }


async def insert_table_data(
    table: str,
    data: Dict[str, Any] | list[Dict[str, Any]],
    use_service_role: bool = False
) -> Dict[str, Any]:
    """Insert data into a table"""
    try:
        client = supabase_client.get_client(use_service_role)
        result = client.table(table).insert(data).execute()
        
        return {
            "success": True,
            "data": result.data,
            "count": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to insert data into {table}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


async def update_table_data(
    table: str,
    data: Dict[str, Any],
    filters: Dict[str, Any],
    use_service_role: bool = False
) -> Dict[str, Any]:
    """Update data in a table"""
    try:
        client = supabase_client.get_client(use_service_role)
        query = client.table(table).update(data)
        
        for column, value in filters.items():
            query = query.eq(column, value)
        
        result = query.execute()
        
        return {
            "success": True,
            "data": result.data,
            "count": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to update data in {table}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


async def delete_table_data(
    table: str,
    filters: Dict[str, Any],
    use_service_role: bool = False
) -> Dict[str, Any]:
    """Delete data from a table"""
    try:
        client = supabase_client.get_client(use_service_role)
        query = client.table(table).delete()
        
        for column, value in filters.items():
            query = query.eq(column, value)
        
        result = query.execute()
        
        return {
            "success": True,
            "data": result.data,
            "count": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to delete data from {table}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


# Database initialization
async def init_database():
    """Initialize database connection and run health checks"""
    try:
        # Test connection
        connection_ok = await supabase_client.test_connection()
        if not connection_ok:
            raise RuntimeError("Database connection failed")
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False
