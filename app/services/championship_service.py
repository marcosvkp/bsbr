from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from app.data.database import get_db
from app.data.data_manager import DataManager
from app.models.championship import (
    Championship, ChampionshipStatus, ChampionshipType,
    ChampionshipParticipant, ParticipantStatus, ChampionshipStage, ChampionshipStageMap,
    Match, MatchFormat, MatchStatus, MatchGame
)

class ChampionshipService:
    def __init__(self):
        pass

    # --- Gerenciamento de Campeonatos ---

    def get_all_championships(self) -> List[Championship]:
        db: Session = next(get_db())
        try:
            return db.query(Championship).order_by(Championship.start_date.desc()).all()
        finally:
            db.close()

    def get_championship_by_id(self, championship_id: int) -> Optional[Championship]:
        db: Session = next(get_db())
        try:
            return db.query(Championship).options(
                joinedload(Championship.stages).joinedload(ChampionshipStage.maps_in_pool),
                joinedload(Championship.participants)
            ).filter(Championship.id == championship_id).first()
        finally:
            db.close()

    def create_championship(self, name: str, description: str, start_date: datetime, end_date: datetime, type: ChampionshipType) -> Championship:
        db: Session = next(get_db())
        try:
            new_champ = Championship(
                name=name, description=description, start_date=start_date,
                end_date=end_date, status=ChampionshipStatus.DRAFT, type=type
            )
            db.add(new_champ)
            db.commit()
            db.refresh(new_champ)
            return new_champ
        finally:
            db.close()

    def delete_championship(self, championship_id: int):
        db: Session = next(get_db())
        try:
            champ = db.query(Championship).filter(Championship.id == championship_id).first()
            if champ:
                db.delete(champ)
                db.commit()
        finally:
            db.close()

    def update_championship_status(self, championship_id: int, new_status: ChampionshipStatus):
        db: Session = next(get_db())
        try:
            champ = db.query(Championship).filter(Championship.id == championship_id).first()
            if champ:
                champ.status = new_status
                db.commit()
        finally:
            db.close()

    # --- Gerenciamento de Participantes ---

    def add_participants_by_rank(self, championship_id: int, start_rank: int, end_rank: int):
        """Adiciona jogadores com base na faixa de ranking do BSBR."""
        players_in_range = [p for p in DataManager.bsbr_data if start_rank <= p['pos'] <= end_rank]
        
        db: Session = next(get_db())
        try:
            for player in players_in_range:
                existing = db.query(ChampionshipParticipant).filter_by(championship_id=championship_id, player_id=player['id']).first()
                if not existing:
                    new_participant = ChampionshipParticipant(
                        championship_id=championship_id,
                        player_id=player['id'],
                        player_name=player['name'],
                        status=ParticipantStatus.APPROVED # Aprovado automaticamente
                    )
                    db.add(new_participant)
            db.commit()
        finally:
            db.close()

    def add_participant_by_invite(self, championship_id: int, player_id: str, player_name: str):
        """Adiciona um jogador por convite (ID do ScoreSaber)."""
        db: Session = next(get_db())
        try:
            existing = db.query(ChampionshipParticipant).filter_by(championship_id=championship_id, player_id=player_id).first()
            if not existing:
                new_participant = ChampionshipParticipant(
                    championship_id=championship_id,
                    player_id=player_id,
                    player_name=player_name,
                    status=ParticipantStatus.APPROVED # Aprovado automaticamente
                )
                db.add(new_participant)
                db.commit()
        finally:
            db.close()

    def register_participant(self, championship_id: int, player_id: str, player_name: str):
        """Um jogador se inscreve em um campeonato aberto."""
        db: Session = next(get_db())
        try:
            existing = db.query(ChampionshipParticipant).filter_by(championship_id=championship_id, player_id=player_id).first()
            if not existing:
                new_participant = ChampionshipParticipant(
                    championship_id=championship_id,
                    player_id=player_id,
                    player_name=player_name,
                    status=ParticipantStatus.PENDING # Requer aprovação
                )
                db.add(new_participant)
                db.commit()
        finally:
            db.close()

    def update_participant_status(self, participant_id: int, status: ParticipantStatus):
        """Aprova ou rejeita um participante."""
        db: Session = next(get_db())
        try:
            participant = db.query(ChampionshipParticipant).filter_by(id=participant_id).first()
            if participant:
                participant.status = status
                db.commit()
        finally:
            db.close()

    def approve_all_participants(self, championship_id: int):
        """Aprova todos os participantes pendentes de um campeonato."""
        db: Session = next(get_db())
        try:
            db.query(ChampionshipParticipant).filter_by(
                championship_id=championship_id,
                status=ParticipantStatus.PENDING
            ).update({"status": ParticipantStatus.APPROVED})
            db.commit()
        finally:
            db.close()
            
    def perform_check_in(self, participant_id: int):
        """Realiza o check-in de um participante."""
        db: Session = next(get_db())
        try:
            participant = db.query(ChampionshipParticipant).filter_by(id=participant_id).first()
            if participant and participant.status == ParticipantStatus.APPROVED:
                participant.checked_in = True
                participant.checked_in_at = datetime.utcnow()
                db.commit()
                return True
            return False
        finally:
            db.close()
            
    # --- Gerenciamento de Fases e Mapas ---

    def add_stage_to_championship(self, championship_id: int, name: str, order: int, match_format: MatchFormat) -> ChampionshipStage:
        db: Session = next(get_db())
        try:
            new_stage = ChampionshipStage(
                championship_id=championship_id, name=name, order=order, match_format=match_format
            )
            db.add(new_stage)
            db.commit()
            db.refresh(new_stage)
            return new_stage
        finally:
            db.close()

    def add_map_to_stage_pool(self, stage_id: int, map_hash: str, difficulty: str, map_name: str = None, map_cover: str = None) -> ChampionshipStageMap:
        db: Session = next(get_db())
        try:
            new_map = ChampionshipStageMap(
                stage_id=stage_id, map_hash=map_hash, difficulty=difficulty,
                map_name=map_name, map_cover=map_cover
            )
            db.add(new_map)
            db.commit()
            db.refresh(new_map)
            return new_map
        finally:
            db.close()
