from sqlalchemy import Column, Integer, String, DateTime, DECIMAL
from sqlalchemy.sql import func
from app.data.database import Base

class RankedBRMaps(Base):
    __tablename__ = "ranked_br_maps"

    leaderboard_id = Column(String, primary_key=True, index=True)
    difficulty = Column(String, nullable=False, default="ExpertPlus")
    map_name = Column(String, nullable=False)
    map_author = Column(String, nullable=False)
    stars = Column(DECIMAL, nullable=False)
    max_score = Column(Integer, nullable=False, default=0, server_default='0')
