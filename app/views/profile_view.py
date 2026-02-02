import flet as ft
from app.colors import AppColors
from app.auth.auth_context import AuthContext
from app.auth.auth_service import AuthService
from app.models.user import ScoreSaberStatus, User
from app.data.database import get_db

class ProfileView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER 
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Busca o ID do usuário da sessão
        user_id = self.page.session.get("user.id")
        if not user_id:
            self.controls = [ft.Text("Erro: Usuário não logado.")]
            return

        # Busca os dados completos e mais recentes do usuário no banco
        self._load_user(user_id)

        if not self.user:
            self.controls = [ft.Text("Erro: Não foi possível carregar os dados do usuário.")]
            return
            
        # Controles
        self.scoresaber_field = ft.TextField(
            label="URL ou ID do seu perfil ScoreSaber",
            value=self.user.scoresaber_id or "",
            width=400
        )
        self.status_text = ft.Text()
        self.update_status_text()

        self.save_btn = ft.ElevatedButton("Salvar ID do ScoreSaber", on_click=self._handle_save)
        self.feedback_text = ft.Text()

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Meu Perfil", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                        ft.Text(f"Usuário: {self.user.username}"),
                        ft.Divider(height=20),
                        ft.Text("Vincular ScoreSaber", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.Row([
                            ft.Text("Status:"),
                            self.status_text
                        ], spacing=10),
                        ft.Container(height=10),
                        self.scoresaber_field,
                        self.save_btn,
                        self.feedback_text
                    ],
                    spacing=15
                ),
                padding=30,
                border_radius=10,
                bgcolor=AppColors.SURFACE,
                width=500
            )
        ]

    def _load_user(self, user_id):
        """Carrega o usuário do banco de dados."""
        db = next(get_db())
        try:
            self.user = db.query(User).filter(User.id == user_id).first()
            # Precisamos fazer um 'expunge' ou detach se quisermos usar o objeto fora da sessão,
            # ou simplesmente copiar os dados que precisamos. 
            # Mas aqui, como vamos recarregar na ação de salvar, apenas manter a referência é ok
            # desde que não acessemos lazy loads depois que a sessão fechar.
            # Como User não tem relacionamentos lazy complexos aqui, deve ser seguro.
            if self.user:
                db.expunge(self.user) # Desanexa o objeto da sessão para que ele persista na memória
        finally:
            db.close()

    def update_status_text(self):
        status = self.user.scoresaber_status
        
        if status is None:
            status = ScoreSaberStatus.NONE

        status_color = {
            ScoreSaberStatus.PENDING: AppColors.WARNING,
            ScoreSaberStatus.APPROVED: AppColors.SUCCESS,
            ScoreSaberStatus.REJECTED: AppColors.ERROR,
            ScoreSaberStatus.NONE: AppColors.TEXT_SECONDARY
        }.get(status, AppColors.TEXT_SECONDARY)
        self.status_text.value = status.value
        self.status_text.color = status_color

    def _handle_save(self, e):
        new_id = self.scoresaber_field.value
        if not new_id:
            self.feedback_text.value = "O campo não pode estar vazio."
            self.feedback_text.color = AppColors.ERROR
            self.update()
            return

        try:
            # Atualiza no banco
            updated_user = AuthService.update_user_scoresaber_id(self.user.id, new_id)
            
            if updated_user:
                # Recarrega o usuário localmente para refletir as mudanças na UI
                # O AuthService retorna um objeto que pode estar atrelado a uma sessão fechada.
                # É mais seguro recarregar usando nosso método _load_user
                self._load_user(self.user.id)
                
                self.feedback_text.value = "ID do ScoreSaber enviado para aprovação!"
                self.feedback_text.color = AppColors.SUCCESS
                self.update_status_text()
                self.update()
            else:
                self.feedback_text.value = "Usuário não encontrado."
                self.feedback_text.color = AppColors.ERROR
                self.update()
                
        except Exception as ex:
            print(f"Erro no profile save: {ex}")
            self.feedback_text.value = f"Ocorreu um erro ao salvar: {str(ex)}"
            self.feedback_text.color = AppColors.ERROR
            self.update()
