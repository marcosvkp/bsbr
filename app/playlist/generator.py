import json
import base64
import os
import requests
from collections import defaultdict
from app.data.database import get_db
from app.data.models.ranked_br_maps import RankedBRMaps

def get_hash_from_scoresaber(leaderboard_id):
    """Busca o hash do mapa usando a API do ScoreSaber."""
    try:
        url = f"https://scoresaber.com/api/leaderboard/by-id/{leaderboard_id}/info"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("songHash")
    except Exception as e:
        print(f"Erro ao buscar hash para {leaderboard_id}: {e}")
    return None

def generate_bsbr_playlist(base_url: str = ""):
    """
    Gera o conteúdo JSON da playlist BSBR Ranked.
    
    Args:
        base_url (str): A URL pública onde o app será hospedado.
    """
    db = next(get_db())
    try:
        ranked_maps = db.query(RankedBRMaps).all()
        
        maps_dict = defaultdict(lambda: {
            "songName": "",
            "levelAuthorName": "",
            "hash": "",
            "levelid": "",
            "difficulties": []
        })
        
        processed_hashes = {}

        for m in ranked_maps:
            map_hash = processed_hashes.get(m.map_id)
            
            if not map_hash:
                print(f"Buscando hash para {m.map_name} ({m.leaderboard_id})...")
                map_hash = get_hash_from_scoresaber(m.leaderboard_id)
                if map_hash:
                    processed_hashes[m.map_id] = map_hash
                else:
                    print(f"Falha ao obter hash para {m.map_name}. Pulando.")
                    continue
            
            diff_name = m.difficulty.replace(" ", "")
            if diff_name == "Expert+": diff_name = "ExpertPlus"
            
            entry = maps_dict[m.map_id]
            if not entry["hash"]:
                entry["songName"] = m.map_name
                entry["levelAuthorName"] = m.map_author
                entry["hash"] = map_hash
                entry["levelid"] = f"custom_level_{map_hash}"
            
            entry["difficulties"].append({
                "characteristic": "Standard",
                "name": diff_name
            })

        songs_list = list(maps_dict.values())

        image_base64 = ""
        logo_path = os.path.join("assets", "bsbr_playlist_logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                image_base64 = f"base64,{encoded}"

        # Monta a syncURL se uma base_url for fornecida
        sync_url = ""
        if base_url:
            # Garante que a URL não tenha uma barra no final e adiciona o caminho do arquivo
            sync_url = f"{base_url.rstrip('/')}/bsbr_ranked.bplist"

        playlist_data = {
            "playlistTitle": "BSBR Ranked Maps",
            "playlistAuthor": "BSBR Team",
            "customData": {
                "syncURL": sync_url
            },
            "songs": songs_list,
            "image": image_base64
        }
        
        return json.dumps(playlist_data, indent=2)

    except Exception as e:
        print(f"Erro ao gerar playlist: {e}")
        return None
    finally:
        db.close()
