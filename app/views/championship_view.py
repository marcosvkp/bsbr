import flet as ft
from app.services.championship_service import ChampionshipService
from app.models.championship import Championship, ChampionshipType, ParticipantStatus
from app.colors import AppColors
from app.auth.auth_context import AuthContext

class ChampionshipsPublicView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.championship_service = ChampionshipService()
        self.championships_list = []
        self.selected_championship: Championship | None = None
        
        self._render()

    def _render(self):
        self.controls.clear()
        
        if self.selected_championship is None:
            view_controls = self._build_championship_list_view()
        else:
            view_controls = self._build_championship_detail_view()
            
        self.controls.extend(view_controls)

    def _build_championship_list_view(self):
        self.championships_list = self.championship_service.get_all_championships()

        list_items = []
        for champ in self.championships_list:
            list_items.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(champ.name, style=ft.TextThemeStyle.HEADLINE_SMALL),
                            ft.Row([
                                ft.Icon(ft.Icons.CALENDAR_TODAY),
                                ft.Text(f"{champ.start_date.strftime('%d/%m/%Y')} a {champ.end_date.strftime('%d/%m/%Y')}")
                            ]),
                            ft.Chip(label=ft.Text(champ.status.value))
                        ]),
                        padding=15,
                        on_click=lambda e, champ_id=champ.id: self._handle_championship_click(champ_id)
                    )
                )
            )

        return [
            ft.Container(
                content=ft.Text("Campeonatos BSBR", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                padding=ft.padding.only(left=20, top=20, bottom=10)
            ),
            ft.ListView(controls=list_items, expand=True, spacing=10, padding=20)
        ]

    def _build_championship_detail_view(self):
        user = AuthContext.get_user(self.page)
        is_registered = False
        participant_id = None
        if user:
            for p in self.selected_championship.participants:
                if p.player_id == user.scoresaber_id:
                    is_registered = True
                    participant_id = p.id
                    break

        # --- Botões de Ação ---
        action_buttons = []
        if user and self.selected_championship.type == ChampionshipType.OPEN and not is_registered:
            action_buttons.append(ft.ElevatedButton("Inscrever-se", icon=ft.Icons.PERSON_ADD, on_click=self._handle_register))
        
        if is_registered:
            action_buttons.append(ft.ElevatedButton("Realizar Check-in", icon=ft.Icons.CHECK, on_click=lambda e, pid=participant_id: self._handle_check_in(pid), bgcolor=AppColors.SUCCESS, color=AppColors.TEXT))

        # --- Abas ---
        participants_list = [ft.ListTile(title=ft.Text(p.player_name)) for p in self.selected_championship.participants if p.status == ParticipantStatus.APPROVED]
        
        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Participantes", content=ft.ListView(controls=participants_list, expand=True)),
                ft.Tab(text="Informações", content=ft.Container(padding=20, content=ft.Text(self.selected_championship.description, selectable=True))),
            ],
            expand=True,
        )

        return [
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=self._handle_back_click, tooltip="Voltar"),
                ft.Text(self.selected_championship.name, style=ft.TextThemeStyle.HEADLINE_MEDIUM)
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row(action_buttons, spacing=10),
            tabs
        ]

    def _handle_championship_click(self, championship_id: int):
        self.selected_championship = self.championship_service.get_championship_by_id(championship_id)
        self._render()
        self.update()

    def _handle_back_click(self, e):
        self.selected_championship = None
        self._render()
        self.update()

    def _handle_register(self, e):
        user = AuthContext.get_user(self.page)
        if user and user.scoresaber_id and user.scoresaber_status == "approved":
            self.championship_service.register_participant(self.selected_championship.id, user.scoresaber_id, user.username)
            self._render() # Re-renderiza para esconder o botão
            self.update()
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Você precisa ter um ScoreSaber ID aprovado para se inscrever."), bgcolor=AppColors.ERROR)
            self.page.snack_bar.open = True
            self.page.update()

    def _handle_check_in(self, participant_id):
        if self.championship_service.perform_check_in(participant_id):
            self.page.snack_bar = ft.SnackBar(ft.Text("Check-in realizado com sucesso!"), bgcolor=AppColors.SUCCESS)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Não foi possível realizar o check-in."), bgcolor=AppColors.ERROR)
        self.page.snack_bar.open = True
        self.page.update()
        self._render()
