import flet as ft
from app.colors import AppColors
from app.config import AppConfig
from app.auth.auth_context import AuthContext

def AppDrawer(page: ft.Page):
    
    destinations = [
        ft.NavigationDrawerDestination(label="Inicio", icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME),
        ft.NavigationDrawerDestination(label="Ranking", icon=ft.Icons.LEADERBOARD_OUTLINED, selected_icon=ft.Icons.LEADERBOARD),
        ft.NavigationDrawerDestination(label="Star Ranking", icon=ft.Icons.STAR, selected_icon=ft.Icons.LEADERBOARD),
        ft.NavigationDrawerDestination(label="Campeonatos", icon=ft.Icons.EMOJI_EVENTS_OUTLINED, selected_icon=ft.Icons.EMOJI_EVENTS),
    ]
    
    user = AuthContext.get_user(page)

    # Adiciona Admin se for admin
    if user and user.role == "admin":
        destinations.append(
            ft.NavigationDrawerDestination(label="Admin", icon=ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, selected_icon=ft.Icons.ADMIN_PANEL_SETTINGS)
        )
        
    destinations.extend([
        ft.NavigationDrawerDestination(label="Discord", icon=ft.Icons.DISCORD, selected_icon=ft.Icons.DISCORD),
        ft.NavigationDrawerDestination(label="Sobre", icon=ft.Icons.INFO_OUTLINED, selected_icon=ft.Icons.INFO),
    ])
    
    # Adiciona Login/Logout/Perfil
    if user:
        destinations.append(ft.Divider(thickness=2))
        destinations.append(ft.NavigationDrawerDestination(label="Meu Perfil", icon=ft.Icons.PERSON, selected_icon=ft.Icons.PERSON))
        destinations.append(ft.NavigationDrawerDestination(label="Logout", icon=ft.Icons.LOGOUT, selected_icon=ft.Icons.LOGOUT))
    else:
        destinations.append(ft.Divider(thickness=2))
        destinations.append(ft.NavigationDrawerDestination(label="Login", icon=ft.Icons.LOGIN, selected_icon=ft.Icons.LOGIN))

    def on_change(e):
        idx = e.control.selected_index
        if idx is None or idx >= len(destinations):
            return

        label = destinations[idx].label
        
        if label == "Inicio": page.go("/")
        elif label == "Ranking": page.go("/ranking")
        elif label == "Star Ranking": page.go("/stars")
        elif label == "Campeonatos": page.go("/championships")
        elif label == "Admin": page.go("/admin")
        elif label == "Discord": page.launch_url(AppConfig.DISCORD_LINK)
        elif label == "Sobre": page.go("/about")
        elif label == "Login": page.go("/login")
        elif label == "Meu Perfil": page.go("/profile")
        elif label == "Logout": AuthContext.logout(page)
            
        page.close(page.drawer)

    return ft.NavigationDrawer(
        on_change=on_change,
        controls=[
            ft.Container(height=12),
            *destinations,
        ],
        bgcolor=AppColors.SURFACE,
        indicator_color=AppColors.SURFACE,
    )
