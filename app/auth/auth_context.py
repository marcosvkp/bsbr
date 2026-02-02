from typing import Optional
import flet as ft
from app.models.user import User

class AuthContext:
    """
    Classe de contexto de autenticação com métodos estáticos
    para gerenciar o estado do usuário na sessão da página.
    """

    @staticmethod
    def login(page: ft.Page, user: User):
        """
        Realiza o login, armazenando os dados do usuário na sessão.
        """
        page.session.set("user.id", user.id)
        page.session.set("user.username", user.username)
        page.session.set("user.role", user.role)
        print(f"AuthContext: Usuário '{user.username}' logado com sucesso.")

    @staticmethod
    def logout(page: ft.Page):
        """
        Realiza o logout, limpando os dados do usuário da sessão.
        """
        page.session.remove("user.id")
        page.session.remove("user.username")
        page.session.remove("user.role")
        print("AuthContext: Usuário deslogado.")
        page.go("/") # Redireciona para a home após o logout

    @staticmethod
    def get_user(page: ft.Page) -> Optional[User]:
        """
        Recupera o objeto User da sessão, se o usuário estiver logado.
        """
        user_id = page.session.get("user.id")
        if not user_id:
            return None
        
        return User(
            id=user_id,
            username=page.session.get("user.username"),
            role=page.session.get("user.role")
        )

    @staticmethod
    def is_logged_in(page: ft.Page) -> bool:
        """Verifica se há um usuário logado na sessão."""
        return page.session.get("user.id") is not None

    @staticmethod
    def is_admin(page: ft.Page) -> bool:
        """Verifica se o usuário logado tem a role 'admin'."""
        if not AuthContext.is_logged_in(page):
            return False
        return page.session.get("user.role") == "admin"
