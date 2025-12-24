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
                    "pos": player["countryRank"],
                    "name": player["name"],
                    "pp": f"{player['pp']}pp"
                })

            # 2. Ranking BR Customizado
            print("DataManager: Calculando Ranking BR Customizado...")
            bsbr_result = rank_calculator()
            
            new_bsbr = []
            for player in bsbr_result["ranking"]:
                new_bsbr.append({
                    "pos": player["rank"],
                    "name": player["name"],
                    "pp": f"{player['total_pp']:.2f}pp"
                })
            
            # 3. Mapas Rankeados (Vindo do Banco de Dados)
            print("DataManager: Buscando Mapas do Banco de Dados...")
            db = next(get_db())
            maps_db = db.query(RankedBRMaps).all()
            
            new_maps = []
            for m in maps_db:
                # Formata a dificuldade para exibição
                diff_name = m.difficulty.replace("Plus", "+") if m.difficulty else "?"
                new_maps.append({
                    "name": m.map_name,
                    "diff": diff_name,
                    "stars": f"{m.stars:.2f}★"
                })

            # Atualização Atômica (substitui as listas antigas pelas novas)
            with cls._lock:
                cls.scoresaber_data = new_scoresaber
                cls.bsbr_data = new_bsbr
                cls.maps_data = new_maps
                cls.last_updated = datetime.now()
                cls.is_loading = False
                print(f"DataManager: Dados atualizados com sucesso em {cls.last_updated}")

        except Exception as e:
            print(f"DataManager Erro Crítico: {e}")
            with cls._lock:
                cls.is_loading = False
