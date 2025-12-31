import requests
import math
import time
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = Lock()

    def wait(self):
        with self.lock:
            now = time.time()
            # Remove chamadas antigas que já saíram da janela de tempo
            self.calls = [t for t in self.calls if t > now - self.period]
            
            if len(self.calls) >= self.max_calls:
                # Calcula quanto tempo precisa esperar até a chamada mais antiga expirar
                sleep_time = self.calls[0] + self.period - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Atualiza o tempo atual após o sleep e limpa novamente
                    now = time.time()
                    self.calls = [t for t in self.calls if t > now - self.period]
            
            self.calls.append(now)

# Global rate limiter: 350 calls per 60 seconds
rate_limiter = RateLimiter(350, 60)

class ScoreSaberAPI:
    BASE_URL = "https://scoresaber.com/api"

    @staticmethod
    def get_player_full(player_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca o perfil completo de um jogador específico.
        """
        url = f"{ScoreSaberAPI.BASE_URL}/player/{player_id}/full"
        
        try:
            rate_limiter.wait()
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
                rate_limiter.wait()
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
            rate_limiter.wait()
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
            rate_limiter.wait()
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

    @staticmethod
    def _fetch_player_scores_page(player_id: str, page: int, limit: int = 100, sort: str = "top") -> List[Dict[str, Any]]:
        """
        Busca uma página de scores de um jogador.
        """
        url = f"{ScoreSaberAPI.BASE_URL}/player/{player_id}/scores"
        params = {
            "limit": limit,
            "sort": sort,
            "page": page
        }
        try:
            rate_limiter.wait()
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 429:
                print(f"Rate limit atingido (429) para jogador {player_id} página {page}. Aguardando 5s...")
                time.sleep(5)
                rate_limiter.wait()
                response = requests.get(url, params=params, timeout=10)

            response.raise_for_status()
            data = response.json()
            return data.get("playerScores", [])
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar scores do jogador {player_id} página {page}: {e}")
            return []

    @staticmethod
    def get_player_scores(player_id: str, limit: int = 100, max_pages: Optional[int] = None, max_workers: int = 5, sort: str = "top") -> List[Dict[str, Any]]:
        """
        Busca os scores de um jogador.
        
        Args:
            player_id (str): ID do jogador.
            limit (int): Scores por página (máx 100).
            max_pages (Optional[int]): Quantas páginas buscar. Se None, busca todas.
            max_workers (int): Threads simultâneas.
            sort (str): 'top' ou 'recent'.
            
        Returns:
            List[Dict[str, Any]]: Lista de scores do jogador.
        """
        # Busca a primeira página para saber o total
        url = f"{ScoreSaberAPI.BASE_URL}/player/{player_id}/scores"
        params = {"limit": limit, "sort": sort, "page": 1}
        
        try:
            rate_limiter.wait()
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar scores iniciais do jogador {player_id}: {e}")
            return []

        all_scores = data.get("playerScores", [])
        metadata = data.get("metadata", {})
        
        total_items = metadata.get("total", 0)
        items_per_page = metadata.get("itemsPerPage", limit)
        
        if total_items == 0:
            return []

        # Calcula quantas páginas precisamos buscar
        total_pages_available = math.ceil(total_items / items_per_page)
        
        if max_pages is not None:
            pages_to_fetch_count = min(total_pages_available, max_pages)
        else:
            pages_to_fetch_count = total_pages_available
        
        if pages_to_fetch_count <= 1:
            return all_scores

        pages_to_fetch = range(2, pages_to_fetch_count + 1)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(ScoreSaberAPI._fetch_player_scores_page, player_id, page, limit, sort): page 
                for page in pages_to_fetch
            }
            
            for future in as_completed(future_to_page):
                page_scores = future.result()
                all_scores.extend(page_scores)

        # Ordena se necessário (se for top, já vem ordenado, mas threads podem embaralhar)
        if sort == "top":
            all_scores.sort(key=lambda x: x["score"]["pp"], reverse=True)
        # Se for recent, não necessariamente precisamos ordenar aqui, mas a API já manda ordenado por página
        
        return all_scores
