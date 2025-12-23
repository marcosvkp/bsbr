import flet as ft
from app.colors import AppColors
from app.config import AppConfig

def AppDrawer(page: ft.Page):
    def drawer_change(e):
        # O índice do item selecionado
        idx = e.control.selected_index
        
        # Mapeamento simples baseado na ordem dos itens
        # 0: Inicio
        # 1: Ranking
        # 2: Discord
        # 3: Sobre
        
        if idx == 2: # Discord
            page.launch_url(AppConfig.DISCORD_LINK)
            # Opcional: Resetar a seleção ou manter onde estava antes
            e.control.selected_index = -1 
            page.update()
        else:
            print(f"Navegar para índice: {idx}")
            
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
                icon=ft.Icons.DISCORD, # Flet não tem ícone oficial do Discord no Material Icons padrão, usando um genérico ou similar se não houver
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
        indicator_color=AppColors.SURFACE,
    )
