import flet as ft
from app.colors import AppColors
from app.config import AppConfig

def AppDrawer(page: ft.Page):
    def drawer_change(e):
        idx = e.control.selected_index
        
        if idx == 0: # Inicio
            page.go("/")
        elif idx == 1: # Ranking
            page.go("/ranking")
        elif idx == 2: # Discord
            page.launch_url(AppConfig.DISCORD_LINK)
            e.control.selected_index = -1 
            page.update()
        elif idx == 3: # Sobre
            page.go("/about")
            pass
            
        page.close(page.drawer)

    return ft.NavigationDrawer(
        on_change=drawer_change,
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="Inicio",
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME, # Corrigido: selected_icon_content -> selected_icon
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Ranking",
                icon=ft.Icons.LEADERBOARD_OUTLINED,
                selected_icon=ft.Icons.LEADERBOARD, # Corrigido
            ),
            ft.NavigationDrawerDestination(
                label="Discord",
                icon=ft.Icons.DISCORD, 
                selected_icon=ft.Icons.DISCORD, # Corrigido
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Sobre",
                icon=ft.Icons.INFO_OUTLINED,
                selected_icon=ft.Icons.INFO, # Corrigido
            ),
        ],
        bgcolor=AppColors.SURFACE,
        indicator_color=AppColors.SURFACE,
    )
