from enum import Enum
from typing import Literal, TypeAlias
import requests
from retry import retry
import warnings


# def player_data_by_puuid(match_data, puuid):
#     participants_ = match_data["metadata"]["participants"]
#     player_index = participants_.index(puuid)
#     player_data = match_data["info"]["participants"][player_index]
#     return player_data


# def players_data_by_match_data(match_data, puuid=None):
#     if puuid is not None:
#         participants_ = match_data["metadata"]["participants"]
#         player_index = participants_.index(puuid)
#         player_team_data = []
#         enemy_team_data = []
#         if player_index < 5:
#             for i in range(5):
#                 if i != player_index:
#                     player_team_data.append(match_data["info"]["participants"][i])
#             for i in range(5, 10):
#                 enemy_team_data.append(match_data["info"]["participants"][i])
#         else:
#             for i in range(5):
#                 enemy_team_data.append(match_data["info"]["participants"][i])
#             for i in range(5, 10):
#                 if i != player_index:
#                     player_team_data.append(match_data["info"]["participants"][i])
#         return player_team_data, enemy_team_data
#     else:
#         player_datas = []
#         for i in range(10):
#             player_datas.append(match_data["info"]["participants"][i])
#         return player_datas


# def kda_by_player_data(data):
#     k = data["kills"]
#     d = data["deaths"]
#     a = data["assists"]
#     return calc_kda(k, d, a)


# def calc_kda(kill, death, assist):
#     if death == 0:
#         return kill + assist
#     return (kill + assist) / death


# def create_team_stats(n):
#     data_teammate = [
#         {
#             "champion": "",
#             "kills": "",
#             "deaths": "",
#             "assists": "",
#             "win": "",
#             "KD/A": "",
#         }
#         for _ in range(n)
#     ]
#     return data_teammate


# def cal_avg(team_data):
#     kda_sum = 0
#     for _ in team_data:
#         kda_sum += _["KD/A"]
#     kda = kda_sum / len(team_data)
#     team_data.append(
#         {
#             "champion": "Average",
#             "kills": "",
#             "deaths": "",
#             "assists": "",
#             "win": "",
#             "KD/A": kda,
#         }
#     )

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


class Region(Enum):
    JP = "jp"
    KR = "kr"
    NA = "na"


class ApiRequest:
    regions = {"jp": ["jp1", "asia"], "kr": ["kr", "asia"], "na": ["na1", "americas"]}

    def __init__(self, key: str, region: Region):
        self.api_key = key
        self.region = region

    def set_key(self, key: str):
        self.api_key = key

    def puuid_by_game_name_and_tag_line(self, game_name: str, tag_line: str):
        url = "https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={api_key} "
        url = url.format(
            region=ApiRequest.regions[self.region.value][1],
            game_name=game_name,
            tag_line=tag_line,
            api_key=self.api_key,
        )

        response = requests.get(url)
        response_json = response.json()

        if response.status_code != 200:
            raise Exception(response_json)
        return response_json

    def summoner_data_by_name(self, summoner_name: str):
        url = (
            "https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{"
            "summoner_name}?api_key={api_key} "
        )
        url = url.format(
            region=ApiRequest.regions[self.region.value][0],
            summoner_name=summoner_name,
            api_key=self.api_key,
        )

        response = requests.get(url)
        response_json = response.json()

        if response.status_code != 200:
            raise Exception(response_json)
        return response_json

    def timeline_by_matchid(self, matchid: str):
        url = (
            "https://{region}.api.riotgames.com/lol/match/v5/matches/{"
            "match_id}/timeline?api_key={api_key}"
        )
        url = url.format(
            region=ApiRequest.regions[self.region.value][1],
            match_id=matchid,
            api_key=self.api_key,
        )

        response = requests.get(url)
        response_json = response.json()

        if response.status_code != 200:
            raise Exception(response_json)
        return response_json

    def summoner_data_by_puuid(self, puuid: str):
        url = (
            "https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{"
            "summoner_name}?api_key={api_key} "
        )
        url = url.format(
            region=ApiRequest.regions[self.region.value][0],
            summoner_name=puuid,
            api_key=self.api_key,
        )

        response = requests.get(url)
        response_json = response.json()

        if response.status_code != 200:
            raise Exception(response_json)
        return response_json

    def rank_by_summonerid(self, summonerid: str):
        url = (
            "https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{"
            "summonerid}?api_key={api_key} "
        )
        url = url.format(
            region=ApiRequest.regions[self.region.value][0],
            summonerid=summonerid,
            api_key=self.api_key,
        )

        response = requests.get(url)
        response_json = response.json()

        if response.status_code != 200:
            raise Exception(response_json)
        return response_json

    def rank_match_ids_by_puuid(self, puuid: str, count: int = 10) -> list[str]:
        if count > 100:
            warnings.warn("`count` can have a maximum value of 100.")
        url = (
            "https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{"
            "puuid}/ids?queue=420&start={start}&count={count}&api_key={api_key} "
        )
        url = url.format(
            region=ApiRequest.regions[self.region.value][1],
            puuid=puuid,
            api_key=self.api_key,
            start=0,
            count=count,
        )

        response = requests.get(url)
        response_json = response.json()

        if response.status_code != 200:
            raise Exception(response_json)
        return response_json

    def mastery_by_puuid(self, puuid: str):
        url = (
            "https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{"
            "puuid}?api_key={api_key} "
        )
        url = url.format(
            region=ApiRequest.regions[self.region.value][0],
            puuid=puuid,
            api_key=self.api_key,
        )

        response = requests.get(url)
        response_json = response.json()

        if response.status_code != 200:
            raise Exception(response_json)
        return response_json

    def player_mastery_of_champion(self, puuid: str, champ_id: int) -> JSON:
        champ_masteries: JSON = list(
            filter(lambda e: e["championId"] == champ_id, self.mastery_by_puuid(puuid))
        )
        assert len(champ_masteries) == 1
        champ_mastery = champ_masteries[0]

        return champ_mastery

    def match_data_by_match_id(self, match_id: str):
        url = (
            "https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={"
            "api_key} "
        )
        url = url.format(
            region=ApiRequest.regions[self.region.value][1],
            match_id=match_id,
            api_key=self.api_key,
        )

        response = requests.get(url)
        response_json = response.json()

        if response.status_code != 200:
            raise Exception(response_json)
        return response_json
