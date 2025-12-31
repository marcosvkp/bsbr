from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, UniqueConstraint
from app.data.database import Base

class PlayerScore(Base):
    __tablename__ = "player_scores"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)
    leaderboard_id = Column(Integer, index=True)
    
    # Dados do Mapa
    map_name = Column(String)
    map_cover = Column(String)
    diff = Column(String)
    stars = Column(String) # Armazenado como string "X.XX★" para manter compatibilidade visual
    
    # Dados do Score
    acc = Column(Float)
    pp = Column(Float)
    score = Column(Integer)
    map_rank = Column(Integer)
    
    # Garante que não duplicaremos o mesmo mapa para o mesmo jogador
    __table_args__ = (
        UniqueConstraint('player_id', 'leaderboard_id', name='uix_player_leaderboard'),
    )

    def to_dict(self):
        return {
            "map_name": self.map_name,
            "map_cover": self.map_cover,
            "diff": self.diff,
            "stars": self.stars,
            "acc": self.acc,
            "pp": self.pp,
            "score": self.score,
            "map_rank": self.map_rank,
            "leaderboard_id": self.leaderboard_id
        }
