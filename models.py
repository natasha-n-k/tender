from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import enum
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Определение статусов тендера
class TenderStatus(enum.Enum):
    CREATED = "CREATED"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"

# Определение статусов предложения
class BidStatus(enum.Enum):
    CREATED = "CREATED"
    PUBLISHED = "PUBLISHED"
    CANCELED = "CANCELED"

# Модель тендера
class Tender(Base):
    __tablename__ = 'tenders'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    service_type = Column(String, nullable=False)
    status = Column(Enum(TenderStatus), default=TenderStatus.CREATED)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Отношение с предложениями
    bids = relationship('Bid', backref='tender')

# Модель предложения
class Bid(Base):
    __tablename__ = 'bids'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(BidStatus), default=BidStatus.CREATED)
    tender_id = Column(Integer, ForeignKey('tenders.id'))
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

# Модель организации
class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Модель ответственного за организацию
class OrganizationResponsible(Base):
    __tablename__ = 'organization_responsible'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

# Модель пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Инициализация базы данных
DATABASE_URL = os.getenv('POSTGRES_CONN', 'postgresql://postgres:1234@localhost:5432/postgres')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
