import requests
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

class ScoreSaberAPI:
    BASE_URL = "https://scoresaber.com/api"

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
        
        Args:
            leaderboard_id (int): O ID do leaderboard (mapa).
            country (str): Código do país (padrão "BR").
            max_workers (int): Número máximo de threads simultâneas.
            
        Returns:
            List[Dict[str, Any]]: Lista completa de scores dos jogadores.
        """
        # 1. Busca a primeira página para obter metadados (total de páginas)
        url = f"{ScoreSaberAPI.BASE_URL}/leaderboard/by-id/{leaderboard_id}/scores"
        params = {
            "countries": country,
            "page": 1
        }
        
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
        
        # Se não houver itens ou paginação, retorna o que temos
        if total_items == 0 or items_per_page == 0:
            return all_scores

        total_pages = math.ceil(total_items / items_per_page)
        
        if total_pages <= 1:
            return all_scores

        # 2. Se houver mais páginas, dispara threads para buscar o restante
        print(f"Encontradas {total_pages} páginas. Iniciando download multi-thread...")
        
        pages_to_fetch = range(2, total_pages + 1)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Mapeia cada future para o número da página (para debug se necessário)
            future_to_page = {
                executor.submit(ScoreSaberAPI._fetch_page, leaderboard_id, country, page): page 
                for page in pages_to_fetch
            }
            
            for future in as_completed(future_to_page):
                page_scores = future.result()
                all_scores.extend(page_scores)

        # 3. Ordena os scores pelo rank para garantir a consistência após o merge das threads
        # O rank vem da API, então confiamos nele.
        all_scores.sort(key=lambda x: x.get("rank", float('inf')))
        
        return all_scores

# Exemplo de uso:
# if __name__ == "__main__":
#     scores = ScoreSaberAPI.get_leaderboard_scores(684641)
#     print(f"Total de scores recuperados: {len(scores)}")
#     for score in scores[:5]:
#         print(f"#{score['rank']} - {score['leaderboardPlayerInfo']['name']}: {score['baseScore']}")
