import flet as ft
from app.colors import AppColors
from app.views.home_view import HomeView
from app.components.app_bar import NavBar
from app.components.drawer import AppDrawer

def main(page: ft.Page):
    page.title = "BeatSaber Brasil"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = AppColors.BACKGROUND

    # Configura o Drawer (Menu lateral para mobile)
    page.drawer = AppDrawer(page)

    # Cria a barra de navegação
    app_bar = NavBar(page)

    # Função para lidar com redimensionamento da janela
    def page_resize(e):
        is_mobile = page.width < 768 # Aumentei um pouco o breakpoint para tablets
        
        # Lógica de visibilidade
        if app_bar.title:
            app_bar.title.visible = not is_mobile
            
        # Actions[0] é o ícone do menu
        # Actions[1] é o container fantasma de equilíbrio
        if len(app_bar.actions) >= 2:
            app_bar.actions[0].visible = is_mobile # Menu icon
            app_bar.actions[1].visible = not is_mobile # Espaçador fantasma

        page.update()

    page.on_resized = page_resize

    # Conteúdo da página inicial
    home_content = HomeView(page)

    page.add(app_bar, home_content)
    
    # Chama o resize uma vez para ajustar o estado inicial
    page_resize(None)

ft.app(target=main)
