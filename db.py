from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, BigInteger, DateTime, Boolean
from config import DATABASE_URL

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    free_requests = Column(Integer, default=5)
    paid_requests_left = Column(Integer, default=0)
    subscription_until = Column(DateTime, nullable=True)
    expiry_notified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)