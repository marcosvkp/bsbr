import flet as ft
from app.colors import AppColors
from app.data.data_manager import DataManager
import math

def PlayerView(page: ft.Page, player_id: str):
    # Busca dados do jogador no DataManager
    player_data = DataManager.get_player_detail(player_id)
    
    if not player_data:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=AppColors.SECONDARY),
                    ft.Text("Jogador não encontrado.", color=AppColors.TEXT_SECONDARY)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True
        )

    info = player_data["info"]
    scores = player_data["scores"]
    
    # --- Cabeçalho do Perfil ---
    profile_header = ft.Container(
        content=ft.Column(
            [
                # Avatar Grande
                ft.Container(
                    content=ft.Image(
                        src=player_data["profile_picture"] or "",
                        width=120,
                        height=120,
                        border_radius=60,
                        fit=ft.ImageFit.COVER,
                        error_content=ft.Icon(ft.Icons.PERSON, size=60, color=AppColors.TEXT_SECONDARY)
                    ),
                    border=ft.border.all(3, AppColors.PRIMARY),
                    border_radius=65,
                    padding=5
                ),
                ft.Text(info["name"], size=32, weight=ft.FontWeight.BOLD, color=AppColors.TEXT),
                
                # Badges de Ranking
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Row([
                                ft.Image(src="/br.png", width=20, height=20, fit=ft.ImageFit.CONTAIN),
                                ft.Text("BSBR Rank:", color=AppColors.TEXT_SECONDARY, size=14),
                                ft.Text(f"#{player_data['bsbr_rank']}", color=AppColors.PRIMARY, weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"({player_data['bsbr_pp']})", color=AppColors.TEXT_SECONDARY, size=12)
                            ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=AppColors.SURFACE,
                            padding=10,
                            border_radius=8
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Image(src="/scoresaber_logo.png", width=20, height=20, fit=ft.ImageFit.CONTAIN),
                                ft.Text("SS BR Rank:", color=AppColors.TEXT_SECONDARY, size=14),
                                ft.Text(f"#{player_data['ss_rank']}", color=AppColors.SECONDARY, weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"({player_data['ss_pp']})", color=AppColors.TEXT_SECONDARY, size=12)
                            ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=AppColors.SURFACE,
                            padding=10,
                            border_radius=8
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        ),
        padding=30,
        alignment=ft.alignment.center
    )

    # --- Componente de Item de Score ---
    def create_score_item(score):
        cover = ft.Container(
            content=ft.Image(
                src=score["map_cover"] or "",
                width=50, height=50, border_radius=5, fit=ft.ImageFit.COVER,
                error_content=ft.Icon(ft.Icons.MUSIC_NOTE, color=AppColors.TEXT_SECONDARY)
            ),
            width=50, height=50, border_radius=5, clip_behavior=ft.ClipBehavior.HARD_EDGE
        )
        
        return ft.Container(
            content=ft.Row(
                [
                    cover,
                    ft.Container(width=10),
                    ft.Column(
                        [
                            ft.Text(score["map_name"], weight=ft.FontWeight.BOLD, color=AppColors.TEXT, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Row(
                                [
                                    ft.Text(score["diff"], color=AppColors.SECONDARY, size=12),
                                    ft.Text("•", color=AppColors.TEXT_SECONDARY),
                                    ft.Text(score["stars"], color=AppColors.SECONDARY, size=12, weight=ft.FontWeight.BOLD)
                                ],
                                spacing=5
                            )
                        ],
                        expand=True, spacing=2
                    ),
                    ft.Column(
                        [
                            ft.Text(f"{score['pp']:.2f}pp", weight=ft.FontWeight.BOLD, color=AppColors.PRIMARY, size=16),
                            ft.Text(f"{score['acc']:.2f}%", color=AppColors.TEXT_SECONDARY, size=12)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=10, bgcolor=AppColors.SURFACE, border_radius=8, margin=ft.margin.only(bottom=5)
        )

    # --- Lógica de Paginação para Scores ---
    class PaginatedScores(ft.Column):
        def __init__(self, all_scores, items_per_page=5):
            super().__init__()
            self.all_scores = all_scores
            self.items_per_page = items_per_page
            self.current_page = 1
            self.total_pages = math.ceil(len(self.all_scores) / self.items_per_page) if self.all_scores else 1
            
            self.list_view = ft.Column(spacing=5)
            self.page_info = ft.Text(f"Página 1/{self.total_pages}", size=12, color=AppColors.TEXT_SECONDARY)
            self.btn_prev = ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=self.prev_page, disabled=True)
            self.btn_next = ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=self.next_page, disabled=self.total_pages <= 1)
            
            self.controls = [
                ft.Container(content=self.list_view, expand=True),
                ft.Row(
                    [self.btn_prev, self.page_info, self.btn_next],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ]
            self.expand = True
            self.update_view()

        def update_view(self):
            if not self.all_scores:
                self.list_view.controls = [ft.Text("Nenhum mapa brasileiro jogado.", color=AppColors.TEXT_SECONDARY)]
                self.page_info.visible = False
                self.btn_prev.visible = False
                self.btn_next.visible = False
                return

            start = (self.current_page - 1) * self.items_per_page
            end = start + self.items_per_page
            current_items = self.all_scores[start:end]
            
            self.list_view.controls = [create_score_item(s) for s in current_items]
            
            self.page_info.value = f"Página {self.current_page}/{self.total_pages}"
            self.btn_prev.disabled = self.current_page == 1
            self.btn_next.disabled = self.current_page == self.total_pages
            
        def prev_page(self, e):
            if self.current_page > 1:
                self.current_page -= 1
                self.update_view()
                self.update()

        def next_page(self, e):
            if self.current_page < self.total_pages:
                self.current_page += 1
                self.update_view()
                self.update()

    # --- Layout Final da Página ---
    return ft.Container(
        content=ft.Column(
            [
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/ranking"), icon_color=AppColors.TEXT),
                profile_header,
                ft.Divider(color=AppColors.SURFACE),
                ft.Text("Mapas Brasileiros Jogados", size=20, weight=ft.FontWeight.BOLD, color=AppColors.TEXT),
                ft.Container(height=10),
                PaginatedScores(scores)
            ],
            expand=True,
        ),
        padding=20
    )
