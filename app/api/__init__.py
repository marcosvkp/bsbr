from flet_web.fastapi import FastAPI
from starlette.requests import Request

from app.data.data_manager import DataManager
from app import scorecalc
from app.integration.types import ScoreSaberScoreMessage
from app.ppcalc import ScoreSaberAPI
from app.scorecalc import get_pp

app = FastAPI()

@app.get("/maps")
def get_maps():
    return DataManager.maps_data

@app.get("/leaderboard/{leaderboard_id}")
async def get_leaderboard(leaderboard_id: int, page: int):

    scores = []

    data = ScoreSaberAPI._fetch_page(leaderboard_id=leaderboard_id, country="br", page=page, limit=10)

    map_info = DataManager.maps_by_leaderboard.get(str(leaderboard_id))
    if map_info is None:
        return {"error": "Map not found"}

    stars = float(map_info["stars"].replace("★", ""))

    for s in data:
        acc = (s["baseScore"] / map_info["maxscore"]) * 100 if map_info["maxscore"] > 0 else 0
        pp = scorecalc.get_pp(stars, acc)
        scores.append({
            "username": s.get("leaderboardPlayerInfo", {}).get("name"),
            "player_id": s.get("leaderboardPlayerInfo", {}).get("id"),
            "rank": s.get("rank"),
            "fc": s.get("fullCombo"),
            "acc": acc,
            "pp": pp
        })

    return {
        "leaderboard_id": leaderboard_id,
        "scores": scores[:200]
    }

@app.post("/scorecalc")
async def get_scorecalc(data: dict):
    msg = ScoreSaberScoreMessage.model_validate(data)
    if not msg:
        return {}

    score2 = msg.commandData.score
    leaderboard = msg.commandData.leaderboard
    song = f"{leaderboard.songName} - {leaderboard.songAuthorName} | Mapper: {leaderboard.levelAuthorName}"

    if not str(leaderboard.id) in DataManager.maps_by_leaderboard:
        return {}

    map_info = DataManager.maps_by_leaderboard.get(str(leaderboard.id))
    if map_info is None:
        stars = leaderboard.stars
    else:
        stars = float(map_info["stars"].replace("★", ""))

    player_data = DataManager.get_player_detail(score2.leaderboardPlayerInfo.id)

    print(player_data)
    acc = round((score2.modifiedScore / leaderboard.maxScore) * 100, 2)

    details = player_data

    pp = round(get_pp(stars, acc), 2)

    # garante que existe lista
    details.setdefault("scores", [])

    new_score = {"pp": pp}
    details["scores"].append(new_score)
    details["scores"].sort(key=lambda x: x["pp"], reverse=True)

    new_score_position = details["scores"].index(new_score)

    weight = 0.965 ** new_score_position
    weighted = pp * weight

    score_data = {
        "player_id": score2.leaderboardPlayerInfo.id,
        "player_name": score2.leaderboardPlayerInfo.name,
        "acc": acc,
        "pp": pp,
        "deviceName": score2.deviceHmd,
        "modifiers": score2.modifiers,
        "fullCombo": score2.fullCombo,
        "weighted": weighted,
        "weight": weight,
        "stars": stars,
    }

    return score_data