import os
import flet as ft
from app.colors import AppColors
from app.views.home_view import HomeView
from app.views.ranking_view import RankingView
from app.views.player_view import PlayerView
from app.views.stars_ranking_view import StarsRankingView
from app.views.championship_view import ChampionshipsPublicView
from app.views.login_view import LoginView
from app.views.admin_view import AdminView
from app.views.profile_view import ProfileView
from app.components.app_bar import NavBar
from app.components.drawer import AppDrawer
from app.data.database import init_db
from app.data.data_manager import DataManager
from app.auth.auth_context import AuthContext
from app.auth.auth_service import AuthService

from fastapi import FastAPI
from fastapi.responses import FileResponse
from threading import Thread
import uvicorn

def main(page: ft.Page):
    page.title = "BeatSaber Brasil"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = AppColors.BACKGROUND

    init_db()
    AuthService.ensure_admin_exists()
    DataManager.start_background_updater()

    content_area = ft.Container(expand=True, alignment=ft.alignment.top_left)

    def page_resize(e):
        if page.appbar and len(page.appbar.actions) >= 2:
            is_mobile = page.width < 768
            page.appbar.actions[0].visible = is_mobile
        page.update()

    def route_change(e):
        page.appbar = NavBar(page)
        page.drawer = AppDrawer(page)
        
        troute = ft.TemplateRoute(page.route)
        
        # Reset alignment by default
        content_area.alignment = ft.alignment.top_left

        if troute.match("/"):
            content_area.content = HomeView(page)
        elif troute.match("/ranking"):
            content_area.content = RankingView(page)
        elif troute.match("/stars"):
            content_area.content = StarsRankingView(page)
        elif troute.match("/championships"):
            content_area.content = ChampionshipsPublicView()
        elif troute.match("/player/:player_id"):
            player_id = troute.player_id
            content_area.content = PlayerView(page, player_id)
        elif troute.match("/admin"):
            if AuthContext.is_admin(page):
                content_area.content = AdminView(page)
            else:
                content_area.alignment = ft.alignment.center
                content_area.content = ft.Text("Acesso Negado", size=30, color=AppColors.ERROR)
        elif troute.match("/profile"):
            if AuthContext.is_logged_in(page):
                content_area.alignment = ft.alignment.center
                content_area.content = ProfileView(page)
            else:
                content_area.alignment = ft.alignment.center
                content_area.content = ft.Text("Acesso Negado. Faça login para ver seu perfil.", size=20, color=AppColors.ERROR)
        elif troute.match("/login"):
            content_area.alignment = ft.alignment.center
            content_area.content = LoginView(page)
        else:
            content_area.content = HomeView(page)
            
        page.update()

    page.on_route_change = route_change
    page.add(content_area)
    page.go("/")
    page_resize(None)

fastapi_app = FastAPI()

@fastapi_app.get("/download/bsbr-playlist")
def download_bsbr_playlist():
    filepath = os.path.join("assets", "bsbr_ranked.bplist")
    return FileResponse(path=filepath, media_type="application/octet-stream", filename="bsbr_ranked.bplist")

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=9598, assets_dir="assets")
