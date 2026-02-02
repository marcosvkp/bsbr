from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from app.data.database import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    PLAYER = "player"

class ScoreSaberStatus(enum.Enum):
    NONE = "none"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SqlEnum(UserRole), default=UserRole.PLAYER)
    
    # Vinculação com ScoreSaber
    scoresaber_id = Column(String, nullable=True)
    scoresaber_status = Column(SqlEnum(ScoreSaberStatus), default=ScoreSaberStatus.NONE)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"
