from sqlalchemy.orm import Session
from app.data.database import get_db
from app.models.user import User, UserRole, ScoreSaberStatus
from app.auth.security import Security
from app.config import AppConfig
import re

class AuthService:
    
    @staticmethod
    def ensure_admin_exists():
        """Cria o usuário admin padrão se ele não existir."""
        db: Session = next(get_db())
        try:
            admin = db.query(User).filter(User.username == "admin").first()
            if not admin:
                print("AuthService: Criando usuário admin padrão...")
                hashed_pw = Security.hash_password(AppConfig.ADMIN_DEFAULT_PASSWORD)
                new_admin = User(
                    username="admin",
                    hashed_password=hashed_pw,
                    role=UserRole.ADMIN,
                    scoresaber_status=ScoreSaberStatus.NONE
                )
                db.add(new_admin)
                db.commit()
                print("AuthService: Usuário admin criado.")
        finally:
            db.close()

    @staticmethod
    def authenticate_user(username, password):
        """Verifica as credenciais e retorna o usuário se forem válidas."""
        db: Session = next(get_db())
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user or not Security.verify_password(user.hashed_password, password):
                return None
            return user
        finally:
            db.close()

    @staticmethod
    def create_user(username, password, scoresaber_id=None):
        """Cria um novo usuário com role PLAYER."""
        db: Session = next(get_db())
        try:
            if db.query(User).filter(User.username == username).first():
                raise ValueError("Nome de usuário já existe.")

            hashed_pw = Security.hash_password(password)
            
            # Extrai o ID se for uma URL
            if scoresaber_id:
                match = re.search(r'/u/(\d+)', scoresaber_id)
                if match:
                    scoresaber_id = match.group(1)

            status = ScoreSaberStatus.PENDING if scoresaber_id else ScoreSaberStatus.NONE
            
            new_user = User(
                username=username,
                hashed_password=hashed_pw,
                role=UserRole.PLAYER,
                scoresaber_id=scoresaber_id,
                scoresaber_status=status
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        finally:
            db.close()

    @staticmethod
    def get_all_users():
        """Retorna todos os usuários, exceto o admin, para gerenciamento."""
        db: Session = next(get_db())
        try:
            return db.query(User).filter(User.role != UserRole.ADMIN).order_by(User.username).all()
        finally:
            db.close()

    @staticmethod
    def update_user_scoresaber_status(user_id: int, status: ScoreSaberStatus):
        """Atualiza o status do ScoreSaber de um usuário (Aprovar/Rejeitar)."""
        db: Session = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.scoresaber_status = status
                # Se rejeitado, limpa o ID para que possa ser submetido novamente
                if status == ScoreSaberStatus.REJECTED:
                    user.scoresaber_id = None
                db.commit()
                return user
            return None
        finally:
            db.close()

    @staticmethod
    def update_user_scoresaber_id(user_id: int, scoresaber_id: str):
        """Permite que um usuário atualize seu ScoreSaber ID."""
        db: Session = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # Extrai o ID se for uma URL
                match = re.search(r'/u/(\d+)', scoresaber_id)
                if match:
                    scoresaber_id = match.group(1)
                
                user.scoresaber_id = scoresaber_id
                user.scoresaber_status = ScoreSaberStatus.PENDING
                db.commit()
                return user
            return None
        finally:
            db.close()
