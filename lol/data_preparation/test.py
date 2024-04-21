import json
from riot_api import ApiRequest, Region

request = ApiRequest(key="RGAPI-a8e1f5ea-59ea-438c-b4a1-587e02da90b9", region=Region.KR)

a = request.puuid_by_game_name_and_tag_line("Hide On Bush", "KR1")

b = request.mastery_by_puuid(a["puuid"])

print(json.dumps(b))
