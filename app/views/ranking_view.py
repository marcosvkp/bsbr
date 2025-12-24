import flet as ft
from app.colors import AppColors
from app.ppcalc import rank_calculator
import math

def RankingView(page: ft.Page):
    # --- Carregamento de Dados Reais ---
    # Nota: Em um app real, isso deveria ser assíncrono para não travar a UI
    # Por enquanto, vamos chamar diretamente, mas idealmente usaria um loading state
    
    # Dados fictícios para ScoreSaber e Mapas (ainda não implementados na API)
    def generate_ranking_data(prefix, count):
        return [
            {"pos": i + 1, "name": f"{prefix} Player {i + 1}", "pp": f"{20000 - (i * 100)}pp"}
            for i in range(count)
        ]

    def generate_maps_data(count):
        diffs = ["Expert+", "Expert", "Hard"]
        return [
            {"name": f"Beat Saber Map {i + 1}", "diff": diffs[i % 3], "stars": f"{12 - (i * 0.2):.1f}★"}
            for i in range(count)
        ]

    scoresaber_data = generate_ranking_data("Global", 50)
    maps_data = generate_maps_data(42)

    # Dados Reais do Ranking BR
    try:
        # Chama o calculador que baixa scores e processa
        # Isso pode demorar um pouco dependendo da quantidade de mapas
        bsbr_result = rank_calculator()
        raw_bsbr_ranking = bsbr_result["ranking"]
        
        # Formata para o padrão da view
        bsbr_data = []
        for player in raw_bsbr_ranking:
            bsbr_data.append({
                "pos": player["rank"],
                "name": player["name"],
                "pp": f"{player['total_pp']:.2f}pp"
            })
            
    except Exception as e:
        print(f"Erro ao calcular ranking BR: {e}")
        bsbr_data = [] # Fallback vazio ou erro visual

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
                self.list_column.controls = [ft.Text("Nenhum dado encontrado.", color=AppColors.TEXT_SECONDARY)]
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

    return ft.Column(
        [
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
