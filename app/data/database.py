import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuração do Caminho do Banco
DB_FOLDER = "storage"
DB_NAME = "bsbr.db"
DB_PATH = os.path.join(os.getcwd(), DB_FOLDER, DB_NAME)
CONNECTION_STRING = f"sqlite:///{DB_PATH}"

# Garante que a pasta storage existe
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# SQLAlchemy Setup
engine = create_engine(CONNECTION_STRING, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    """Generator para obter a sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Cria as tabelas no banco de dados."""
    # Importar os models aqui para que o Base os reconheça
    #from app.data.models.user import User
    Base.metadata.create_all(bind=engine)
