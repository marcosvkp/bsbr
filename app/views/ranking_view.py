import flet as ft
from app.colors import AppColors
from app.data.data_manager import DataManager
import math

def RankingView(page: ft.Page):
    # --- Carregamento de Dados do Cache ---
    
    # Lê diretamente do DataManager (Singleton)
    # Se os dados ainda estiverem carregando (primeira execução), as listas estarão vazias
    # Podemos mostrar um aviso se estiver vazio e carregando
    
    scoresaber_data = DataManager.scoresaber_data
    bsbr_data = DataManager.bsbr_data
    maps_data = DataManager.maps_data
    
    # Se não tiver dados e estiver carregando, podemos mostrar um loading (opcional)
    # Mas como o Flet constrói a UI, se estiver vazio vai mostrar "Nenhum dado encontrado"
    # O ideal seria um Timer na página para verificar se os dados chegaram e atualizar a UI,
    # mas para simplificar, vamos assumir que o usuário pode navegar e voltar ou recarregar.
    
    # Dica: Se quiser reatividade em tempo real quando os dados chegarem, precisaria usar PubSub ou um Timer.
    
    # --- Componentes de Item ---
    def create_ranking_item(pos, name, pp, color=AppColors.TEXT):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(f"#{pos}", weight=ft.FontWeight.BOLD, color=AppColors.SECONDARY, width=35),
                    ft.Text(name, weight=ft.FontWeight.BOLD, color=color, expand=True),
                    ft.Text(pp, color=AppColors.TEXT_SECONDARY, size=12),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.symmetric(vertical=5),
            border=ft.border.only(bottom=ft.BorderSide(1, AppColors.SURFACE))
        )

    def create_map_item(data):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(f"{data['name']} ({data['diff']})", weight=ft.FontWeight.BOLD, color=AppColors.TEXT),
                    ft.Text(f"Dificuldade: {data['stars']}", color=AppColors.SECONDARY, size=12),
                ],
                spacing=2
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
                    control = self.item_creator(item["pos"], item["name"], item["pp"], self.title_color)
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
