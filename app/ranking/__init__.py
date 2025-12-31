import requests
import json
import time
import concurrent.futures
from threading import Lock
import sys
import math

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

# Limite de 350 requisições por 60 segundos (gap de segurança para o limite de 400)
rate_limiter = RateLimiter(350, 60)

def get_scores_for_player(player):
    player_id = player["id"]
    player_name = player["name"]
    ranked_play_count = player["rankedPlayCount"]
    
    player_scores_list = []
    
    if ranked_play_count == 0:
        return player_scores_list

    items_per_page = 100
    current_page = 1
    fetched_count = 0
    
    # Limite de segurança para páginas
    max_pages = (ranked_play_count // items_per_page) + 2 
    
    while fetched_count < ranked_play_count and current_page <= max_pages:
        url = f"https://scoresaber.com/api/player/{player_id}/scores?limit={items_per_page}&sort=top&page={current_page}&withMetadata=false"
        headers = {"accept": "application/json"}
        
        try:
            rate_limiter.wait()
            response = requests.get(url, headers=headers)
            
            if response.status_code == 429:
                print(f"Rate limit atingido para {player_name}. Aguardando 5s...")
                time.sleep(5)
                continue
                
            response.raise_for_status()
            data = response.json()
            player_scores = data.get("playerScores", [])
            
            if not player_scores:
                break
                
            for item in player_scores:
                score = item.get("score", {})
                leaderboard = item.get("leaderboard", {})
                
                pp_value = score.get("pp", 0)
                
                # Não incluir scores com 0.00pp
                if pp_value > 0:
                    modified_score = score.get("modifiedScore", 0)
                    max_score = leaderboard.get("maxScore", 0)
                    accuracy = 0.0
                    if max_score > 0:
                        accuracy = (modified_score / max_score) * 100
                    
                    player_scores_list.append({
                        "playerName": player_name,
                        "scoreId": score.get("id"),
                        "pp": pp_value,
                        "songName": leaderboard.get("songName"),
                        "songAuthorName": leaderboard.get("songAuthorName"),
                        "levelAuthorName": leaderboard.get("levelAuthorName"),
                        "accuracy": accuracy,
                        "weight": score.get("weight"),
                        "stars": leaderboard.get("stars", 0)
                    })
            
            fetched_count += len(player_scores)
            current_page += 1
            
        except Exception as e:
            print(f"Erro ao coletar scores de {player_name} na página {current_page}: {e}")
            break
            
    print(f"Finalizado: {player_name} ({len(player_scores_list)} scores)")
    return player_scores_list

def generate_star_ranking(all_scores, excluded_players=None):
    if excluded_players is None:
        excluded_players = []
        
    # Dicionário para armazenar o melhor score por range de estrelas
    # Chave: range_start (float), Valor: score object
    best_scores_by_range = {}
    
    # Definir o range máximo (ex: até 15 estrelas, incrementando de 0.5)
    max_stars = 15.0
    step = 0.5
    
    for score in all_scores:
        if score["playerName"] in excluded_players:
            continue
            
        stars = score.get("stars", 0)
        if stars == 0:
            continue
            
        # Calcular o índice do range (0.0, 0.5, 1.0, etc.)
        range_start = math.floor(stars / step) * step
        
        # Se ainda não tem score nesse range ou se o score atual tem mais PP
        if range_start not in best_scores_by_range:
            best_scores_by_range[range_start] = score
        else:
            if score["pp"] > best_scores_by_range[range_start]["pp"]:
                best_scores_by_range[range_start] = score
                
    # Ordenar os ranges
    sorted_ranges = sorted(best_scores_by_range.keys())
    
    output_lines = []
    if excluded_players:
        output_lines.append("Top 1 por maior pp (Excluindo Top 4):")
    else:
        output_lines.append("Top 1 por maior pp:")
    
    for r_start in sorted_ranges:
        r_end = r_start + step
        score = best_scores_by_range[r_start]
        
        # Formatar a linha
        # Ex: 0.00-0.50: 97.20pp 0.43☆ - ZLQ fez 100.00% no mapa: Small Shock Toby Fox (Venclaire)
        line = (f"{r_start:.2f}-{r_end:.2f}: {score['pp']:.2f}pp {score['stars']}☆ - "
                f"{score['playerName']} fez {score['accuracy']:.2f}% no mapa: "
                f"{score['songName']} {score.get('songAuthorName', '')} ({score.get('levelAuthorName', '')})")
        
        output_lines.append(line)
        
    return output_lines

def collect_ranking_players():
    # Tenta configurar o stdout para utf-8 para evitar erros de print no console do Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass # Python < 3.7 ou ambiente que não suporta reconfigure

    headers = {"accept": "application/json"}
    simplified_players = []
    
    try:
        # Coletar até 200 jogadores (4 páginas de 50)
        print("Coletando top 200 jogadores do Brasil...")
        
        for page in range(1, 5): 
            url = f"https://scoresaber.com/api/players?countries=BR&page={page}"
            
            try:
                rate_limiter.wait()
                response = requests.get(url, headers=headers)
                response.raise_for_status()

                players_data = response.json()
                current_page_players = players_data.get("players", [])
                
                if not current_page_players:
                    break
                    
                for player in current_page_players:
                    score_stats = player.get("scoreStats", {})
                    simplified_players.append({
                        "id": player.get("id"),
                        "name": player.get("name"),
                        "pp": player.get("pp"),
                        "countryRank": player.get("countryRank"),
                        "rankedPlayCount": score_stats.get("rankedPlayCount", 0)
                    })
                    
                print(f"Página {page} coletada. Total até agora: {len(simplified_players)}")
                
            except Exception as e:
                print(f"Erro ao coletar página {page} de jogadores: {e}")
                break

        with open("ranking_br.json", "w", encoding="utf-8") as json_file:
            json.dump({"players": simplified_players}, json_file, indent=4, ensure_ascii=False)
        
        print(f"Coletados {len(simplified_players)} jogadores no total. Iniciando coleta de scores com 10 threads...")

        all_scores = []
        
        # Multi-threading com 10 workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_player = {executor.submit(get_scores_for_player, player): player for player in simplified_players}
            
            for future in concurrent.futures.as_completed(future_to_player):
                try:
                    scores = future.result()
                    all_scores.extend(scores)
                except Exception as exc:
                    print(f"Exceção gerada: {exc}")

        # Ordenar por PP decrescente
        all_scores.sort(key=lambda x: x["pp"], reverse=True)
        
        with open("ranking_scores.json", "w", encoding="utf-8") as json_file:
            json.dump({"scores": all_scores}, json_file, indent=4, ensure_ascii=False)
            
        print("Scores coletados e salvos em ranking_scores.json")
        
        # Lista 1: Top PP Geral
        print("\nLista de Scores (Top PP):")
        with open("ranking_scores_list.txt", "w", encoding="utf-8") as txt_file:
            for i, s in enumerate(all_scores, 1):
                line = f"{i}º {s['playerName']}: {s['pp']:.2f}pp com {s['accuracy']:.2f}% ACC ({s['songName']})"
                try:
                    print(line)
                except UnicodeEncodeError:
                    print(line.encode('ascii', 'replace').decode('ascii'))
                txt_file.write(line + "\n")
        
        print("Lista salva em ranking_scores_list.txt")
        
        # Lista 2: Top PP por Estrelas (Todos)
        print("\nGerando lista por estrelas (Geral)...")
        star_ranking_lines = generate_star_ranking(all_scores)
        
        with open("ranking_stars_list.txt", "w", encoding="utf-8") as star_file:
            for line in star_ranking_lines:
                try:
                    print(line)
                except UnicodeEncodeError:
                    print(line.encode('ascii', 'replace').decode('ascii'))
                star_file.write(line + "\n")
        print("Lista por estrelas salva em ranking_stars_list.txt")
        
        # Lista 3: Top PP por Estrelas (Excluindo Top 4)
        print("\nGerando lista por estrelas (Excluindo Top 4)...")
        
        # Identificar Top 4 jogadores (baseado no countryRank)
        # simplified_players já está na ordem que veio da API (que é por rank)
        # Mas para garantir, vamos ordenar por countryRank
        simplified_players.sort(key=lambda x: x["countryRank"])
        top_4_players = [p["name"] for p in simplified_players[:5]]
        
        print(f"Excluindo jogadores: {top_4_players}")
        
        star_ranking_no_top4_lines = generate_star_ranking(all_scores, excluded_players=top_4_players)
        
        with open("ranking_stars_list_no_top4.txt", "w", encoding="utf-8") as star_file_no_top4:
            for line in star_ranking_no_top4_lines:
                try:
                    print(line)
                except UnicodeEncodeError:
                    print(line.encode('ascii', 'replace').decode('ascii'))
                star_file_no_top4.write(line + "\n")
                
        print("Lista por estrelas (sem top 4) salva em ranking_stars_list_no_top4.txt")

    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    collect_ranking_players()
