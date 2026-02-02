import flet as ft
from app.services.championship_service import ChampionshipService
from app.models.championship import Championship
from app.colors import AppColors

class ChampionshipsPublicView(ft.Column):
    """
    Um controle que gerencia a exibição da lista de campeonatos
    e a visualização de detalhes de um campeonato específico.
    """
    def __init__(self):
        super().__init__()
        self.expand = True
        self.championship_service = ChampionshipService()
        self.championships_list = []
        self.selected_championship: Championship | None = None
        
        self._render()

    def _render(self):
        """Limpa e reconstrói os controles filhos com base no estado atual."""
        self.controls.clear()
        
        if self.selected_championship is None:
            view_controls = self._build_championship_list_view()
        else:
            view_controls = self._build_championship_detail_view()
            
        self.controls.extend(view_controls)

    def _build_championship_list_view(self):
        """Constrói e retorna os controles para a view de lista."""
        self.championships_list = self.championship_service.get_all_championships()

        list_items = []
        for champ in self.championships_list:
            list_items.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(champ.name, style=ft.TextThemeStyle.HEADLINE_SMALL),
                            ft.Row([
                                ft.Icon(ft.icons.CALENDAR_TODAY),
                                ft.Text(f"{champ.start_date.strftime('%d/%m/%Y')} a {champ.end_date.strftime('%d/%m/%Y')}")
                            ]),
                            ft.Chip(label=ft.Text(champ.status.value))
                        ]),
                        padding=15
                    ),
                    on_click=lambda e, champ_id=champ.id: self._handle_championship_click(champ_id)
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
        """Constrói e retorna os controles para a view de detalhes."""
        
        # --- Aba de Partidas/Fases ---
        stages_content = []
        if self.selected_championship.stages:
            for stage in self.selected_championship.stages:
                matches_list = [ft.Text(f"Partidas da fase '{stage.name}' aqui...")]
                stages_content.append(
                    ft.Column([
                        ft.Text(stage.name, style=ft.TextThemeStyle.TITLE_LARGE),
                        ft.Text(f"Formato: {stage.match_format.value}"),
                        ft.Column(controls=matches_list)
                    ])
                )
        else:
            stages_content.append(ft.Container(
                content=ft.Text("Nenhuma fase definida para este campeonato.", color=AppColors.TEXT_SECONDARY),
                padding=20, alignment=ft.alignment.center
            ))
        
        matches_tab_content = ft.ListView(controls=stages_content, expand=True, spacing=20, padding=20)

        # --- Aba de Participantes ---
        participants_list = [ft.ListTile(title=ft.Text(p.player_name)) for p in self.selected_championship.participants]
        if not participants_list:
            participants_list.append(ft.Container(
                content=ft.Text("Nenhum participante inscrito.", color=AppColors.TEXT_SECONDARY),
                padding=20, alignment=ft.alignment.center
            ))
        participants_tab_content = ft.ListView(controls=participants_list, expand=True)

        # --- Aba de Informações ---
        info_tab_content = ft.Container(
            content=ft.Column([
                ft.Text("Descrição", style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Text(self.selected_championship.description, selectable=True),
                ft.Divider(height=20),
                ft.Text("Período", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text(f"{self.selected_championship.start_date.strftime('%d/%m/%Y')} a {self.selected_championship.end_date.strftime('%d/%m/%Y')}"),
            ]),
            padding=20
        )

        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Partidas", content=matches_tab_content),
                ft.Tab(text="Participantes", content=participants_tab_content),
                ft.Tab(text="Informações", content=info_tab_content),
            ],
            expand=True,
        )

        return [
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, on_click=self._handle_back_click, tooltip="Voltar"),
                ft.Text(self.selected_championship.name, style=ft.TextThemeStyle.HEADLINE_MEDIUM)
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            tabs
        ]

    # --- Handlers de Eventos ---
    def _handle_championship_click(self, championship_id: int):
        """Busca os detalhes do campeonato e atualiza a view."""
        self.selected_championship = self.championship_service.get_championship_by_id(championship_id)
        self._render()
        self.update()

    def _handle_back_click(self, e):
        """Volta para a lista de campeonatos."""
        self.selected_championship = None
        self._render()
        self.update()
