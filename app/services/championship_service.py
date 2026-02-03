from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from app.data.database import get_db
from app.models.championship import (
    Championship, ChampionshipStatus, ChampionshipType,
    ChampionshipParticipant, ChampionshipStage, ChampionshipStageMap,
    Match, MatchFormat, MatchStatus, MatchGame
)

class ChampionshipService:
    def __init__(self):
        # O serviço agora não mantém estado, ele opera diretamente no banco.
        pass

    # --- Gerenciamento de Campeonatos ---

    def get_all_championships(self) -> List[Championship]:
        """Retorna todos os campeonatos do banco de dados."""
        db: Session = next(get_db())
        try:
            return db.query(Championship).order_by(Championship.start_date.desc()).all()
        finally:
            db.close()

    def get_championship_by_id(self, championship_id: int) -> Optional[Championship]:
        """Busca um campeonato específico pelo seu ID, com seus relacionamentos."""
        db: Session = next(get_db())
        try:
            return db.query(Championship).options(
                joinedload(Championship.stages).joinedload(ChampionshipStage.maps_in_pool),
                joinedload(Championship.participants)
            ).filter(Championship.id == championship_id).first()
        finally:
            db.close()

    def create_championship(self, name: str, description: str, start_date: datetime, end_date: datetime, type: ChampionshipType) -> Championship:
        """Cria um novo campeonato no banco de dados."""
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

    def update_championship_status(self, championship_id: int, new_status: ChampionshipStatus):
        """Atualiza o status de um campeonato."""
        db: Session = next(get_db())
        try:
            champ = db.query(Championship).filter(Championship.id == championship_id).first()
            if champ:
                champ.status = new_status
                db.commit()
        finally:
            db.close()

    # --- Gerenciamento de Fases (Stages) ---

    def add_stage_to_championship(self, championship_id: int, name: str, order: int, match_format: MatchFormat) -> ChampionshipStage:
        """Adiciona uma nova fase a um campeonato."""
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
        """Adiciona um mapa ao pool de uma fase."""
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

    # --- Gerenciamento de Participantes e Partidas (Matches) ---

    def add_participant(self, championship_id: int, player_id: str, player_name: str) -> Optional[ChampionshipParticipant]:
        """Adiciona um participante a um campeonato."""
        db: Session = next(get_db())
        try:
            existing = db.query(ChampionshipParticipant).filter_by(championship_id=championship_id, player_id=player_id).first()
            if existing:
                return existing
            new_participant = ChampionshipParticipant(championship_id=championship_id, player_id=player_id, player_name=player_name)
            db.add(new_participant)
            db.commit()
            db.refresh(new_participant)
            return new_participant
        finally:
            db.close()

    def create_matches_for_stage(self, stage_id: int, participant_pairs: List[Tuple[int, int]]) -> List[Match]:
        """Cria as partidas para uma fase com base em pares de IDs de participantes."""
        db: Session = next(get_db())
        try:
            matches = []
            for p1_id, p2_id in participant_pairs:
                match = Match(stage_id=stage_id, participant1_id=p1_id, participant2_id=p2_id)
                matches.append(match)
            db.add_all(matches)
            db.commit()
            return matches
        finally:
            db.close()

    def record_match_game_result(self, match_id: int, map_id: int, score1: int, score2: int, winner_participant_id: int, proof_link: str = None) -> MatchGame:
        """Registra o resultado de um jogo (mapa) dentro de uma partida e verifica se a partida terminou."""
        db: Session = next(get_db())
        try:
            new_game = MatchGame(
                match_id=match_id, map_id=map_id, score1=score1, score2=score2,
                winner_participant_id=winner_participant_id, proof_link=proof_link
            )
            db.add(new_game)
            
            # Lógica para verificar e finalizar a partida
            match = db.query(Match).options(joinedload(Match.games), joinedload(Match.stage)).filter(Match.id == match_id).first()
            if match:
                p1_wins = sum(1 for game in match.games if game.winner_participant_id == match.participant1_id)
                p2_wins = sum(1 for game in match.games if game.winner_participant_id == match.participant2_id)

                # Adiciona a vitória do jogo atual
                if winner_participant_id == match.participant1_id:
                    p1_wins += 1
                else:
                    p2_wins += 1

                # Calcula o número de vitórias necessárias
                wins_needed = {
                    MatchFormat.BO1: 1, MatchFormat.BO3: 2,
                    MatchFormat.BO5: 3, MatchFormat.BO7: 4
                }.get(match.stage.match_format, 1)

                if p1_wins >= wins_needed:
                    match.winner_participant_id = match.participant1_id
                    match.status = MatchStatus.COMPLETED
                    match.end_time = datetime.utcnow()
                elif p2_wins >= wins_needed:
                    match.winner_participant_id = match.participant2_id
                    match.status = MatchStatus.COMPLETED
                    match.end_time = datetime.utcnow()
                else:
                    match.status = MatchStatus.IN_PROGRESS

            db.commit()
            db.refresh(new_game)
            return new_game
        finally:
            db.close()
