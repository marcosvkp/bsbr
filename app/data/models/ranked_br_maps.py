from sqlalchemy import Column, Integer, String, DateTime, DECIMAL
from sqlalchemy.sql import func
from app.data.database import Base

class RankedBRMaps(Base):
    __tablename__ = "ranked_br_maps"

    id = Column(String, primary_key=True, index=True)
    difficulty = Column(String, primary_key=True, index=True)
    stars = Column(DECIMAL, nullable=False)
    map_id = Column(String, nullable=False)
