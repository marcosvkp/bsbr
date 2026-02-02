from typing import Optional
import flet as ft
from app.models.user import User, UserRole
from app.data.database import get_db

class AuthContext:
    """
    Classe de contexto de autenticação com métodos estáticos
    para gerenciar o estado do usuário na sessão da página.
    """

    @staticmethod
    def login(page: ft.Page, user: User):
        """
        Realiza o login, armazenando o ID do usuário na sessão.
        """
        page.session.set("user.id", user.id)
        print(f"AuthContext: Usuário ID '{user.id}' logado com sucesso.")

    @staticmethod
    def logout(page: ft.Page):
        """
        Realiza o logout, limpando os dados do usuário da sessão.
        """
        page.session.remove("user.id")
        print("AuthContext: Usuário deslogado.")
        page.go("/") # Redireciona para a home após o logout

    @staticmethod
    def get_user(page: ft.Page) -> Optional[User]:
        """
        Recupera o objeto User completo do banco de dados,
        com base no ID armazenado na sessão.
        """
        user_id = page.session.get("user.id")
        if not user_id:
            return None
        
        db = next(get_db())
        try:
            # Busca o usuário completo no banco de dados
            user = db.query(User).filter(User.id == user_id).first()
            return user
        finally:
            db.close()

    @staticmethod
    def is_logged_in(page: ft.Page) -> bool:
        """Verifica se há um usuário logado na sessão."""
        return page.session.get("user.id") is not None

    @staticmethod
    def is_admin(page: ft.Page) -> bool:
        """Verifica se o usuário logado tem a role 'admin'."""
        user = AuthContext.get_user(page)
        if not user:
            return False
        return user.role == UserRole.ADMIN
