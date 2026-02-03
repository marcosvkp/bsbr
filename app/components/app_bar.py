import flet as ft
from app.colors import AppColors
from app.config import AppConfig

def NavBar(page: ft.Page):
    def nav_click(e):
        print(f"Navegar para: {e.control.text}")

    def discord_click(e):
        page.launch_url(AppConfig.DISCORD_LINK)

    def open_drawer(e):
        page.open(page.drawer)

    # Botões de navegação (Desktop)
    nav_buttons = ft.Row(
        [
            ft.TextButton("Inicio", on_click=lambda _: page.go("/"), style=ft.ButtonStyle(color=AppColors.TEXT)),
            ft.TextButton("Ranking", on_click=lambda _: page.go("/ranking"), style=ft.ButtonStyle(color=AppColors.TEXT)),
            ft.TextButton("Star Ranking", on_click=lambda _: page.go("/stars"), style=ft.ButtonStyle(color=AppColors.TEXT)),
            ft.TextButton("Discord", on_click=discord_click, style=ft.ButtonStyle(color=AppColors.TEXT)),
            ft.TextButton("Sobre", on_click=lambda _: page.go("/about"), style=ft.ButtonStyle(color=AppColors.TEXT)),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Logo e Título (Lado Esquerdo)
    logo_title = ft.Row(
        [
            ft.Icon(ft.Icons.MUSIC_NOTE, color=AppColors.SECONDARY),
            ft.Text("BeatSaber Brasil", weight=ft.FontWeight.BOLD, color=AppColors.TEXT, size=20),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Menu para mobile (Lado Direito)
    # Importante: on_click chama a função para abrir o drawer
    menu_icon = ft.IconButton(ft.Icons.MENU, visible=False, icon_color=AppColors.TEXT, on_click=open_drawer)

    # Barra superior
    app_bar = ft.AppBar(
        # Leading: Logo e Título
        leading=ft.Container(content=logo_title, padding=ft.padding.only(left=10)),
        leading_width=220, 
        
        # Title: Botões centralizados
        title=nav_buttons,
        center_title=True,
        
        bgcolor=AppColors.SURFACE,
        
        # Actions: Menu Icon (Mobile) e um container vazio para equilibrar o layout se necessário no desktop
        actions=[
            menu_icon,
            # Container fantasma para equilibrar o leading no desktop e forçar o title ao centro real
            ft.Container(width=220, visible=True)
        ],
    )
    
    return app_bar
