import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class AppConfig:
    DISCORD_LINK = "https://discord.gg/dmtfhxdgah"
    
    # Senha padrão para o usuário 'admin'.
    # Defina ADMIN_DEFAULT_PASSWORD no seu arquivo .env
    ADMIN_DEFAULT_PASSWORD = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin_password_123")
