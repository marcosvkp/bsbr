import flet as ft
from app.colors import AppColors
from app.auth.auth_service import AuthService
from app.services.championship_service import ChampionshipService
from app.models.user import User, ScoreSaberStatus
from app.models.championship import Championship, ChampionshipType
from app.views.admin_championship_detail_view import AdminChampionshipDetailView
from datetime import datetime

class AdminView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        
        self.users = AuthService.get_all_users()
        self.championships = ChampionshipService().get_all_championships()
        
        self.users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Usuário")),
                ft.DataColumn(ft.Text("ScoreSaber ID")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Ações")),
            ],
            rows=[]
        )

        self.champs_list_view = ft.ListView(expand=True, spacing=10, padding=20)

        # Estado para navegação interna
        self.current_view = "main" # main ou detail
        self.detail_view = None

        self.build()
        self.update_users_list()
        self.update_champs_list()

    def build(self):
        self.controls = [
            ft.Container(
                content=ft.Text("Painel Administrativo", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                padding=20
            ),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Gerenciar Usuários", content=ft.Column([self.users_table], scroll=ft.ScrollMode.AUTO, expand=True)),
                    ft.Tab(text="Gerenciar Campeonatos", content=self._build_champs_tab()),
                ],
                expand=True,
            )
        ]

    def update_users_list(self):
        rows = []
        for user in self.users:
            status_color = {
                ScoreSaberStatus.PENDING: AppColors.WARNING,
                ScoreSaberStatus.APPROVED: AppColors.SUCCESS,
                ScoreSaberStatus.REJECTED: AppColors.ERROR,
                ScoreSaberStatus.NONE: AppColors.TEXT_SECONDARY
            }.get(user.scoresaber_status, AppColors.TEXT_SECONDARY)

            actions = []
            if user.scoresaber_status == ScoreSaberStatus.PENDING:
                actions.extend([
                    ft.IconButton(ft.Icons.CHECK_CIRCLE_OUTLINE, icon_color=AppColors.SUCCESS, on_click=lambda e, u=user: self._handle_approve(u.id), tooltip="Aprovar"),
                    ft.IconButton(ft.Icons.CANCEL_OUTLINED, icon_color=AppColors.ERROR, on_click=lambda e, u=user: self._handle_reject(u.id), tooltip="Rejeitar"),
                ])
            else:
                actions.append(ft.Container(width=80))

            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(user.username)),
                    ft.DataCell(ft.Text(user.scoresaber_id or 'N/A')),
                    ft.DataCell(ft.Container(
                        content=ft.Text(user.scoresaber_status.value if user.scoresaber_status else 'N/A', color=AppColors.BACKGROUND, size=12, weight=ft.FontWeight.BOLD),
                        bgcolor=status_color,
                        padding=5,
                        border_radius=5
                    )),
                    ft.DataCell(ft.Row(actions, spacing=0)),
                ])
            )
        self.users_table.rows = rows
        if self.page: self.page.update()

    def _build_champs_tab(self):
        return ft.Column([
            ft.Container(
                content=ft.ElevatedButton("Criar Novo Campeonato", icon=ft.Icons.ADD, on_click=self._open_create_champ_dialog),
                padding=ft.padding.only(top=10, left=20, right=20)
            ),
            self.champs_list_view
        ], expand=True, spacing=10)

    def update_champs_list(self):
        items = []
        for champ in self.championships:
            items.append(
                ft.ListTile(
                    title=ft.Text(champ.name),
                    subtitle=ft.Text(f"Status: {champ.status.value} | Tipo: {champ.type.value}"),
                    trailing=ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=AppColors.ERROR, on_click=lambda e, c=champ: self._handle_delete_champ(c.id), tooltip="Deletar"),
                    on_click=lambda e, c=champ: self._open_champ_detail(c.id)
                )
            )
        self.champs_list_view.controls = items
        if self.page: self.page.update()

    def _open_champ_detail(self, champ_id):
        self.detail_view = AdminChampionshipDetailView(self.page, champ_id, self._back_to_main)
        self.controls = [self.detail_view]
        self.page.update()

    def _back_to_main(self, e):
        self.detail_view = None
        self.build() # Reconstrói a view principal
        self.update_users_list()
        self.update_champs_list()
        self.page.update()

    def _handle_approve(self, user_id):
        AuthService.update_user_scoresaber_status(user_id, ScoreSaberStatus.APPROVED)
        self.users = AuthService.get_all_users()
        self.update_users_list()

    def _handle_reject(self, user_id):
        AuthService.update_user_scoresaber_status(user_id, ScoreSaberStatus.REJECTED)
        self.users = AuthService.get_all_users()
        self.update_users_list()

    def _open_create_champ_dialog(self, e):
        try:
            name_field = ft.TextField(label="Nome do Campeonato")
            desc_field = ft.TextField(label="Descrição", multiline=True)
            start_date_field = ft.TextField(label="Data de Início (YYYY-MM-DD)", hint_text="Ex: 2024-01-01")
            end_date_field = ft.TextField(label="Data de Fim (YYYY-MM-DD)", hint_text="Ex: 2024-01-15")
            type_dropdown = ft.Dropdown(
                label="Tipo",
                options=[ft.dropdown.Option(key=t.name, text=t.value) for t in ChampionshipType],
                value=ChampionshipType.OPEN.name
            )
            error_text = ft.Text("", color=AppColors.ERROR)

            dlg = None

            def create_champ(e):
                try:
                    if not name_field.value or not start_date_field.value or not end_date_field.value:
                        error_text.value = "Preencha todos os campos obrigatórios."
                        dlg.update()
                        return

                    start_date = datetime.fromisoformat(start_date_field.value)
                    end_date = datetime.fromisoformat(end_date_field.value)
                    champ_type = ChampionshipType[type_dropdown.value]

                    ChampionshipService().create_championship(
                        name=name_field.value,
                        description=desc_field.value,
                        start_date=start_date,
                        end_date=end_date,
                        type=champ_type
                    )
                    
                    self.page.close(dlg)
                    self.championships = ChampionshipService().get_all_championships()
                    self.update_champs_list()
                    self.page.update()
                except ValueError:
                    error_text.value = "Formato de data inválido. Use YYYY-MM-DD."
                    dlg.update()
                except Exception as ex:
                    error_text.value = f"Erro: {str(ex)}"
                    print(f"Erro ao criar campeonato: {ex}")
                    dlg.update()
            
            dialog_content = ft.Column([
                name_field, desc_field, start_date_field, end_date_field, type_dropdown, error_text
            ], scroll=ft.ScrollMode.AUTO, spacing=15, height=400)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Criar Novo Campeonato"),
                content=dialog_content,
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                    ft.ElevatedButton("Criar", on_click=create_champ),
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            
            self.page.open(dlg)

        except Exception as ex:
            print(f"ERRO CRÍTICO ao abrir diálogo: {ex}")


    def _handle_delete_champ(self, champ_id):
        ChampionshipService().delete_championship(champ_id)
        self.championships = ChampionshipService().get_all_championships()
        self.update_champs_list()
