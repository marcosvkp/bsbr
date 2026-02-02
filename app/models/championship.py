from sqlalchemy import Column, Integer, String, DateTime, Enum as SqlEnum, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.data.database import Base
import enum
from datetime import datetime

# --- Enums ---
class ChampionshipStatus(enum.Enum):
    DRAFT = "Rascunho"
    ACTIVE = "Ativo"
    FINISHED = "Finalizado"

class ChampionshipType(enum.Enum):
    OPEN = "Aberto"
    INVITE_ONLY = "Por Convite"
    RANK_BASED = "Baseado em Ranking"

class MatchFormat(enum.Enum):
    BO1 = "Melhor de 1"
    BO3 = "Melhor de 3"
    BO5 = "Melhor de 5"
    BO7 = "Melhor de 7"

class MatchStatus(enum.Enum):
    PENDING = "Pendente"
    IN_PROGRESS = "Em Andamento"
    COMPLETED = "Concluída"
    CANCELLED = "Cancelada"

# --- Modelos SQLAlchemy ---

class Championship(Base):
    __tablename__ = "championships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(SqlEnum(ChampionshipStatus), default=ChampionshipStatus.DRAFT)
    type = Column(SqlEnum(ChampionshipType), default=ChampionshipType.OPEN)

    # Relacionamentos
    participants = relationship("ChampionshipParticipant", back_populates="championship", cascade="all, delete-orphan")
    stages = relationship("ChampionshipStage", back_populates="championship", cascade="all, delete-orphan", order_by="ChampionshipStage.order")

class ChampionshipParticipant(Base):
    __tablename__ = "championship_participants"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championships.id"))
    player_id = Column(String, index=True) # ScoreSaber ID (String)
    player_name = Column(String, nullable=True) # Cache do nome para exibição rápida
    
    final_rank = Column(Integer, nullable=True)

    championship = relationship("Championship", back_populates="participants")
    matches_as_p1 = relationship("Match", foreign_keys="[Match.participant1_id]", back_populates="participant1")
    matches_as_p2 = relationship("Match", foreign_keys="[Match.participant2_id]", back_populates="participant2")
    matches_won = relationship("Match", foreign_keys="[Match.winner_participant_id]", back_populates="winner_participant")
    match_games_won = relationship("MatchGame", foreign_keys="[MatchGame.winner_participant_id]", back_populates="winner_participant")


class ChampionshipStage(Base):
    __tablename__ = "championship_stages"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championships.id"))
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    match_format = Column(SqlEnum(MatchFormat), default=MatchFormat.BO1)

    championship = relationship("Championship", back_populates="stages")
    maps_in_pool = relationship("ChampionshipStageMap", back_populates="stage", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="stage", cascade="all, delete-orphan")


class ChampionshipStageMap(Base):
    __tablename__ = "championship_stage_maps"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("championship_stages.id"))
    map_hash = Column(String, nullable=False) # Hash do BeatSaver
    difficulty = Column(String, nullable=False) # Ex: ExpertPlus
    
    # Metadados opcionais para exibição rápida sem consulta externa
    map_name = Column(String, nullable=True)
    map_cover = Column(String, nullable=True)

    stage = relationship("ChampionshipStage", back_populates="maps_in_pool")
    match_games = relationship("MatchGame", back_populates="map")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("championship_stages.id"))
    participant1_id = Column(Integer, ForeignKey("championship_participants.id"))
    participant2_id = Column(Integer, ForeignKey("championship_participants.id"))
    winner_participant_id = Column(Integer, ForeignKey("championship_participants.id"), nullable=True)
    status = Column(SqlEnum(MatchStatus), default=MatchStatus.PENDING)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    stage = relationship("ChampionshipStage", back_populates="matches")
    participant1 = relationship("ChampionshipParticipant", foreign_keys=[participant1_id], back_populates="matches_as_p1")
    participant2 = relationship("ChampionshipParticipant", foreign_keys=[participant2_id], back_populates="matches_as_p2")
    winner_participant = relationship("ChampionshipParticipant", foreign_keys=[winner_participant_id], back_populates="matches_won")
    games = relationship("MatchGame", back_populates="match", cascade="all, delete-orphan")


class MatchGame(Base):
    __tablename__ = "match_games"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    map_id = Column(Integer, ForeignKey("championship_stage_maps.id"))
    winner_participant_id = Column(Integer, ForeignKey("championship_participants.id"), nullable=True)
    
    score1 = Column(Integer, nullable=True) # Score do participant1 da Match
    score2 = Column(Integer, nullable=True) # Score do participant2 da Match
    
    submitted_at = Column(DateTime, default=datetime.utcnow)
    proof_link = Column(String, nullable=True)

    match = relationship("Match", back_populates="games")
    map = relationship("ChampionshipStageMap", back_populates="match_games")
    winner_participant = relationship("ChampionshipParticipant", foreign_keys=[winner_participant_id], back_populates="match_games_won")
