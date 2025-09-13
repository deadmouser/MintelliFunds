"""
Database connection and session management for Financial AI Assistant
"""
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from contextlib import contextmanager
import logging
import os
from typing import Generator, Optional

from ..config import settings
from .models import Base, get_all_models

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and session manager"""
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize database connection"""
        if self._initialized:
            return
        
        try:
            database_url = settings.get_database_url()
            logger.info(f"Connecting to database: {database_url.split('@')[-1] if '@' in database_url else 'SQLite'}")
            
            # Create engine with appropriate settings
            if database_url.startswith("sqlite"):
                # SQLite specific settings
                self.engine = create_engine(
                    database_url,
                    echo=settings.DATABASE_ECHO,
                    connect_args={"check_same_thread": False},
                    poolclass=pool.StaticPool
                )
                
                # Enable foreign keys for SQLite
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.execute("PRAGMA temp_store=memory")
                    cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
                    cursor.close()
                    
            else:
                # PostgreSQL or other database settings
                self.engine = create_engine(
                    database_url,
                    echo=settings.DATABASE_ECHO,
                    pool_size=settings.DATABASE_POOL_SIZE,
                    max_overflow=settings.DATABASE_MAX_OVERFLOW,
                    pool_pre_ping=True,
                    pool_recycle=3600  # Recycle connections after 1 hour
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self._initialized = True
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        if not self._initialized:
            self.initialize()
        
        try:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=self.engine)
            
            # Log created tables
            models = get_all_models()
            table_names = [model.__tablename__ for model in models]
            logger.info(f"Created tables: {', '.join(table_names)}")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        if not self._initialized:
            self.initialize()
        
        try:
            logger.warning("Dropping all database tables...")
            Base.metadata.drop_all(bind=self.engine)
            logger.info("All tables dropped successfully")
            
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        if not self._initialized:
            self.initialize()
        
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """Get database session for dependency injection"""
        if not self._initialized:
            self.initialize()
        
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Check database connection health"""
        if not self._initialized:
            return False
        
        try:
            with self.get_session() as session:
                # Simple query to test connection
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get database connection information"""
        if not self._initialized or not self.engine:
            return {"status": "not_connected"}
        
        try:
            with self.get_session() as session:
                # Get database version and basic info
                if settings.get_database_url().startswith("sqlite"):
                    result = session.execute("SELECT sqlite_version()").scalar()
                    return {
                        "status": "connected",
                        "type": "sqlite",
                        "version": result,
                        "url": settings.get_database_url()
                    }
                else:
                    result = session.execute("SELECT version()").scalar()
                    return {
                        "status": "connected", 
                        "type": "postgresql",
                        "version": result.split()[1] if result else "unknown",
                        "pool_size": settings.DATABASE_POOL_SIZE,
                        "max_overflow": settings.DATABASE_MAX_OVERFLOW
                    }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Global database manager instance
db_manager = DatabaseManager()

