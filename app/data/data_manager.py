import threading
import time
from datetime import datetime
from app.ppcalc import rank_calculator
from app.ppcalc.rankedbr import ScoreSaberAPI
from app.data.database import get_db
from app.data.models.ranked_br_maps import RankedBRMaps
from collections import defaultdict

class DataManager:
    # Cache em memória
    scoresaber_data = []
    bsbr_data = []
    maps_data = []
    player_details = {}
    global_scores_cache = {} # Cache para scores globais: {player_id: [scores]}
    
    last_updated = None
    is_loading = False
    _lock = threading.Lock()

    @classmethod
    def start_background_updater(cls, interval_seconds=1800):
        def updater_loop():
            print("--- Iniciando atualização de dados em background ---")
            cls.update_all_data()
            while True:
                time.sleep(interval_seconds)
                print("--- Executando atualização periódica ---")
                cls.update_all_data()
        thread = threading.Thread(target=updater_loop, daemon=True)
        thread.start()

    @classmethod
    def update_all_data(cls):
        with cls._lock:
            cls.is_loading = True

        try:
            # 1. ScoreSaber Global/BR Oficial
            print("DataManager: Atualizando ScoreSaber...")
            raw_players = ScoreSaberAPI.get_players(country="BR")
            new_scoresaber = [{"id": p["id"], "profilePicture": p["profilePicture"], "pos": p["countryRank"], "name": p["name"], "pp": f"{p['pp']}pp"} for p in raw_players]

            # 2. Mapas Rankeados (Vindo do Banco de Dados)
            print("DataManager: Buscando Mapas do Banco de Dados...")
            db = next(get_db())
            maps_db = (
                db.query(RankedBRMaps)
                .order_by(
                    RankedBRMaps.map_name.asc(),# depois por nome
                    RankedBRMaps.stars.desc()  # primeiro ordena por estrelas (rating)
                )
                .all()
            )
            maps_lookup = {m.leaderboard_id: {"leaderboard_id": m.leaderboard_id, "name": m.map_name, "diff": m.difficulty.replace("Plus", "+") if m.difficulty else "?", "stars": f"{m.stars:.2f}★", "cover_image": m.cover_image} for m in maps_db}
            new_maps = list(maps_lookup.values())

            # 3. Ranking BR Customizado
            print("DataManager: Calculando Ranking BR Customizado...")
            bsbr_result = rank_calculator()
            
            new_bsbr = [{"pos": p["rank"], "name": p["name"], "id": p["id"], "profilePicture": p["profilePicture"], "pp": f"{p['total_pp']:.2f}pp"} for p in bsbr_result["ranking"]]
            
            # 4. Processamento Detalhado por Jogador (Mapas BR)
            new_player_details = defaultdict(lambda: {"scores": [], "total_medals": 0})
            map_scores = bsbr_result.get("map_scores", {})

            def medal_from_rank(rank: int):
                if rank == 1:
                    return 10
                elif rank == 2:
                    return 8
                elif rank == 3:
                    return 6
                elif rank == 4:
                    return 5
                elif rank == 5:
                    return 4
                elif rank == 6:
                    return 3
                elif rank == 7:
                    return 2
                elif rank > 7:
                    return 1
                else:
                    return 0
            
            for map_id, scores_list in map_scores.items():
                map_meta = maps_lookup.get(str(map_id), {})
                
                # A lista de scores já vem ordenada por rank da API
                for rank, score in enumerate(scores_list, 1):
                    pid = score["player_id"]
                    
                    # Adiciona medalhas
                    if rank <= 10:
                        new_player_details[pid]["total_medals"] += medal_from_rank(rank)
                    
                    # Adiciona o score à lista do jogador
                    new_player_details[pid]["scores"].append({
                        "map_name": map_meta.get("name", "Unknown Map"),
                        "map_cover": map_meta.get("cover_image"),
                        "diff": map_meta.get("diff", "?"),
                        "stars": map_meta.get("stars", "?"),
                        "acc": score["accuracy"],
                        "pp": score["pp"],
                        "score": score["score"],
                        "map_rank": rank # Adiciona a posição no mapa
                    })

            # Calcula o PP Ponderado para cada score
            for pid, details in new_player_details.items():
                # Ordena os scores por PP (maior para menor) para calcular o peso
                details["scores"].sort(key=lambda x: x["pp"], reverse=True)
                for i, score in enumerate(details["scores"]):
                    score["weighted_pp"] = score["pp"] * (0.965 ** i)

            # 5. Atualização de Scores Globais (Assíncrono/Sob demanda seria melhor, mas vamos tentar carregar para os top players)
            # Para evitar sobrecarga, vamos carregar apenas se a lista estiver vazia ou em intervalos maiores.
            # Por enquanto, vamos deixar o carregamento sob demanda na view ou carregar aqui para os top 50.
            print("DataManager: Iniciando busca de scores globais para Top 50...")
            new_global_scores = {}
            
            # Pega os top 50 do ranking BR oficial (ScoreSaber)
            # Para buscar scores globais, precisamos do ID do jogador.
            # raw_players já tem essa informação.
            top_players = raw_players[:50] # Usa raw_players para ter acesso a rankedPlayCount se disponível, ou apenas id
            
            # Função auxiliar para thread
            def fetch_player_global(player):
                pid = player["id"]
                try:
                    # Busca TODOS os scores (max_pages=None)
                    # Isso pode demorar, então cuidado com o rate limit
                    scores = ScoreSaberAPI.get_player_scores(pid, limit=100, max_pages=None)
                    processed_scores = []
                    for s in scores:
                        leaderboard = s["leaderboard"]
                        score_data = s["score"]
                        
                        # Ignora scores com 0 pp
                        if score_data["pp"] <= 0:
                            continue

                        processed_scores.append({
                            "map_name": leaderboard["songName"],
                            "map_cover": leaderboard["coverImage"],
                            "diff": leaderboard["difficulty"]["difficultyRaw"], # Ex: _ExpertPlus_SoloStandard
                            "stars": f"{leaderboard['stars']}★",
                            "acc": (score_data["baseScore"] / leaderboard["maxScore"]) * 100 if leaderboard["maxScore"] > 0 else 0,
                            "pp": score_data["pp"],
                            "score": score_data["baseScore"],
                            "map_rank": score_data["rank"]
                        })
                    return pid, processed_scores
                except Exception as e:
                    print(f"Erro ao buscar scores globais para {pid}: {e}")
                    return pid, []

            # Executa em paralelo
            from concurrent.futures import ThreadPoolExecutor, as_completed
            # Aumentei max_workers para 10 para agilizar, já que o rate limiter controla as requisições
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(fetch_player_global, p): p for p in top_players}
                for future in as_completed(futures):
                    pid, scores = future.result()
                    if scores:
                        new_global_scores[pid] = scores
                        print(f"DataManager: Scores globais carregados para {pid} ({len(scores)} scores)")

            # Atualização Atômica
            with cls._lock:
                cls.scoresaber_data = new_scoresaber
                cls.bsbr_data = new_bsbr
                cls.maps_data = new_maps
                cls.player_details = new_player_details
                cls.global_scores_cache = new_global_scores # Atualiza o cache global
                cls.last_updated = datetime.now()
                cls.is_loading = False
                print(f"DataManager: Dados atualizados com sucesso em {cls.last_updated}")

        except Exception as e:
            print(f"DataManager Erro Crítico: {e}")
            with cls._lock:
                cls.is_loading = False

    @classmethod
    def get_player_detail(cls, player_id):
        ss_info = next((p for p in cls.scoresaber_data if p["id"] == player_id), None)
        if not ss_info:
            ss_info = ScoreSaberAPI.get_player_full(player_id)
            if ss_info is None:
                return None
            ss_info["pos"] = 0

        bsbr_info = next((p for p in cls.bsbr_data if p["id"] == player_id), None)
        detail = cls.player_details.get(player_id)
        
        player_profile = {
            "info": {
                "name": ss_info["name"],
                "id": ss_info["id"],
                "profilePicture": ss_info["profilePicture"]
            },
            "scores": detail["scores"] if detail else [],
            "total_medals": detail["total_medals"] if detail else 0,
            "ss_rank": ss_info["pos"],
            "ss_pp": ss_info["pp"],
            "bsbr_rank": bsbr_info["pos"] if bsbr_info else "Sem Rank",
            "bsbr_pp": bsbr_info["pp"] if bsbr_info else "0pp",
            "profile_picture": ss_info["profilePicture"]
        }
        return player_profile
