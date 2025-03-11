from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_engine = None # Global engine which manages the connection pool
_SessionLocal = None # Global session factory

def init_db(db_url: str):
    """
    Called once at application startup.
    Creates the global engine and SessionLocal for the entire app.
    """
    global _engine, _SessionLocal
    if _engine is not None:
        return  # Already initialized
    
    if not db_url:
        raise ValueError("DATABASE_URL is empty or not provided.")
    
    _engine = create_engine(db_url, echo=False, future=True)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

def get_db():
    """
    FastAPI dependency that yields a session from the global SessionLocal.
    Raises an error if init_db(...) wasn't called.
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db(db_url) before get_db().")
    
    db = _SessionLocal()
    try:
        yield db # return db to the caller, but come back to this function when the request is done
    finally:
        db.close()
