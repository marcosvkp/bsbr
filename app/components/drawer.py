import flet as ft
from app.colors import AppColors
from app.config import AppConfig
from app.auth.auth_context import AuthContext

def AppDrawer(page: ft.Page):
    def drawer_change(e):
        idx = e.control.selected_index
        
        # Mapeamento de índices para ações
        # A ordem dos itens é dinâmica, então precisamos de uma lógica mais robusta
        # Mas para simplificar, vamos usar o texto do item selecionado se possível,
        # ou manter a ordem fixa e adicionar itens condicionalmente.
        
        # Vamos reconstruir a lógica baseada na ordem de inserção
        pass 

    # Como a lista é dinâmica, é melhor definir as ações diretamente nos itens ou usar um mapeamento
    # Mas o NavigationDrawer do Flet usa índices.
    # Vamos criar a lista de destinos dinamicamente.
    
    destinations = [
        ft.NavigationDrawerDestination(label="Inicio", icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME),
        ft.NavigationDrawerDestination(label="Ranking", icon=ft.Icons.LEADERBOARD_OUTLINED, selected_icon=ft.Icons.LEADERBOARD),
        ft.NavigationDrawerDestination(label="Star Ranking", icon=ft.Icons.STAR, selected_icon=ft.Icons.LEADERBOARD),
        ft.NavigationDrawerDestination(label="Campeonatos", icon=ft.Icons.EMOJI_EVENTS_OUTLINED, selected_icon=ft.Icons.EMOJI_EVENTS),
    ]
    
    # Adiciona Admin se for admin
    if AuthContext.is_admin(page):
        destinations.append(
            ft.NavigationDrawerDestination(label="Admin", icon=ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, selected_icon=ft.Icons.ADMIN_PANEL_SETTINGS)
        )
        
    destinations.extend([
        ft.NavigationDrawerDestination(label="Discord", icon=ft.Icons.DISCORD, selected_icon=ft.Icons.DISCORD),
        ft.NavigationDrawerDestination(label="Sobre", icon=ft.Icons.INFO_OUTLINED, selected_icon=ft.Icons.INFO),
    ])
    
    # Adiciona Login/Logout
    user = AuthContext.get_user(page)
    if user:
        destinations.append(ft.NavigationDrawerDestination(label="Logout", icon=ft.Icons.LOGOUT, selected_icon=ft.Icons.LOGOUT))
    else:
        destinations.append(ft.NavigationDrawerDestination(label="Login", icon=ft.Icons.LOGIN, selected_icon=ft.Icons.LOGIN))

    def on_change(e):
        # Obtém o label do item selecionado
        # Infelizmente o evento só dá o índice.
        # Vamos usar a lista `destinations` que criamos.
        idx = e.control.selected_index
        if idx < len(destinations):
            label = destinations[idx].label
            
            if label == "Inicio": page.go("/")
            elif label == "Ranking": page.go("/ranking")
            elif label == "Star Ranking": page.go("/stars")
            elif label == "Campeonatos": page.go("/championships")
            elif label == "Admin": page.go("/admin")
            elif label == "Discord": page.launch_url(AppConfig.DISCORD_LINK)
            elif label == "Sobre": page.go("/about")
            elif label == "Login": page.go("/login")
            elif label == "Logout": AuthContext.logout(page)
            
        page.close(page.drawer)

    return ft.NavigationDrawer(
        on_change=on_change,
        controls=[
            ft.Container(height=12),
            *destinations, # Desempacota a lista dinâmica
        ],
        bgcolor=AppColors.SURFACE,
        indicator_color=AppColors.SURFACE,
    )
