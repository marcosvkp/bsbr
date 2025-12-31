import flet as ft
from app.colors import AppColors
from app.data.data_manager import DataManager
import math

def StarsRankingView(page: ft.Page):
    # --- Lógica de Processamento de Dados ---
    
    # Função auxiliar para processar scores
    def process_scores(only_br_maps=True):
        # Lista plana de todos os scores para processamento
        all_scores_flat = []
        
        # Se quisermos apenas mapas BR, precisamos filtrar os mapas permitidos
        allowed_maps = set()
        if only_br_maps:
            # DataManager.maps_data contém os mapas BR rankeados
            # Vamos criar um set de chaves (nome, diff, stars) para identificar mapas BR
            for m in DataManager.maps_data:
                # m tem: leaderboard_id, name, diff, stars, cover_image
                # O score salvo em player_details tem: map_name, diff, stars
                # Vamos usar essa tupla como chave
                allowed_maps.add((m["name"], m["diff"], m["stars"]))

        # Fonte de dados:
        # Se only_br_maps=True, usamos player_details (que tem scores BR)
        # Se only_br_maps=False, usamos global_scores_cache (que tem scores globais)
        
        source_data = DataManager.player_details if only_br_maps else DataManager.global_scores_cache
        
        # Se for global, a estrutura do dicionário é {player_id: [lista de scores]}
        # Se for BR, a estrutura é {player_id: {"scores": [lista], ...}}
        
        for player_id, details in source_data.items():
            player_name = "Desconhecido"
            player_avatar = None
            
            p_bsbr = next((p for p in DataManager.bsbr_data if p["id"] == player_id), None)
            if p_bsbr:
                player_name = p_bsbr["name"]
                player_avatar = p_bsbr["profilePicture"]
            else:
                p_ss = next((p for p in DataManager.scoresaber_data if p["id"] == player_id), None)
                if p_ss:
                    player_name = p_ss["name"]
                    player_avatar = p_ss["profilePicture"]
            
            scores_list = details["scores"] if only_br_maps else details
            
            for score in scores_list:
                map_key = (score["map_name"], score["diff"], score["stars"])
                
                # Se for para filtrar apenas mapas BR e o mapa não estiver na lista, pula
                if only_br_maps and map_key not in allowed_maps:
                    continue
                
                # Adiciona à lista plana com metadados do jogador
                all_scores_flat.append({
                    "player_name": player_name,
                    "player_avatar": player_avatar,
                    "pp": score["pp"],
                    "acc": score["acc"],
                    "stars": score["stars"],
                    "map_name": score["map_name"],
                    "diff": score["diff"],
                    "cover": score["map_cover"]
                })
        
        # --- Lógica idêntica ao script __init__.py ---
        
        # Dicionário para armazenar o melhor score por range de estrelas
        # Chave: range_start (float), Valor: score object
        best_scores_by_range = {}
        
        step = 0.5
        
        for score in all_scores_flat:
            try:
                stars_str = str(score["stars"]).replace("★", "")
                stars_val = float(stars_str)
            except ValueError:
                continue
            
            if stars_val == 0:
                continue
                
            # Calcular o índice do range (0.0, 0.5, 1.0, etc.)
            range_start = math.floor(stars_val / step) * step
            
            # Se ainda não tem score nesse range ou se o score atual tem mais PP
            if range_start not in best_scores_by_range:
                best_scores_by_range[range_start] = score
            else:
                if score["pp"] > best_scores_by_range[range_start]["pp"]:
                    best_scores_by_range[range_start] = score
        
        # Ordenar os ranges
        sorted_ranges = sorted(best_scores_by_range.keys())
        
        final_list = []
        for r_start in sorted_ranges:
            r_end = r_start + step
            score = best_scores_by_range[r_start]
            
            range_label = f"{r_start:.2f}-{r_end:.2f}"

            final_list.append({
                "range": range_label,
                "data": score
            })
            
        return final_list

    # Processa as duas listas
    br_maps_list = process_scores(only_br_maps=True)
    global_maps_list = process_scores(only_br_maps=False)
    
    # --- Componentes da UI ---
    
    def create_star_item(item):
        data = item["data"]
        range_label = item["range"]
        
        # Capa do Mapa
        cover = ft.Container(
            content=ft.Image(
                src=data["cover"] or "",
                width=60, height=60, border_radius=5, fit=ft.ImageFit.COVER,
                error_content=ft.Icon(ft.Icons.MUSIC_NOTE, color=AppColors.TEXT_SECONDARY)
            ),
            width=60, height=60, border_radius=5, clip_behavior=ft.ClipBehavior.HARD_EDGE
        )
        
        # Avatar do Jogador
        avatar = ft.Container(
            content=ft.Image(
                src=data["player_avatar"] or "",
                width=30, height=30, border_radius=15, fit=ft.ImageFit.COVER,
                error_content=ft.Icon(ft.Icons.PERSON, size=20, color=AppColors.TEXT_SECONDARY)
            ),
            width=30, height=30, border_radius=15, clip_behavior=ft.ClipBehavior.HARD_EDGE
        )
        
        return ft.Container(
            content=ft.ResponsiveRow(
                [
                    # Faixa de Estrelas
                    ft.Container(
                        content=ft.Text(range_label, color=AppColors.PRIMARY, weight=ft.FontWeight.BOLD, size=16),
                        col={"xs": 12, "sm": 2},
                        alignment=ft.alignment.center_left
                    ),
                    # Info Principal
                    ft.Container(
                        content=ft.Row(
                            [
                                cover,
                                ft.Column(
                                    [
                                        ft.Text(f"{data['pp']:.2f}pp", color=AppColors.SECONDARY, weight=ft.FontWeight.BOLD, size=14),
                                        ft.Text(f"{data['stars']}", color=AppColors.TEXT_SECONDARY, size=12),
                                    ],
                                    spacing=2
                                ),
                                ft.Column(
                                    [
                                        ft.Row([avatar, ft.Text(f"{data['player_name']}", color=AppColors.TEXT, weight=ft.FontWeight.BOLD, size=14)], spacing=5),
                                        ft.Text(f"{data['acc']:.2f}%", color=AppColors.TEXT_SECONDARY, size=12),
                                    ],
                                    spacing=2
                                )
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        col={"xs": 12, "sm": 6}
                    ),
                    # Nome do Mapa
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(data['map_name'], color=AppColors.TEXT, weight=ft.FontWeight.BOLD, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(data['diff'], color=AppColors.TEXT_SECONDARY, size=12)
                            ],
                            spacing=2,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        col={"xs": 12, "sm": 4},
                        alignment=ft.alignment.center_left
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                run_spacing=10
            ),
            padding=10, bgcolor=AppColors.SURFACE, border_radius=8, margin=ft.margin.only(bottom=5)
        )

    def create_list_view(data_list, empty_msg="Nenhum dado disponível."):
        if not data_list:
             return ft.Container(
                content=ft.Text(empty_msg, color=AppColors.TEXT_SECONDARY),
                alignment=ft.alignment.center,
                padding=20
            )
            
        return ft.Column(
            controls=[create_star_item(item) for item in data_list],
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    # Tabs para alternar entre as listas
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Mapas Brasileiros",
                content=ft.Container(
                    content=create_list_view(br_maps_list, "Nenhum mapa brasileiro rankeado encontrado."),
                    padding=ft.padding.only(top=10)
                )
            ),
            ft.Tab(
                text="ScoreSaber (Geral)",
                content=ft.Container(
                    content=create_list_view(global_maps_list, "Nenhum score global carregado. Aguarde a atualização."),
                    padding=ft.padding.only(top=10)
                )
            ),
        ],
        expand=True,
        indicator_color=AppColors.PRIMARY,
        label_color=AppColors.PRIMARY,
        unselected_label_color=AppColors.TEXT_SECONDARY,
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/ranking"), icon_color=AppColors.TEXT),
                        ft.Text("Stars Ranking (Top 1 PP)", size=20, weight=ft.FontWeight.BOLD, color=AppColors.TEXT),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Divider(color=AppColors.SURFACE),
                tabs
            ],
            expand=True
        ),
        padding=20,
        expand=True
    )
