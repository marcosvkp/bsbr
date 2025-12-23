import flet as ft
from app.colors import AppColors

def AppDrawer(page: ft.Page):
    def drawer_change(e):
        print(f"Drawer mudou para: {e.control.selected_index}")
        page.close(page.drawer)

    return ft.NavigationDrawer(
        on_change=drawer_change,
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="Inicio",
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.HOME, color=AppColors.PRIMARY),
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Ranking",
                icon=ft.Icons.LEADERBOARD_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.LEADERBOARD, color=AppColors.PRIMARY),
            ),
            ft.NavigationDrawerDestination(
                label="Discord",
                icon=ft.Icons.DISCORD_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.DISCORD, color=AppColors.PRIMARY),
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Sobre",
                icon=ft.Icons.INFO_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.INFO, color=AppColors.PRIMARY),
            ),
        ],
        bgcolor=AppColors.SURFACE,
        indicator_color=AppColors.SURFACE, # Para não ficar com fundo estranho na seleção
    )
