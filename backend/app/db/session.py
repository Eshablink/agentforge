from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import get_settings

settings = get_settings()
# Readiness provides the connectivity check. Pool recycling and short
# connections prevent stale managed-PostgreSQL connections from lingering.
engine = create_engine(settings.database_url, pool_pre_ping=True,
                       pool_recycle=1800, pool_timeout=5,
                       connect_args={"connect_timeout": 5})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
