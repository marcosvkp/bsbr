import requests
import sys
from collections import defaultdict
from sqlalchemy.orm import Session
from app.data.database import engine, SessionLocal
from app.data.models.ranked_br_maps import RankedBRMaps

def get_map_info(map_id):
    """Busca informações do mapa no BeatSaver."""
    url = f"https://api.beatsaver.com/maps/id/{map_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar mapa {map_id}: {e}")
        return None

def get_leaderboards_by_hash(map_hash):
    """Busca leaderboards no ScoreSaber pelo hash."""
    url = f"https://scoresaber.com/api/leaderboard/get-difficulties/{map_hash}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar leaderboards para hash {map_hash}: {e}")
        return []

def get_leaderboard_info(leaderboard_id):
    """Busca detalhes do leaderboard no ScoreSaber."""
    url = f"https://scoresaber.com/api/leaderboard/by-id/{leaderboard_id}/info"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar info do leaderboard {leaderboard_id}: {e}")
        return None

def difficulty_int_to_str(diff_int):
    """Converte o inteiro de dificuldade do ScoreSaber para string legível."""
    mapping = {
        1: "Easy",
        3: "Normal",
        5: "Hard",
        7: "Expert",
        9: "ExpertPlus"
    }
    return mapping.get(diff_int, str(diff_int))

def list_current_ranked_maps():
    """Lista todos os mapas rankeados atualmente no banco de dados."""
    db = SessionLocal()
    try:
        maps = db.query(RankedBRMaps).all()
        
        if not maps:
            print("Nenhum mapa rankeado encontrado no banco de dados.")
            return

        # Agrupa por map_id (BeatSaver Key)
        grouped_maps = defaultdict(list)
        map_details = {} # map_id -> {name, author}

        for m in maps:
            grouped_maps[m.map_id].append(m)
            if m.map_id not in map_details:
                map_details[m.map_id] = {
                    "name": m.map_name,
                    "author": m.map_author
                }

        print(f"\n--- Mapas Rankeados BR Atuais ({len(grouped_maps)} mapas, {len(maps)} dificuldades) ---\n")

        # Ordena por nome do mapa
        sorted_keys = sorted(grouped_maps.keys(), key=lambda k: map_details[k]["name"].lower())

        for map_id in sorted_keys:
            details = map_details[map_id]
            diffs = grouped_maps[map_id]
            
            # Ordena dificuldades por estrelas (decrescente)
            diffs.sort(key=lambda x: float(x.stars), reverse=True)
            
            print(f"[{map_id}] {details['name']} - {details['author']}")
            for d in diffs:
                print(f"  - {d.difficulty}: {d.stars:.2f}★ (ID: {d.leaderboard_id})")
            print("") # Linha em branco entre mapas

    except Exception as e:
        print(f"Erro ao listar mapas: {e}")
    finally:
        db.close()

def add_ranked_map():
    print("--- Adicionar Mapa Rankeado BR ---")
    map_id_input = input("Digite o ID do mapa (BeatSaver Key): ").strip()
    
    if not map_id_input:
        print("ID inválido.")
        return

    # 1. Busca no BeatSaver
    print(f"Buscando mapa {map_id_input} no BeatSaver...")
    bs_data = get_map_info(map_id_input)
    
    if not bs_data:
        return

    print(f"Mapa encontrado: {bs_data['name']} por {bs_data['uploader']['name']}")
    
    # Pega a versão mais recente (última da lista versions)
    versions = bs_data.get("versions", [])
    if not versions:
        print("Nenhuma versão encontrada para este mapa.")
        return
        
    latest_version = versions[-1] 
    map_hash = latest_version["hash"]
    print(f"Hash da versão mais recente: {map_hash}")

    # 2. Busca Leaderboards no ScoreSaber
    print("Buscando dificuldades no ScoreSaber...")
    leaderboards = get_leaderboards_by_hash(map_hash)
    
    if not leaderboards:
        print("Nenhum leaderboard encontrado no ScoreSaber para este hash.")
        return

    print("\nDificuldades encontradas:")
    valid_leaderboards = []
    
    db = SessionLocal()
    
    for i, lb in enumerate(leaderboards):
        diff_name = difficulty_int_to_str(lb["difficulty"])
        game_mode = lb["gameMode"]
        lb_id = lb["leaderboardId"]
        
        # Verifica se já existe no banco para avisar
        existing = db.query(RankedBRMaps).filter_by(leaderboard_id=str(lb_id)).first()
        status_msg = ""
        if existing:
            status_msg = f" [JÁ ADICIONADO - {existing.stars}★]"
            
        print(f"{i+1}. {diff_name} ({game_mode}) - ID: {lb_id}{status_msg}")
        valid_leaderboards.append(lb)

    # 3. Seleção e Definição de Estrelas
    selected_indices = input("\nDigite os números das dificuldades que deseja adicionar (separados por vírgula, ex: 1,3): ").strip()
    
    if not selected_indices:
        print("Nenhuma dificuldade selecionada.")
        db.close()
        return

    try:
        indices = [int(x.strip()) - 1 for x in selected_indices.split(",")]
    except ValueError:
        print("Entrada inválida.")
        db.close()
        return

    for idx in indices:
        if idx < 0 or idx >= len(valid_leaderboards):
            print(f"Índice {idx+1} inválido, pulando.")
            continue
            
        lb = valid_leaderboards[idx]
        lb_id = lb["leaderboardId"]
        diff_name = difficulty_int_to_str(lb["difficulty"])
        
        # Pergunta as estrelas
        stars_input = input(f"Defina as estrelas para {diff_name} (ID: {lb_id}): ").strip()
        try:
            stars = float(stars_input)
        except ValueError:
            print(f"Valor de estrelas inválido para {diff_name}, pulando.")
            continue

        # 4. Busca Info Final do Leaderboard
        print(f"Obtendo detalhes finais para {diff_name}...")
        lb_info = get_leaderboard_info(lb_id)
        
        if not lb_info:
            print("Falha ao obter detalhes finais, pulando.")
            continue

        # Salva no Banco de Dados
        try:
            # Verifica se já existe
            existing = db.query(RankedBRMaps).filter_by(leaderboard_id=str(lb_id)).first()
            
            if existing:
                print(f"Mapa {lb_id} já existe no banco. Atualizando dados...")
                existing.stars = stars
                existing.map_name = lb_info["songName"]
                existing.cover_image = lb_info["coverImage"]
                existing.map_author = lb_info["levelAuthorName"]
                existing.max_score = lb_info["maxScore"]
                # existing.hash = lb_info["songHash"] # O model não tem hash, removido
            else:
                new_map = RankedBRMaps(
                    leaderboard_id=str(lb_id),
                    map_id=map_id_input, # ID do BeatSaver (Key)
                    map_name=lb_info["songName"],
                    map_author=lb_info["levelAuthorName"],
                    difficulty=diff_name,
                    stars=stars,
                    max_score=lb_info["maxScore"],
                    cover_image=lb_info["coverImage"]
                    # hash removido pois não existe no model RankedBRMaps
                )
                db.add(new_map)
                print(f"Adicionado: {lb_info['songName']} - {diff_name} ({stars}★)")
            
            db.commit()
            
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")
            db.rollback()

    db.close()
    print("\nProcesso finalizado.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-atual":
        list_current_ranked_maps()
    else:
        add_ranked_map()
