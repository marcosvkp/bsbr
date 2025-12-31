import flet as ft
from app.colors import AppColors
from app.views.home_view import HomeView
from app.views.ranking_view import RankingView
from app.views.player_view import PlayerView
from app.views.stars_ranking_view import StarsRankingView
from app.components.app_bar import NavBar
from app.components.drawer import AppDrawer
from app.data.database import init_db
from app.data.data_manager import DataManager

def main(page: ft.Page):
    page.title = "BeatSaber Brasil"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = AppColors.BACKGROUND

    # Inicializa o Banco de Dados
    init_db()

    # Inicia o gerenciador de dados em background (Cache + Auto Update)
    DataManager.start_background_updater()

    # Configura o Drawer (Menu lateral para mobile)
    page.drawer = AppDrawer(page)

    # Cria a barra de navegação e atribui à propriedade appbar da página
    app_bar = NavBar(page)
    page.appbar = app_bar

    # Container principal que vai receber o conteúdo das views
    content_area = ft.Container(expand=True)

    # Função para lidar com redimensionamento da janela
    def page_resize(e):
        is_mobile = page.width < 768
        
        if app_bar.title:
            app_bar.title.visible = not is_mobile
            
        if len(app_bar.actions) >= 2:
            app_bar.actions[0].visible = is_mobile
            app_bar.actions[1].visible = not is_mobile

        page.update()

    page.on_resized = page_resize

    # Sistema de Rotas
    def route_change(e):
        troute = ft.TemplateRoute(page.route)
        
        if troute.match("/"):
            content_area.content = HomeView(page)
        elif troute.match("/ranking"):
            content_area.content = RankingView(page)
        elif troute.match("/stars"):
            content_area.content = StarsRankingView(page)
        elif troute.match("/player/:player_id"):
            # Extrai o ID da rota e passa para a view
            player_id = troute.player_id
            content_area.content = PlayerView(page, player_id)
        else:
            content_area.content = HomeView(page)
            
        page.update()

    page.on_route_change = route_change

    # Adiciona apenas a área de conteúdo à página
    page.add(content_area)
    
    # Força a navegação inicial para a Home
    page.go("/")
    
    # Chama o resize uma vez para ajustar o estado inicial
    page_resize(None)

ft.app(target=main, assets_dir="assets")
