from app.ppcalc.rankedbr import ScoreSaberAPI
from app.scorecalc import get_pp, get_total_weighted_pp
from collections import defaultdict

def rank_calculator():
    # Importações tardias para evitar ciclos se necessário, ou apenas para seguir o padrão do usuário
    from app.data.database import get_db
    from app.data.models.ranked_br_maps import RankedBRMaps

    db = next(get_db())
    maps = db.query(RankedBRMaps).all()

    # Estrutura para armazenar os scores por mapa
    # map_id -> list of scores
    map_scores_data = {}

    # Estrutura para agrupar PPs por jogador
    # player_name -> list of pp values
    player_pps = defaultdict(list)
    
    # Estrutura para guardar info do jogador (para não perder o ID ou outros dados se precisar depois)
    # player_name -> player_info dict
    player_infos = {}

    for map_obj in maps:
        # Busca scores do mapa
        scores = ScoreSaberAPI.get_leaderboard_scores(map_obj.leaderboard_id)
        
        processed_scores = []
        
        for score in scores:
            # Calcula accuracy
            # Nota: modifiedScore pode ser 0 ou negativo em casos raros de falha, mas assumindo dados válidos
            if map_obj.max_score > 0:
                accuracy = (score['modifiedScore'] / map_obj.max_score) * 100
            else:
                accuracy = 0

            if 'NF' in score['modifiers']:
                continue
            
            # Calcula PP usando a função do scorecalc
            pp = get_pp(float(map_obj.stars), accuracy)
            
            player_name = score['leaderboardPlayerInfo']['name']
            player_id = score['leaderboardPlayerInfo']['id']
            
            # Armazena o PP na lista do jogador
            player_pps[player_name].append(pp)
            
            # Guarda info básica se ainda não tiver
            if player_name not in player_infos:
                player_infos[player_name] = {
                    "id": player_id,
                    "profilePicture": score['leaderboardPlayerInfo']['profilePicture'],
                    "name": player_name,
                    "country": score['leaderboardPlayerInfo'].get('country', 'BR')
                }

            # Adiciona ao resultado processado deste mapa
            processed_scores.append({
                "player_name": player_name,
                "player_id": player_id,
                "score": score['modifiedScore'],
                "timeSet": score['timeSet'],
                "accuracy": round(accuracy, 2),
                "pp": pp
            })
            
        # Salva os scores processados deste mapa
        map_scores_data[map_obj.leaderboard_id] = processed_scores

    # Calcula o ranking final
    final_ranking = []
    
    for player_name, pps in player_pps.items():
        # Ordena os PPs do maior para o menor antes de calcular o peso
        pps.sort(reverse=True)
        
        # Calcula o PP total ponderado
        total_pp = get_total_weighted_pp(pps)
        
        player_data = player_infos[player_name]
        player_data["total_pp"] = total_pp
        player_data["play_count"] = len(pps)
        
        final_ranking.append(player_data)

    # Ordena o ranking global pelo PP total
    final_ranking.sort(key=lambda x: x["total_pp"], reverse=True)
    
    # Adiciona a posição (rank)
    for i, player in enumerate(final_ranking):
        player["rank"] = i + 1

    return {
        "ranking": final_ranking,
        "map_scores": map_scores_data
    }
