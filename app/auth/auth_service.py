from sqlalchemy.orm import Session
from app.data.database import get_db
from app.models.user import User, UserRole, ScoreSaberStatus
from app.auth.security import Security
from app.config import AppConfig

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
        """
        Verifica as credenciais e retorna o usuário se forem válidas.
        Retorna None caso contrário.
        """
        db: Session = next(get_db())
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return None
            
            if Security.verify_password(user.hashed_password, password):
                return user
            return None
        finally:
            db.close()

    @staticmethod
    def create_user(username, password, scoresaber_id=None):
        """
        Cria um novo usuário com role PLAYER.
        Retorna o usuário criado ou lança uma exceção se já existir.
        """
        db: Session = next(get_db())
        try:
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                raise ValueError("Nome de usuário já existe.")

            hashed_pw = Security.hash_password(password)
            
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
