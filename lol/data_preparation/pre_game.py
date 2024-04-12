"""
python3 -m lol.data_preparation.pre_game
"""

import csv
import itertools
import json
import os
import time
from typing import Final, TypeAlias

from retry import retry

from . import riot_api

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

MATH_DATA_DIR: Final = "match_data"

api = riot_api.ApiRequest(
    key="RGAPI-77767ec5-577f-47e6-9b43-0e9256f56496", region=riot_api.Region.KR
)

# use retry decorator on the three apis
retry_match_data_by_match_id = retry(tries=1, delay=10)(api.match_data_by_match_id)
retry_player_mastery_of_champion = retry(tries=1, delay=10)(
    api.player_mastery_of_champion
)
retry_rank_match_ids_by_puuid = retry(tries=1, delay=10)(api.rank_match_ids_by_puuid)


def get_local_caches():
    match_data_paths = os.listdir(MATH_DATA_DIR)
    return list(
        map(lambda e: e[:-5], filter(lambda e: e[-4:] == "json", match_data_paths))
    )


def cached_match_data_by_match_id(match_id: str) -> JSON:
    if match_id in get_local_caches():
        print("hit")
        with open(f"{MATH_DATA_DIR}/{match_id}.json", "r") as f:
            match_data = json.load(f)
    else:
        print("miss")
        match_data = retry_match_data_by_match_id(match_id)

        with open(f"{MATH_DATA_DIR}/{match_id}.json", "w") as f:
            json.dump(match_data, f)

    return match_data


def find_match_ids_before_this_match(cur_match_id: str, puuid: str) -> list[str]:
    recent15 = retry_rank_match_ids_by_puuid(puuid, 100)
    try:
        cur_idx = recent15.index(cur_match_id)
        next_5_slice = slice(cur_idx + 1, (cur_idx + 1) + 5)
        return recent15[next_5_slice]
    except ValueError:
        return []


def avg_k_d_a_in_matches(match_ids: list[str], puuid: str):
    print(f"match_ids: {match_ids}")
    return [k_d_a_in_match(match_id, puuid) for match_id in match_ids]


def k_d_a_in_match(match_id: str, puuid: str) -> tuple[int, int, int]:
    print(match_id)

    match_data = cached_match_data_by_match_id(match_id)
    if match_data["info"].get("endOfGameResult") == "Abort_Unexpected":  # type: ignore
        return 0, 0, 0

    participants = match_data["info"]["participants"]  # type: ignore
    assert isinstance(participants, list)
    current_player_stats_list: JSON = list(
        filter(lambda e: e["puuid"] == puuid, participants)  # type: ignore
    )

    assert len(current_player_stats_list) == 1, current_player_stats_list

    current_player_stats: dict[str, JSON] = current_player_stats_list[0]  # type: ignore
    k = current_player_stats["kills"]
    d = current_player_stats["deaths"]
    a = current_player_stats["assists"]
    assert isinstance(k, int)
    assert isinstance(d, int)
    assert isinstance(a, int)

    return k, d, a


def make_pre_game(match_data: JSON, champ_wr: dict[int, list[float]]):
    participants = match_data["info"]["participants"]  # type: ignore
    match_id: str = match_data["metadata"]["matchId"]  # type: ignore
    assert isinstance(match_id, str)
    assert isinstance(participants, list)
    assert len(participants) == 10

    team1_win = participants[0]["win"]  # type: ignore
    assert isinstance(team1_win, bool)
    team2_win = not team1_win

    team1: list[tuple[str, int]] = [
        (participants[i]["puuid"], participants[i]["championId"]) for i in range(5)  # type: ignore
    ]
    team2: list[tuple[str, int]] = [
        (participants[i]["puuid"], participants[i]["championId"]) for i in range(5, 10)  # type: ignore
    ]

    team1_mastery = sum(
        retry_player_mastery_of_champion(puuid, champ_id)["championPoints"]  # type: ignore
        for puuid, champ_id in team1
    )
    assert isinstance(team1_mastery, int)

    time.sleep(5)

    team2_mastery = sum(
        retry_player_mastery_of_champion(puuid, champ_id)["championPoints"]  # type: ignore
        for puuid, champ_id in team2
    )

    assert isinstance(team2_mastery, int)

    match_ids1 = [
        (
            find_match_ids_before_this_match(
                match_id,
                puuid,
            ),
            puuid,
        )
        for puuid, _ in team1
    ]
    kda_list_1 = [avg_k_d_a_in_matches(matches, puuid) for matches, puuid in match_ids1]
    kda1 = [sum(col) for col in zip(*itertools.chain.from_iterable(kda_list_1))]

    match_ids2 = [
        (
            find_match_ids_before_this_match(
                match_id,
                puuid,
            ),
            puuid,
        )
        for puuid, _ in team2
    ]
    kda_list_2 = [avg_k_d_a_in_matches(matches, puuid) for matches, puuid in match_ids2]
    kda2 = [sum(col) for col in zip(*itertools.chain.from_iterable(kda_list_2))]

    team1_champ_wr = sum(champ_wr[champ_id][0] for _, champ_id in team1)
    team2_champ_wr = sum(champ_wr[champ_id][0] for _, champ_id in team2)

    print(kda_list_1)
    print(kda_list_2)

    return [
        [match_id, team1_mastery, team1_champ_wr, *kda1, team1_win],
        [match_id, team2_mastery, team2_champ_wr, *kda2, team2_win],
    ]


def main():
    with open("data/roles/roles_highest.json", "r") as f:
        roles_highest = json.load(f)

    with open("champ2idx.json", "r") as f:
        champ2idx = json.load(f)

    l = ["KR_7017226474"]
    champ_wr = {champ2idx[k]: v for d in roles_highest.values() for k, v in d.items()}
    pre_game_data: list[list[str | int | float | bool]] = []

    count = 0
    for x in l:
        print(x)
        print(count)
        if count > 22:
            break
        with open(f"{MATH_DATA_DIR}/{x}.json", "r") as f:
            match_data = json.load(f)

        pre_game_data.extend(make_pre_game(match_data, champ_wr))
        count += 1

    csv_file = "pre_game.csv"
    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        for row in pre_game_data:
            writer.writerow(row)


main() if __name__ == "__main__" else None
