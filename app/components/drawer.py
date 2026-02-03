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
        elif idx == 2: # Star Ranking
            page.go("/stars")
        elif idx == 3: # Campeonatos
            page.go("/championships")
        elif idx == 4: # Discord
            page.launch_url(AppConfig.DISCORD_LINK)
            e.control.selected_index = -1
            page.update()
        elif idx == 5: # Sobre
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
                selected_icon=ft.Icons.HOME,
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Ranking",
                icon=ft.Icons.LEADERBOARD_OUTLINED,
                selected_icon=ft.Icons.LEADERBOARD,
            ),
            ft.NavigationDrawerDestination(
                label="Star Ranking",
                icon=ft.Icons.STAR,
                selected_icon=ft.Icons.LEADERBOARD,
            ),
            ft.NavigationDrawerDestination(
                label="Campeonatos",
                icon=ft.Icons.EMOJI_EVENTS_OUTLINED,
                selected_icon=ft.Icons.EMOJI_EVENTS,
            ),
            ft.NavigationDrawerDestination(
                label="Discord",
                icon=ft.Icons.DISCORD, 
                selected_icon=ft.Icons.DISCORD,
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Sobre",
                icon=ft.Icons.INFO_OUTLINED,
                selected_icon=ft.Icons.INFO,
            ),
        ],
        bgcolor=AppColors.SURFACE,
        indicator_color=AppColors.SURFACE,
    )
