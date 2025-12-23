import flet as ft
from app.colors import AppColors

def NavBar(page: ft.Page):
    def nav_click(e):
        print(f"Navegar para: {e.control.text}")

    def open_drawer(e):
        page.open(page.drawer)

    # Botões de navegação (Desktop)
    nav_buttons = ft.Row(
        [
            ft.TextButton("Inicio", on_click=nav_click, style=ft.ButtonStyle(color=AppColors.TEXT)),
            ft.TextButton("Ranking", on_click=nav_click, style=ft.ButtonStyle(color=AppColors.TEXT)),
            ft.TextButton("Discord", on_click=nav_click, style=ft.ButtonStyle(color=AppColors.TEXT)),
            ft.TextButton("Sobre", on_click=nav_click, style=ft.ButtonStyle(color=AppColors.TEXT)),
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
        # Para garantir centralização absoluta, o Flet às vezes precisa que o title ocupe tudo
        # Mas o AppBar do Material Design tem limitações.
        # Uma estratégia é usar actions para equilibrar ou usar um Container expandido.
        # Aqui, vamos confiar no center_title=True, mas garantir que a Row dos botões não tenha largura fixa restritiva.
        title=nav_buttons,
        center_title=True,
        
        bgcolor=AppColors.SURFACE,
        
        # Actions: Menu Icon (Mobile) e um container vazio para equilibrar o layout se necessário no desktop
        # Se quisermos centralização perfeita no desktop, precisamos "fingir" um peso igual na direita.
        # Mas como o leading tem 220px, podemos colocar um container de 220px na direita (actions) quando no desktop.
        actions=[
            menu_icon,
            # Container fantasma para equilibrar o leading no desktop e forçar o title ao centro real
            ft.Container(width=220, visible=True)
        ],
    )
    
    return app_bar