# Dependency function for FastAPI
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to get database session"""
    session = db_manager.get_session_sync()
    try:
        yield session
    finally:
        session.close()

# Migration functions
def run_migrations():
    """Run database migrations"""
    logger.info("Running database migrations...")
    
    try:
        # Initialize database if not already done
        db_manager.initialize()
        
        # Create tables
        db_manager.create_tables()
        
        # Run any custom migration scripts
        with db_manager.get_session() as session:
            # Check if we need to populate initial data
            from .models import User
            
            # Check if any users exist
            user_count = session.query(User).count()
            if user_count == 0:
                logger.info("No users found, creating initial admin user...")
                create_initial_admin_user(session)
        
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def create_initial_admin_user(session: Session):
    """Create initial admin user for the system"""
    from .models import User, PrivacySetting
    from ..security.auth import security_manager
    
    try:
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@mintellifunds.com",
            hashed_password=security_manager.hash_password("admin123"),
            full_name="System Administrator",
            is_verified=True,
            is_admin=True
        )
        
        session.add(admin_user)
        session.flush()  # Get the user ID
        
        # Create default privacy settings for admin
        privacy_settings = PrivacySetting(
            user_id=admin_user.id,
            transactions_enabled=True,
            accounts_enabled=True,
            assets_enabled=True,
            liabilities_enabled=True,
            epf_enabled=True,
            credit_score_enabled=True,
            investments_enabled=True,
            spending_trends_enabled=True,
            category_breakdown_enabled=True,
            dashboard_insights_enabled=True
        )
        
        session.add(privacy_settings)
        session.commit()
        
        logger.info(f"Created initial admin user: {admin_user.username}")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create initial admin user: {e}")
        raise

def migrate_json_data():
    """Migrate existing JSON data to database"""
    logger.info("Starting JSON to database migration...")
    
    try:
        from ..services.data_service import DataService
        from .models import User, Account, Transaction, Investment, Asset, Liability
        
        # Load existing JSON data
        data_service = DataService()
        json_data = data_service.load_all_data()
        
        with db_manager.get_session() as session:
            # Get or create a default user for the data
            default_user = session.query(User).filter(User.username == "demo_user").first()
            if not default_user:
                default_user = User(
                    username="demo_user",
                    email="demo@mintellifunds.com",
                    hashed_password=security_manager.hash_password("demo123"),
                    full_name="Demo User",
                    is_verified=True,
                    is_admin=False
                )
                session.add(default_user)
                session.flush()
                
                # Create privacy settings
                privacy_settings = PrivacySetting(user_id=default_user.id)
                session.add(privacy_settings)
            
            # Migrate accounts
            if json_data.get("accounts"):
                for acc_data in json_data["accounts"]:
                    account = Account(
                        user_id=default_user.id,
                        account_name=acc_data.get("name", "Unknown Account"),
                        account_type=acc_data.get("type", "savings"),
                        institution_name=acc_data.get("bank", "Unknown Bank"),
                        balance=float(acc_data.get("balance", 0.0)),
                        currency="INR"
                    )
                    session.add(account)
                
                session.flush()  # Get account IDs
                
                # Migrate transactions
                if json_data.get("transactions"):
                    accounts = session.query(Account).filter(Account.user_id == default_user.id).all()
                    primary_account = accounts[0] if accounts else None
                    
                    for trans_data in json_data["transactions"]:
                        if primary_account:
                            transaction = Transaction(
                                user_id=default_user.id,
                                account_id=primary_account.id,
                                description=trans_data.get("description", "Unknown Transaction"),
                                amount=float(trans_data.get("amount", 0.0)),
                                category=trans_data.get("category", "other"),
                                transaction_type="credit" if trans_data.get("amount", 0.0) > 0 else "debit",
                                transaction_date=trans_data.get("date", func.now()),
                                merchant_name=trans_data.get("merchant")
                            )
                            session.add(transaction)
            
            # Migrate investments
            if json_data.get("investments"):
                for inv_data in json_data["investments"]:
                    investment = Investment(
                        user_id=default_user.id,
                        investment_name=inv_data.get("name", "Unknown Investment"),
                        investment_type=inv_data.get("type", "stocks"),
                        symbol=inv_data.get("symbol"),
                        quantity=float(inv_data.get("quantity", 0.0)),
                        current_price=float(inv_data.get("current_price", 0.0)),
                        total_value=float(inv_data.get("total_value", 0.0))
                    )
                    session.add(investment)
            
            # Migrate assets
            if json_data.get("assets"):
                for asset_data in json_data["assets"]:
                    asset = Asset(
                        user_id=default_user.id,
                        asset_name=asset_data.get("name", "Unknown Asset"),
                        asset_type=asset_data.get("type", "other"),
                        estimated_value=float(asset_data.get("value", 0.0)),
                        description=asset_data.get("description")
                    )
                    session.add(asset)
            
            # Migrate liabilities
            if json_data.get("liabilities"):
                for liab_data in json_data["liabilities"]:
                    liability = Liability(
                        user_id=default_user.id,
                        liability_name=liab_data.get("name", "Unknown Liability"),
                        liability_type=liab_data.get("type", "loan"),
                        outstanding_balance=float(liab_data.get("balance", 0.0)),
                        monthly_payment=float(liab_data.get("monthly_payment", 0.0)),
                        institution_name=liab_data.get("bank")
                    )
                    session.add(liability)
            
            session.commit()
            logger.info("JSON data migration completed successfully")
            
    except Exception as e:
        logger.error(f"JSON data migration failed: {e}")
        raise

# Initialize database on import if not in testing mode
if not settings.is_testing:
    try:
        db_manager.initialize()
        logger.info("Database manager initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed (will retry on first use): {e}")