import flet as ft
from app.colors import AppColors
from app.data.data_manager import DataManager
import math

def RankingView(page: ft.Page):
    # --- Carregamento de Dados do Cache ---
    scoresaber_data = DataManager.scoresaber_data
    bsbr_data = DataManager.bsbr_data
    maps_data = DataManager.maps_data

    def page_go_update(player_id):
        page.launch_url(f"https://scoresaber.com/u/{player_id}")
        page.update()
    
    # --- Componentes de Item ---
    def create_ranking_item(pos, name, pp, profile_picture=None, player_id=None, color=AppColors.TEXT):
        # Cria o avatar (imagem ou ícone padrão)
        avatar_content = ft.Icon(ft.Icons.PERSON, color=AppColors.TEXT_SECONDARY)
        if profile_picture:
            avatar_content = ft.Image(
                src=profile_picture,
                width=30,
                height=30,
                border_radius=ft.border_radius.all(15), # Redondo
                fit=ft.ImageFit.COVER,
                error_content=ft.Icon(ft.Icons.PERSON, color=AppColors.TEXT_SECONDARY)
            )
        
        avatar_container = ft.Container(
            content=avatar_content,
            width=30,
            height=30,
            border_radius=15,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        # Botão ScoreSaber (Logo SVG Local)
        ss_button = ft.Container(
            content=ft.Image(
                src="/scoresaber_logo.png",
                width=15,
                height=15,
                fit=ft.ImageFit.CONTAIN,
                color=AppColors.TEXT if page.theme_mode == ft.ThemeMode.LIGHT else None 
            ),
            on_click=lambda e: page.launch_url(f"https://scoresaber.com/u/{player_id}") if player_id else None,
            tooltip="Ver perfil no ScoreSaber",
            padding=5,
            border_radius=5,
            ink=True, 
        )

        # Botão Brasil (Perfil Local - Futuro)
        br_button = ft.Container(
            content=ft.Image(
                src="/br.png",
                width=15,
                height=15,
                fit=ft.ImageFit.CONTAIN,
                color=AppColors.TEXT if page.theme_mode == ft.ThemeMode.LIGHT else None
            ),
            on_click=lambda e: page.go(f"/player/{player_id}") if player_id else None,
            tooltip="Ver perfil no BSBR",
            padding=5,
            border_radius=5,
            ink=True,
        )

        return ft.Container(
            content=ft.Row(
                [
                    # Posição
                    ft.Text(f"#{pos}", weight=ft.FontWeight.BOLD, color=AppColors.SECONDARY, width=35),
                    
                    # Avatar + Nome + Botões
                    ft.Row(
                        [
                            avatar_container,
                            ft.Container(width=10), 
                            ft.Text(name, weight=ft.FontWeight.BOLD, color=color, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Container(width=10), 
                            br_button,
                            ss_button,
                        ],
                        expand=True,
                        spacing=0, 
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    
                    # PP
                    ft.Text(pp, color=AppColors.TEXT_SECONDARY, size=12),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.symmetric(vertical=5),
            border=ft.border.only(bottom=ft.BorderSide(1, AppColors.SURFACE))
        )

    def create_map_item(data):
        # Cria a imagem de capa (quadrada com bordas arredondadas)
        cover_content = ft.Icon(ft.Icons.MUSIC_NOTE, color=AppColors.TEXT_SECONDARY)
        if data.get('cover_image'):
            cover_content = ft.Image(
                src=data['cover_image'],
                width=40,
                height=40,
                border_radius=ft.border_radius.all(5),
                fit=ft.ImageFit.COVER,
                error_content=ft.Icon(ft.Icons.MUSIC_NOTE, color=AppColors.TEXT_SECONDARY)
            )
            
        cover_container = ft.Container(
            content=cover_content,
            width=40,
            height=40,
            border_radius=5,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        return ft.Container(
            content=ft.Row(
                [
                    # Capa
                    cover_container,
                    
                    # Espaçamento
                    ft.Container(width=10),
                    
                    # Informações do Mapa
                    ft.Column(
                        [
                            ft.Text(f"{data['name']}", weight=ft.FontWeight.BOLD, color=AppColors.TEXT, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Row(
                                [
                                    ft.Text(f"{data['diff']}", color=AppColors.SECONDARY, size=12),
                                    ft.Text("•", color=AppColors.TEXT_SECONDARY, size=12),
                                    ft.Text(f"{data['stars']}", color=AppColors.SECONDARY, size=12, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=5
                            )
                        ],
                        spacing=2,
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.symmetric(vertical=5),
            border=ft.border.only(bottom=ft.BorderSide(1, AppColors.SURFACE))
        )

    # --- Lógica de Paginação ---
    class PaginatedSection(ft.Container):
        def __init__(self, title, icon, data, item_creator_func, items_per_page=10, title_color=AppColors.TEXT, is_ranking=True):
            super().__init__()
            self.title = title
            self.icon = icon
            self.all_data = data
            self.item_creator = item_creator_func
            self.items_per_page = items_per_page
            self.current_page = 1
            self.title_color = title_color
            self.is_ranking = is_ranking
            
            self.total_pages = math.ceil(len(self.all_data) / self.items_per_page) if self.all_data else 1
            
            self.list_column = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)
            self.page_info = ft.Text(f"Página 1/{self.total_pages}", size=12, color=AppColors.TEXT_SECONDARY)
            self.btn_prev = ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=self.prev_page, disabled=True, icon_color=AppColors.TEXT)
            self.btn_next = ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=self.next_page, disabled=self.total_pages <= 1, icon_color=AppColors.TEXT)

            self.bgcolor = AppColors.SURFACE
            self.padding = 20
            self.border_radius = 10
            self.col = {"sm": 12, "md": 4}
            self.height = 600

            self.update_list_view()
            
            self.content = ft.Column(
                [
                    ft.Row([
                        ft.Icon(self.icon, color=self.title_color),
                        ft.Text(self.title, size=20, weight=ft.FontWeight.BOLD, color=self.title_color)
                    ]),
                    ft.Divider(color=self.title_color if self.title_color != AppColors.TEXT else AppColors.TEXT_SECONDARY),
                    
                    ft.Container(content=self.list_column, expand=True),
                    
                    ft.Divider(color=AppColors.SURFACE),
                    
                    ft.Row(
                        [
                            self.btn_prev,
                            self.page_info,
                            self.btn_next
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ]
            )

        def update_list_view(self):
            if not self.all_data:
                msg = "Carregando dados..." if DataManager.is_loading else "Nenhum dado encontrado."
                self.list_column.controls = [
                    ft.Container(
                        content=ft.Column([
                            ft.ProgressRing() if DataManager.is_loading else ft.Icon(ft.Icons.WARNING_AMBER, color=AppColors.TEXT_SECONDARY),
                            ft.Text(msg, color=AppColors.TEXT_SECONDARY)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                ]
                return

            start = (self.current_page - 1) * self.items_per_page
            end = start + self.items_per_page
            current_items = self.all_data[start:end]
            
            self.list_column.controls.clear()
            for item in current_items:
                if self.is_ranking:
                    pfp = item.get("profilePicture")
                    pid = item.get("id")
                    control = self.item_creator(item["pos"], item["name"], item["pp"], pfp, pid, self.title_color)
                else:
                    control = self.item_creator(item)
                self.list_column.controls.append(control)
            
            self.page_info.value = f"Página {self.current_page}/{self.total_pages}"
            self.btn_prev.disabled = self.current_page == 1
            self.btn_next.disabled = self.current_page == self.total_pages

        def prev_page(self, e):
            if self.current_page > 1:
                self.current_page -= 1
                self.update_list_view()
                self.content.update()

        def next_page(self, e):
            if self.current_page < self.total_pages:
                self.current_page += 1
                self.update_list_view()
                self.content.update()

    # --- Instanciação das Colunas ---
    
    score_saber_col = PaginatedSection(
        title="ScoreSaber",
        icon=ft.Icons.PUBLIC,
        data=scoresaber_data,
        item_creator_func=create_ranking_item,
        items_per_page=8,
        title_color=AppColors.TEXT
    )

    bsbr_col = PaginatedSection(
        title="Ranking BR",
        icon=ft.Icons.FLAG,
        data=bsbr_data,
        item_creator_func=create_ranking_item,
        items_per_page=8,
        title_color=AppColors.PRIMARY
    )

    maps_col = PaginatedSection(
        title="Mapas Ranqueados",
        icon=ft.Icons.MAP,
        data=maps_data,
        item_creator_func=create_map_item,
        items_per_page=6,
        title_color=AppColors.SECONDARY,
        is_ranking=False
    )

    # Adiciona um botão de refresh manual ou info de última atualização
    last_update_text = "Atualizando..."
    if DataManager.last_updated:
        last_update_text = f"Última atualização: {DataManager.last_updated.strftime('%H:%M:%S')}"
    
    return ft.Column(
        [
            ft.Container(
                content=ft.Text(last_update_text, size=12, color=AppColors.TEXT_SECONDARY),
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(right=20, top=10)
            ),
            ft.Divider(color=AppColors.SURFACE),
            ft.ResponsiveRow(
                [
                    score_saber_col,
                    bsbr_col,
                    maps_col
                ],
                spacing=20,
                run_spacing=20,
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
    )
