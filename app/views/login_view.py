import flet as ft
from app.colors import AppColors
from app.auth.auth_service import AuthService
from app.auth.auth_context import AuthContext

class LoginView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # Estado
        self.is_registering = False
        
        # Controles
        self.username_field = ft.TextField(label="Usuário", width=300)
        self.password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
        self.scoresaber_field = ft.TextField(label="ScoreSaber ID (Opcional)", width=300, visible=False)
        
        self.error_text = ft.Text("", color=AppColors.ERROR, size=14)
        
        self.action_btn = ft.ElevatedButton("Entrar", on_click=self._handle_action, width=300)
        self.toggle_btn = ft.TextButton("Não tem conta? Registre-se", on_click=self._toggle_mode)

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.LOCK_OUTLINE, size=50, color=AppColors.PRIMARY),
                        ft.Text("Login BSBR", size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(height=20),
                        self.username_field,
                        self.password_field,
                        self.scoresaber_field,
                        ft.Container(height=10),
                        self.error_text,
                        ft.Container(height=10),
                        self.action_btn,
                        self.toggle_btn
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                padding=40,
                bgcolor=AppColors.SURFACE,
                border_radius=10,
                width=400
            )
        ]

    def _toggle_mode(self, e):
        self.is_registering = not self.is_registering
        
        if self.is_registering:
            self.scoresaber_field.visible = True
            self.action_btn.text = "Registrar"
            self.toggle_btn.text = "Já tem conta? Faça Login"
        else:
            self.scoresaber_field.visible = False
            self.action_btn.text = "Entrar"
            self.toggle_btn.text = "Não tem conta? Registre-se"
            
        self.error_text.value = ""
        self.update()

    def _handle_action(self, e):
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.error_text.value = "Preencha todos os campos obrigatórios."
            self.update()
            return

        try:
            if self.is_registering:
                # Registro
                scoresaber_id = self.scoresaber_field.value if self.scoresaber_field.value else None
                user = AuthService.create_user(username, password, scoresaber_id)
                
                # Auto-login após registro
                AuthContext.login(self.page, user)
                self.page.go("/")
                
            else:
                # Login
                user = AuthService.authenticate_user(username, password)
                if user:
                    AuthContext.login(self.page, user)
                    self.page.go("/")
                else:
                    self.error_text.value = "Usuário ou senha incorretos."
                    self.update()
                    
        except ValueError as err:
            self.error_text.value = str(err)
            self.update()
        except Exception as ex:
            print(f"Erro no login: {ex}")
            self.error_text.value = "Ocorreu um erro inesperado."
            self.update()
