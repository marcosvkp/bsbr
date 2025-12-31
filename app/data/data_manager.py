import threading
import time
from datetime import datetime
from app.ppcalc import rank_calculator
from app.ppcalc.rankedbr import ScoreSaberAPI
from app.data.database import get_db
from app.data.models.ranked_br_maps import RankedBRMaps
from app.data.models.player_score import PlayerScore
from collections import defaultdict
from sqlalchemy.orm import Session

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
        # Carrega dados do banco ao iniciar
        cls.load_from_db()
        
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
    def load_from_db(cls):
        """Carrega os scores salvos no banco para a memória."""
        print("DataManager: Carregando scores do banco de dados...")
        db = next(get_db())
        try:
            scores_db = db.query(PlayerScore).all()
            new_cache = defaultdict(list)
            
            for s in scores_db:
                new_cache[s.player_id].append(s.to_dict())
            
            with cls._lock:
                cls.global_scores_cache = dict(new_cache)
            print(f"DataManager: {len(scores_db)} scores carregados do banco.")
        except Exception as e:
            print(f"DataManager: Erro ao carregar do banco: {e}")
        finally:
            db.close()

    @classmethod
    def save_scores_to_db(cls, player_id, scores_list):
        """Salva ou atualiza scores no banco de dados."""
        db = next(get_db())
        try:
            # Para otimizar, vamos usar merge ou verificar existência
            # Como a lista pode ser grande, vamos fazer em batch se necessário
            # Mas o SQLAlchemy lida bem com merge
            
            for s in scores_list:
                # Cria objeto PlayerScore
                # Verifica se já existe (player_id + leaderboard_id)
                existing = db.query(PlayerScore).filter_by(player_id=player_id, leaderboard_id=s["leaderboard_id"]).first()
                
                if existing:
                    # Atualiza se o PP ou Score melhorou
                    if s["score"] > existing.score:
                        existing.pp = s["pp"]
                        existing.score = s["score"]
                        existing.acc = s["acc"]
                        existing.map_rank = s["map_rank"]
                        # Atualiza outros campos se necessário
                else:
                    new_score = PlayerScore(
                        player_id=player_id,
                        leaderboard_id=s["leaderboard_id"],
                        map_name=s["map_name"],
                        map_cover=s["map_cover"],
                        diff=s["diff"],
                        stars=s["stars"],
                        acc=s["acc"],
                        pp=s["pp"],
                        score=s["score"],
                        map_rank=s["map_rank"]
                    )
                    db.add(new_score)
            
            db.commit()
        except Exception as e:
            print(f"DataManager: Erro ao salvar scores de {player_id}: {e}")
            db.rollback()
        finally:
            db.close()

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
                    RankedBRMaps.map_name.asc(),
                    RankedBRMaps.stars.desc()
                )
                .all()
            )
            maps_lookup = {m.leaderboard_id: {"leaderboard_id": m.leaderboard_id, "name": m.map_name, "diff": m.difficulty.replace("Plus", "+") if m.difficulty else "?", "stars": f"{m.stars:.2f}★", "cover_image": m.cover_image} for m in maps_db}
            new_maps = list(maps_lookup.values())
            db.close()

            # 3. Ranking BR Customizado
            print("DataManager: Calculando Ranking BR Customizado...")
            bsbr_result = rank_calculator()
            
            new_bsbr = [{"pos": p["rank"], "name": p["name"], "id": p["id"], "profilePicture": p["profilePicture"], "pp": f"{p['total_pp']:.2f}pp"} for p in bsbr_result["ranking"]]
            
            # 4. Processamento Detalhado por Jogador (Mapas BR)
            new_player_details = defaultdict(lambda: {"scores": [], "total_medals": 0})
            map_scores = bsbr_result.get("map_scores", {})

            def medal_from_rank(rank: int):
                if rank == 1: return 10
                elif rank == 2: return 8
                elif rank == 3: return 6
                elif rank == 4: return 5
                elif rank == 5: return 4
                elif rank == 6: return 3
                elif rank == 7: return 2
                elif rank > 7: return 1
                else: return 0
            
            for map_id, scores_list in map_scores.items():
                map_meta = maps_lookup.get(str(map_id), {})
                for rank, score in enumerate(scores_list, 1):
                    pid = score["player_id"]
                    if rank <= 10:
                        new_player_details[pid]["total_medals"] += medal_from_rank(rank)
                    
                    new_player_details[pid]["scores"].append({
                        "map_name": map_meta.get("name", "Unknown Map"),
                        "map_cover": map_meta.get("cover_image"),
                        "diff": map_meta.get("diff", "?"),
                        "stars": map_meta.get("stars", "?"),
                        "acc": score["accuracy"],
                        "pp": score["pp"],
                        "score": score["score"],
                        "map_rank": rank
                    })

            for pid, details in new_player_details.items():
                details["scores"].sort(key=lambda x: x["pp"], reverse=True)
                for i, score in enumerate(details["scores"]):
                    score["weighted_pp"] = score["pp"] * (0.965 ** i)

            # 5. Atualização de Scores Globais (Inteligente)
            print("DataManager: Iniciando atualização inteligente de scores globais...")
            
            top_players = raw_players[:50]
            
            def fetch_and_save_player(player):
                pid = player["id"]
                
                # Verifica se já temos dados desse jogador no cache
                has_data = pid in cls.global_scores_cache and len(cls.global_scores_cache[pid]) > 0
                
                if has_data:
                    # Se já tem, busca apenas os RECENTES (ex: últimas 5 páginas ~ 400 scores)
                    # Isso deve cobrir as jogadas novas
                    print(f"Atualizando recentes para {player['name']}...")
                    scores = ScoreSaberAPI.get_player_scores(pid, limit=100, max_pages=5, sort="recent")
                else:
                    # Se não tem, busca TUDO (Top scores)
                    print(f"Baixando TUDO para {player['name']}...")
                    scores = ScoreSaberAPI.get_player_scores(pid, limit=100, max_pages=None, sort="top")
                
                processed_scores = []
                for s in scores:
                    leaderboard = s["leaderboard"]
                    score_data = s["score"]
                    
                    if score_data["pp"] <= 0: continue

                    processed_scores.append({
                        "leaderboard_id": leaderboard["id"],
                        "map_name": leaderboard["songName"],
                        "map_cover": leaderboard["coverImage"],
                        "diff": leaderboard["difficulty"]["difficultyRaw"],
                        "stars": f"{leaderboard['stars']}★",
                        "acc": (score_data["baseScore"] / leaderboard["maxScore"]) * 100 if leaderboard["maxScore"] > 0 else 0,
                        "pp": score_data["pp"],
                        "score": score_data["baseScore"],
                        "map_rank": score_data["rank"]
                    })
                
                if processed_scores:
                    cls.save_scores_to_db(pid, processed_scores)
                    return pid
                return None

            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(fetch_and_save_player, p): p for p in top_players}
                for future in as_completed(futures):
                    future.result()

            # Recarrega do banco para garantir consistência e atualizar o cache
            cls.load_from_db()

            # Atualização Atômica
            with cls._lock:
                cls.scoresaber_data = new_scoresaber
                cls.bsbr_data = new_bsbr
                cls.maps_data = new_maps
                cls.player_details = new_player_details
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
