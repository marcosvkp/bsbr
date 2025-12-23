import flet as ft
from app.colors import AppColors

def HomeView(page: ft.Page):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Ranking Brasileiro de Beat Saber", 
                    size=32, 
                    weight=ft.FontWeight.BOLD, 
                    color=AppColors.PRIMARY, # Verde
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Acompanhe o desempenho dos melhores jogadores do Brasil.", 
                    size=16, 
                    color=AppColors.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Ver Ranking", 
                    bgcolor=AppColors.SECONDARY, # Amarelo
                    color=AppColors.BACKGROUND, # Texto escuro no amarelo para contraste
                    icon=ft.Icons.LEADERBOARD,
                    icon_color=AppColors.BACKGROUND,
                    height=50,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
        padding=20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[AppColors.BACKGROUND, AppColors.SURFACE],
        )
    )
