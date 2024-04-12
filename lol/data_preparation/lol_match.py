import csv
import json
import os
import queue
import time

import numpy as np
import pandas as pd
import sys
from . import riot_api


def match_ver(game_data) -> str:
    version = game_data["info"]["gameVersion"]
    assert isinstance(version, str)

    return version


seen_players = []
seen_matches = []

players = set()

total = 0

if os.path.exists("match_ids.csv"):
    with open("match_ids.csv", newline="") as f:
        reader = csv.reader(f)
        data = list(reader)
        seen_matches = data[0]

print(seen_matches)


def getdata(puuid: str):
    seen_players.append(puuid)
    players.remove(puuid)
    global total

    if total % 10 == 0:
        print(total)

    if total > 2000:
        sys.exit()
        return

    recent_match_ids = api.rank_match_ids_by_puuid(puuid, 10)
    # time.sleep(0.5)
    # print(f"puuid: {puuid}")
    for match_id in recent_match_ids:
        # print(match_id)
        if match_id in seen_matches:
            continue
        seen_matches.append(match_id)

        match_data = api.match_data_by_match_id(match_id)
        time.sleep(1)

        try:
            if match_ver(match_data).find("14.7") == -1:
                break
        except:
            continue

        timeline = api.timeline_by_matchid(match_id)
        # time.sleep(0.1)

        os.makedirs("match_data", exist_ok=True)
        os.makedirs("timeline", exist_ok=True)

        try:
            participants = api.match_data_by_match_id(recent_match_ids[-1])["metadata"][
                "participants"
            ]
        except:
            continue

        with open("match_data/{}.json".format(match_id), "w") as f:
            json.dump(match_data, f)

        with open("timeline/{}.json".format(match_id), "w") as f:
            json.dump(timeline, f)

        total += 1

        np.savetxt(
            "jp_silver_match_ids.csv", np.array(seen_matches), fmt="%s,", newline=""
        )

        for p in participants:
            players.add(p)
            if p not in seen_players:
                getdata(p)


# with open("jp_silver_match_ids.csv", newline="") as f:
#     reader = csv.reader(f)
#     data = list(reader)

# match_ids = data[0]

api = riot_api.ApiRequest(
    key="RGAPI-86cad0d8-41fa-423e-b096-7a1094579e53", region=riot_api.Region.JP
)

otto_account = api.puuid_by_game_name_and_tag_line("Apdo", "kr43")
otto_puuid = otto_account["puuid"]

# otto_recent10 = api.rank_match_ids_by_puuid(otto_puuid, 10)

# print(otto_recent10)

# total = 0

getdata(otto_puuid)

# for faker_match_id in faker_recent10:
#     if faker_match_id in match_ids:
#         continue
#     print(faker_match_id)
#     res = api.match_data_by_match_id(faker_match_id)
#
#     res['metadata']['participants']
#
#     if match_ver(res).find('13.4') == -1:
#         break
#     timeline = api.timeline_by_matchid(faker_match_id)
#
#     with open('data/{}.json'.format(faker_match_id), 'w') as f:
#         json.dump(res, f)
#
#     with open('data/timeline{}.json'.format(faker_match_id), 'w') as f:
#         json.dump(timeline, f)
