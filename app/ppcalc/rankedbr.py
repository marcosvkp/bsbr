import requests
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

class ScoreSaberAPI:
    BASE_URL = "https://scoresaber.com/api"

    @staticmethod
    def get_player_full(player_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca o perfil completo de um jogador específico.
        
        Args:
            player_id (str): O ID do jogador no ScoreSaber.
            
        Returns:
            Optional[Dict[str, Any]]: Dicionário com os dados do jogador ou None se não for encontrado.
        """
        url = f"{ScoreSaberAPI.BASE_URL}/player/{player_id}/full"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Jogador com ID {player_id} não encontrado.")
            else:
                print(f"Erro HTTP ao buscar jogador {player_id}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão ao buscar jogador {player_id}: {e}")
            return None

    @staticmethod
    def get_players(country: str = "BR") -> List[Dict[str, Any]]:
        """
        Busca o ranking de jogadores de um país específico.
        """
        all_players = []
        page = 1
        
        while True:
            url = f"{ScoreSaberAPI.BASE_URL}/players"
            params = {
                "countries": country,
                "page": page,
                "withMetadata": "true"
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                players = data.get("players", [])
                if not players:
                    break
                    
                all_players.extend(players)
                
                metadata = data.get("metadata", {})
                total_items = metadata.get("total", 0)
                items_per_page = metadata.get("itemsPerPage", 0)
                
                if len(all_players) >= total_items or items_per_page == 0:
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Erro ao buscar jogadores página {page}: {e}")
                break
                
        return all_players

    @staticmethod
    def _fetch_page(leaderboard_id: int, country: str, page: int) -> List[Dict[str, Any]]:
        """
        Função auxiliar para buscar uma página específica.
        """
        url = f"{ScoreSaberAPI.BASE_URL}/leaderboard/by-id/{leaderboard_id}/scores"
        params = {
            "countries": country,
            "page": page
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("scores", [])
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar página {page} do leaderboard {leaderboard_id}: {e}")
            return []

    @staticmethod
    def get_leaderboard_scores(leaderboard_id: int, country: str = "BR", max_workers: int = 10) -> List[Dict[str, Any]]:
        """
        Busca TODOS os scores de um leaderboard específico filtrado por país.
        Utiliza multi-threading para buscar várias páginas simultaneamente.
        """
        url = f"{ScoreSaberAPI.BASE_URL}/leaderboard/by-id/{leaderboard_id}/scores"
        params = {"countries": country, "page": 1}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados iniciais do leaderboard {leaderboard_id}: {e}")
            return []

        all_scores = data.get("scores", [])
        metadata = data.get("metadata", {})
        
        total_items = metadata.get("total", 0)
        items_per_page = metadata.get("itemsPerPage", 0)
        
        if total_items == 0 or items_per_page == 0:
            return all_scores

        total_pages = math.ceil(total_items / items_per_page)
        
        if total_pages <= 1:
            return all_scores

        pages_to_fetch = range(2, total_pages + 1)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(ScoreSaberAPI._fetch_page, leaderboard_id, country, page): page 
                for page in pages_to_fetch
            }
            
            for future in as_completed(future_to_page):
                page_scores = future.result()
                all_scores.extend(page_scores)

        all_scores.sort(key=lambda x: x.get("rank", float('inf')))
        
        return all_scores
