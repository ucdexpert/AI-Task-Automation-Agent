from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Database connection with connection pool settings
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True  # Test connections before using
    )
else:
    # PostgreSQL connection pool settings
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,  # Test connections before using
        pool_recycle=3600,   # Recycle connections every 1 hour
        pool_timeout=30,     # Timeout after 30 seconds
        connect_args={
            "connect_timeout": 10,
            "sslmode": "prefer"  # SSL mode
        }
    )

    # Handle SSL connection drops
    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        """Test connection health before checkout from pool"""
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SELECT 1")
            cursor.close()
        except Exception:
            logger.warning("Connection lost, invalidating from pool")
            raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
