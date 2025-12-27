import threading
import time
from datetime import datetime
from app.ppcalc import rank_calculator
from app.ppcalc.rankedbr import ScoreSaberAPI
from app.data.database import get_db
from app.data.models.ranked_br_maps import RankedBRMaps

class DataManager:
    # Cache em memória (variáveis de classe funcionam como Singleton neste contexto)
    scoresaber_data = []
    bsbr_data = []
    maps_data = []
    
    # Novo: Cache detalhado por jogador para a tela de perfil
    # player_id -> { "scores": [...], "info": {...} }
    player_details = {}
    
    last_updated = None
    is_loading = False
    _lock = threading.Lock()

    @classmethod
    def start_background_updater(cls, interval_seconds=1800): # 30 minutos padrão
        """Inicia a thread que atualiza os dados periodicamente."""
        def updater_loop():
            # Executa imediatamente na primeira vez
            print("--- Iniciando atualização de dados em background ---")
            cls.update_all_data()
            
            while True:
                time.sleep(interval_seconds)
                print("--- Executando atualização periódica ---")
                cls.update_all_data()

        # daemon=True garante que a thread morra quando o app fechar
        thread = threading.Thread(target=updater_loop, daemon=True)
        thread.start()

    @classmethod
    def update_all_data(cls):
        """Busca e processa todos os dados, atualizando o cache de forma segura."""
        with cls._lock:
            cls.is_loading = True

        try:
            # 1. ScoreSaber Global/BR Oficial
            print("DataManager: Atualizando ScoreSaber...")
            raw_players = ScoreSaberAPI.get_players(country="BR")
            new_scoresaber = []
            for player in raw_players:
                new_scoresaber.append({
                    "id": player["id"],
                    "profilePicture": player["profilePicture"],
                    "pos": player["countryRank"],
                    "name": player["name"],
                    "pp": f"{player['pp']}pp"
                })

            # 2. Mapas Rankeados (Vindo do Banco de Dados)
            print("DataManager: Buscando Mapas do Banco de Dados...")
            db = next(get_db())
            maps_db = db.query(RankedBRMaps).all()
            
            maps_lookup = {}
            new_maps = []
            for m in maps_db:
                diff_name = m.difficulty.replace("Plus", "+") if m.difficulty else "?"
                map_info = {
                    "leaderboard_id": m.leaderboard_id,
                    "name": m.map_name,
                    "diff": diff_name,
                    "stars": f"{m.stars:.2f}★",
                    "cover_image": m.cover_image
                }
                new_maps.append(map_info)
                maps_lookup[m.leaderboard_id] = map_info

            # 3. Ranking BR Customizado
            print("DataManager: Calculando Ranking BR Customizado...")
            bsbr_result = rank_calculator()
            
            new_bsbr = []
            new_player_details = {}

            for player in bsbr_result["ranking"]:
                new_bsbr.append({
                    "pos": player["rank"],
                    "name": player["name"],
                    "id": player["id"],
                    "profilePicture": player["profilePicture"],
                    "pp": f"{player['total_pp']:.2f}pp"
                })

            map_scores = bsbr_result.get("map_scores", {})
            
            for map_id, scores_list in map_scores.items():
                map_meta = maps_lookup.get(str(map_id), {})
                
                for score in scores_list:
                    pid = score["player_id"]
                    
                    if pid not in new_player_details:
                        new_player_details[pid] = {
                            "scores": [],
                            "name": score["player_name"],
                            "id": pid,
                        }
                    
                    new_player_details[pid]["scores"].append({
                        "map_name": map_meta.get("name", "Unknown Map"),
                        "map_cover": map_meta.get("cover_image"),
                        "diff": map_meta.get("diff", "?"),
                        "stars": map_meta.get("stars", "?"),
                        "acc": score["accuracy"],
                        "pp": score["pp"],
                        "score": score["score"]
                    })

            for pid in new_player_details:
                new_player_details[pid]["scores"].sort(key=lambda x: x["pp"], reverse=True)

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
        """Retorna os detalhes completos de um jogador pelo ID."""
        
        # A fonte da verdade para a existência de um jogador é a lista do ScoreSaber
        ss_info = next((p for p in cls.scoresaber_data if p["id"] == player_id), None)
        
        if not ss_info:
            return None

        # Agora, buscamos dados opcionais
        bsbr_info = next((p for p in cls.bsbr_data if p["id"] == player_id), None)
        detail = cls.player_details.get(player_id)

        print(ss_info)
        
        # Monta o perfil final
        player_profile = {
            "info": {
                "name": ss_info["name"],
                "id": ss_info["id"],
                "profilePicture": ss_info["profilePicture"]
            },
            "scores": detail["scores"] if detail else [],
            "ss_rank": ss_info["pos"],
            "ss_pp": ss_info["pp"],
            "bsbr_rank": bsbr_info["pos"] if bsbr_info else "Sem Rank",
            "bsbr_pp": bsbr_info["pp"] if bsbr_info else "0pp",
            "profile_picture": ss_info["profilePicture"]
        }
        
        return player_profile
