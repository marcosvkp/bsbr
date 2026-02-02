import flet as ft
from app.colors import AppColors
from app.config import AppConfig
from app.auth.auth_context import AuthContext

def NavBar(page: ft.Page):
    def discord_click(e):
        page.launch_url(AppConfig.DISCORD_LINK)

    def open_drawer(e):
        page.open(page.drawer)
        
    def handle_logout(e):
        AuthContext.logout(page)

    # --- Lógica de Controles Dinâmicos ---
    user = AuthContext.get_user(page)
    
    # Botões de navegação padrão
    nav_buttons_list = [
        ft.TextButton("Inicio", on_click=lambda _: page.go("/"), style=ft.ButtonStyle(color=AppColors.TEXT)),
        ft.TextButton("Ranking", on_click=lambda _: page.go("/ranking"), style=ft.ButtonStyle(color=AppColors.TEXT)),
        ft.TextButton("Star Ranking", on_click=lambda _: page.go("/stars"), style=ft.ButtonStyle(color=AppColors.TEXT)),
        ft.TextButton("Campeonatos", on_click=lambda _: page.go("/championships"), style=ft.ButtonStyle(color=AppColors.TEXT)),
    ]

    # Adiciona botão de Admin se o usuário for admin
    if AuthContext.is_admin(page):
        nav_buttons_list.append(
            ft.TextButton("Admin", on_click=lambda _: page.go("/admin"), style=ft.ButtonStyle(color=AppColors.PRIMARY))
        )

    # Adiciona botões de Discord e Sobre
    nav_buttons_list.extend([
        ft.TextButton("Discord", on_click=discord_click, style=ft.ButtonStyle(color=AppColors.TEXT)),
        ft.TextButton("Sobre", on_click=lambda _: page.go("/about"), style=ft.ButtonStyle(color=AppColors.TEXT)),
    ])

    nav_buttons = ft.Row(nav_buttons_list, alignment=ft.MainAxisAlignment.CENTER)

    # --- Controles de Usuário (Lado Direito) ---
    user_controls = []
    if user:
        # Menu de perfil para usuário logado
        user_menu = ft.PopupMenuButton(
            content=ft.Row([
                ft.Text(user.username, color=AppColors.TEXT),
                ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=AppColors.TEXT)
            ]),
            items=[
                ft.PopupMenuItem(text="Meu Perfil", icon=ft.Icons.PERSON, on_click=lambda _: page.go("/profile")),
                ft.PopupMenuItem(text="Logout", icon=ft.Icons.LOGOUT, on_click=handle_logout),
            ]
        )
        user_controls.append(user_menu)
    else:
        # Botão de Login para usuário não logado
        user_controls.append(
            ft.TextButton("Login", on_click=lambda _: page.go("/login"), style=ft.ButtonStyle(color=AppColors.TEXT))
        )

    # --- Montagem da AppBar ---
    logo_title = ft.Row(
        [
            ft.Icon(ft.Icons.MUSIC_NOTE, color=AppColors.SECONDARY),
            ft.Text("BeatSaber Brasil", weight=ft.FontWeight.BOLD, color=AppColors.TEXT, size=20),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    menu_icon = ft.IconButton(ft.Icons.MENU, visible=False, icon_color=AppColors.TEXT, on_click=open_drawer)

    app_bar = ft.AppBar(
        leading=ft.Container(content=logo_title, padding=ft.padding.only(left=10)),
        leading_width=220,
        title=nav_buttons,
        center_title=True,
        bgcolor=AppColors.SURFACE,
        actions=[
            menu_icon,
            ft.Row(user_controls, alignment=ft.MainAxisAlignment.END),
            ft.Container(width=180, visible=True)
        ],
    )
    
    return app_bar
