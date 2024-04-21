import json
import threading
import time
from functools import reduce

import requests
from flask import Flask
from lstm import *
from champ_item_embedding import infer

app = Flask(__name__)

EXP_TILL_LEVEL = [
    0,
    280,
    660,
    1140,
    1720,
    2400,
    3180,
    4060,
    5040,
    6120,
    7300,
    8580,
    9960,
    11440,
    13020,
    14700,
    16480,
    18360,
]
PEM_PATH = "riotgames.pem"
context = []
with open("item.json", "r", encoding="utf-8") as f:
    item_data = json.loads(f.read())
with open("item2idx.json", "r", encoding="utf-8") as f:
    item2idx = json.load(f)
with open("champ2idx.json", "r", encoding="utf-8") as f:
    champ2idx = json.load(f)
with open("champ_short_name2champ_long_name.json", "r", encoding="utf-8") as f:
    champ_short_name2champ_long_name = json.load(f)
with open("champ_id2champ_name.json", "r", encoding="utf-8") as f:
    champ_id2champ_name = json.load(f)
with open("jp_champ_name2champid.json", "r", encoding="utf-8") as f:
    jp_champ_name2champid = json.load(f)
with open("itemid2name.json", "r", encoding="utf-8") as f:
    itemid2name = json.load(f)
itemid2name = {int(k): v for k, v in itemid2name.items()}


def refresh_data(context: list):
    while True:
        try:
            response = requests.get(
                "https://127.0.0.1:2999/liveclientdata/allgamedata", verify=PEM_PATH
            ).json()
            minute = response["gameData"]["gameTime"] // 60
            processed_data = process_data(response)
            data = (
                create_current_data_a(processed_data),
                create_current_data_b(processed_data),
                minute,
            )

            if len(context) == 0 or minute > context[-1][2]:
                action = "add new" if len(context) > 0 else "first"
                print(f"Game minute {minute}, {action} data point")
                context.append(data)
            else:
                print(f"Game minute {minute}, refresh data point")
                context[-1] = data

        except Exception as e:
            print(f"Error refreshing data: {e}")

        time.sleep(1)


def process_data(data):
    all_player_data = data["allPlayers"]
    player_names = [e["summonerName"] for e in all_player_data]

    processed_all_player_data = [
        {
            "gold": sum(
                item_data["data"]
                .get(str(c["itemID"]), {})
                .get("gold", {})
                .get("total", 3000)
                for c in e["items"]
            ),
            "summoner_name": e["summonerName"],
            "score": e["scores"],
            "level": e["level"],
            "items": [e["itemID"] for e in e["items"]],
            "champion_name": e["championName"],
        }
        for e in all_player_data
    ]

    events = data["events"]["Events"]

    events_a = [e for e in events if e.get("KillerName") in player_names[0:5]]
    events_b = [e for e in events if e.get("KillerName") in player_names[5:10]]

    gamedata = data["gameData"]

    return {
        "player": processed_all_player_data,
        "events": {"team_a": events_a, "team_b": events_b},
        "time": gamedata["gameTime"] / 60,
    }


def calculate_statistic(players, indices: list[int]):
    gold = sum(players[i]["gold"] for i in indices)
    gold_diff = sum(players[i]["gold"] for i in indices) - sum(
        players[i]["gold"] for i in range(10) if i not in indices
    )
    exp = sum(EXP_TILL_LEVEL[players[i]["level"] - 1] for i in indices)
    exp_diff = sum(EXP_TILL_LEVEL[players[i]["level"] - 1] for i in indices) - sum(
        EXP_TILL_LEVEL[players[i]["level"] - 1] for i in range(10) if i not in indices
    )

    item_score = sum(
        sum(
            infer.infer(
                champ2idx[
                    champ_id2champ_name[
                        jp_champ_name2champid[players[i]["champion_name"]]
                    ]
                ],
                item2idx.get(itemid2name[j]),
            )
            for j in players[i]["items"]
        )
        for i in indices
    )
    print(item_score)

    return [gold, gold_diff, exp, exp_diff]


def count_events(events, event_names):
    return len([event for event in events if event["EventName"] in event_names])


def create_current_data_a(curr_data):
    player_data = curr_data["player"]
    team_a_events = curr_data["events"]["team_a"]

    indices = range(5)

    result = calculate_statistic(player_data, indices)

    result += [
        count_events(team_a_events, ["HeraldKilled", "BaronKilled"]),
        count_events(team_a_events, ["DrakeKilled"]),
        count_events(team_a_events, ["TurretKilled"]),
    ]

    return result


def create_current_data_b(curr_data):
    player_data = curr_data["player"]
    team_b_events = curr_data["events"]["team_b"]

    indices = range(5, 10)

    result = calculate_statistic(player_data, indices)

    result += [
        count_events(team_b_events, ["HeraldKilled", "BaronKilled"]),
        count_events(team_b_events, ["DrakeKilled"]),
        count_events(team_b_events, ["TurretKilled"]),
    ]

    return result


def pred():
    game_state_seq_a = np.array([t[0] for t in context], dtype=np.float32)
    game_state_seq_b = np.array([t[1] for t in context], dtype=np.float32)
    a = infer(game_state_seq_a)
    b = infer(game_state_seq_b)
    return {
        "preda": a,
        "predb": b,
        "pred": a / (a + b),
        "time": context[2],
    }


@app.route("/", methods=["GET"])
def get_wr_pred():
    return pred()


if __name__ == "__main__":
    refresh_thread = threading.Thread(target=refresh_data, args=(context,))
    refresh_thread.daemon = True
    refresh_thread.start()
    app.run(port=7999)
