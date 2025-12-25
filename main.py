import flet as ft
from app.colors import AppColors
from app.views.home_view import HomeView
from app.views.ranking_view import RankingView
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
    # Isso vai começar a baixar os dados imediatamente sem travar a UI
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
        # Determina qual view mostrar baseado na rota
        if page.route == "/ranking":
            content_area.content = RankingView(page)
        else:
            content_area.content = HomeView(page)
            
        page.update()

    page.on_route_change = route_change

    # Adiciona apenas a área de conteúdo à página (a AppBar já está configurada na propriedade page.appbar)
    page.add(content_area)
    
    # Força a navegação inicial para a Home
    page.go("/")
    
    # Chama o resize uma vez para ajustar o estado inicial
    page_resize(None)

# Adicionado assets_dir="assets" para que o Flet encontre a pasta de imagens
ft.app(target=main, assets_dir="assets")
