import flet as ft
from app.colors import AppColors
from app.services.championship_service import ChampionshipService
from app.models.championship import Championship, ParticipantStatus, MatchFormat
from app.data.data_manager import DataManager

class AdminChampionshipDetailView(ft.Column):
    def __init__(self, page: ft.Page, championship_id: int, on_back):
        super().__init__()
        self.page = page
        self.championship_id = championship_id
        self.on_back = on_back
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        
        self.service = ChampionshipService()
        self.championship = self.service.get_championship_by_id(championship_id)
        
        # Tabelas
        self.participants_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Check-in")),
                ft.DataColumn(ft.Text("Ações")),
            ],
            rows=[]
        )
        
        self.stages_column = ft.Column(spacing=20)

        self.build()
        self.update_view()

    def build(self):
        self.controls = [
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.on_back),
                ft.Text(f"Gerenciar: {self.championship.name}", style=ft.TextThemeStyle.HEADLINE_SMALL)
            ]),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(text="Participantes", content=self._build_participants_tab()),
                    ft.Tab(text="Fases e Mapas", content=self._build_stages_tab()),
                ],
                expand=True
            )
        ]

    def update_view(self):
        self.championship = self.service.get_championship_by_id(self.championship_id)
        self._update_participants_table()
        self._update_stages_list()
        if self.page: self.page.update()

    # --- Aba de Participantes ---
    def _build_participants_tab(self):
        return ft.Column([
            ft.Row([
                ft.ElevatedButton("Adicionar por Ranking", icon=ft.Icons.LEADERBOARD, on_click=self._open_add_by_rank_dialog),
                ft.ElevatedButton("Convidar Jogador", icon=ft.Icons.PERSON_ADD, on_click=self._open_invite_dialog),
                ft.ElevatedButton("Aprovar Todos", icon=ft.Icons.DONE_ALL, on_click=self._approve_all, bgcolor=AppColors.SUCCESS, color=AppColors.TEXT),
            ], wrap=True),
            self.participants_table
        ], expand=True, scroll=ft.ScrollMode.AUTO)

    def _update_participants_table(self):
        rows = []
        for p in self.championship.participants:
            status_color = {
                ParticipantStatus.PENDING: AppColors.WARNING,
                ParticipantStatus.APPROVED: AppColors.SUCCESS,
                ParticipantStatus.REJECTED: AppColors.ERROR
            }.get(p.status, AppColors.TEXT_SECONDARY)
            
            actions = []
            if p.status == ParticipantStatus.PENDING:
                actions.extend([
                    ft.IconButton(ft.Icons.CHECK, icon_color=AppColors.SUCCESS, on_click=lambda e, pid=p.id: self._update_status(pid, ParticipantStatus.APPROVED)),
                    ft.IconButton(ft.Icons.CLOSE, icon_color=AppColors.ERROR, on_click=lambda e, pid=p.id: self._update_status(pid, ParticipantStatus.REJECTED)),
                ])
            
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p.player_name)),
                ft.DataCell(ft.Text(p.status.value, color=status_color)),
                ft.DataCell(ft.Icon(ft.Icons.CHECK_BOX if p.checked_in else ft.Icons.CHECK_BOX_OUTLINE_BLANK, color=AppColors.SUCCESS if p.checked_in else AppColors.TEXT_SECONDARY)),
                ft.DataCell(ft.Row(actions)),
            ]))
        self.participants_table.rows = rows

    def _update_status(self, pid, status):
        self.service.update_participant_status(pid, status)
        self.update_view()

    def _approve_all(self, e):
        self.service.approve_all_participants(self.championship_id)
        self.update_view()

    def _open_add_by_rank_dialog(self, e):
        start_rank = ft.TextField(label="Rank Inicial", value="1", width=100)
        end_rank = ft.TextField(label="Rank Final", value="10", width=100)
        
        def confirm(e):
            try:
                s = int(start_rank.value)
                e = int(end_rank.value)
                self.service.add_participants_by_rank(self.championship_id, s, e)
                self.page.close(dlg)
                self.update_view()
            except Exception as ex:
                print(f"Erro: {ex}")

        dlg = ft.AlertDialog(
            title=ft.Text("Adicionar por Ranking BSBR"),
            content=ft.Row([start_rank, end_rank]),
            actions=[ft.TextButton("Adicionar", on_click=confirm)]
        )
        self.page.open(dlg)

    def _open_invite_dialog(self, e):
        # Dropdown com jogadores do DataManager para facilitar
        options = [ft.dropdown.Option(key=p['id'], text=p['name']) for p in DataManager.bsbr_data]
        player_dd = ft.Dropdown(label="Selecione o Jogador", options=options, width=300, enable_filter=True)
        
        def confirm(e):
            if player_dd.value:
                # Encontra o nome
                name = next((p['name'] for p in DataManager.bsbr_data if p['id'] == player_dd.value), "Unknown")
                self.service.add_participant_by_invite(self.championship_id, player_dd.value, name)
                self.page.close(dlg)
                self.update_view()

        dlg = ft.AlertDialog(
            title=ft.Text("Convidar Jogador"),
            content=player_dd,
            actions=[ft.TextButton("Convidar", on_click=confirm)]
        )
        self.page.open(dlg)

    # --- Aba de Fases e Mapas ---
    def _build_stages_tab(self):
        return ft.Column([
            ft.ElevatedButton("Adicionar Fase", icon=ft.Icons.ADD, on_click=self._open_add_stage_dialog),
            self.stages_column
        ], expand=True, scroll=ft.ScrollMode.AUTO)

    def _update_stages_list(self):
        controls = []
        for stage in self.championship.stages:
            maps_list = []
            for m in stage.maps_in_pool:
                maps_list.append(ft.ListTile(
                    leading=ft.Image(src=m.map_cover, width=40, height=40, border_radius=5) if m.map_cover else ft.Icon(ft.Icons.MUSIC_NOTE),
                    title=ft.Text(m.map_name or m.map_hash),
                    subtitle=ft.Text(m.difficulty)
                ))
            
            controls.append(ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(stage.name, style=ft.TextThemeStyle.TITLE_MEDIUM),
                            ft.Chip(ft.Text(stage.match_format.value)),
                            ft.IconButton(ft.Icons.ADD, tooltip="Adicionar Mapa", on_click=lambda e, sid=stage.id: self._open_add_map_dialog(sid))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Column(maps_list) if maps_list else ft.Text("Nenhum mapa adicionado.", color=AppColors.TEXT_SECONDARY)
                    ]),
                    padding=10
                )
            ))
        self.stages_column.controls = controls

    def _open_add_stage_dialog(self, e):
        name_field = ft.TextField(label="Nome da Fase (ex: Grupos)")
        order_field = ft.TextField(label="Ordem", value=str(len(self.championship.stages) + 1))
        format_dd = ft.Dropdown(
            label="Formato",
            options=[ft.dropdown.Option(key=f.name, text=f.value) for f in MatchFormat],
            value=MatchFormat.BO3.name
        )
        
        def confirm(e):
            try:
                self.service.add_stage_to_championship(
                    self.championship_id, name_field.value, int(order_field.value), MatchFormat[format_dd.value]
                )
                self.page.close(dlg)
                self.update_view()
            except Exception as ex:
                print(f"Erro: {ex}")

        dlg = ft.AlertDialog(
            title=ft.Text("Nova Fase"),
            content=ft.Column([name_field, order_field, format_dd], height=200),
            actions=[ft.TextButton("Criar", on_click=confirm)]
        )
        self.page.open(dlg)

    def _open_add_map_dialog(self, stage_id):
        # Idealmente, aqui teria uma busca no BeatSaver.
        # Por enquanto, vamos pedir o Hash e Diff manualmente.
        hash_field = ft.TextField(label="Map Hash (BeatSaver)")
        diff_field = ft.TextField(label="Dificuldade (ex: ExpertPlus)")
        
        def confirm(e):
            # Aqui poderíamos buscar metadados na API do BeatSaver
            self.service.add_map_to_stage_pool(stage_id, hash_field.value, diff_field.value)
            self.page.close(dlg)
            self.update_view()

        dlg = ft.AlertDialog(
            title=ft.Text("Adicionar Mapa"),
            content=ft.Column([hash_field, diff_field], height=150),
            actions=[ft.TextButton("Adicionar", on_click=confirm)]
        )
        self.page.open(dlg)
