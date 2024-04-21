"""
python3 -m lol.data_preparation.champ_item_score
"""

import itertools
import json
import math
import os

from lol import CHAMP_ITEM_PICK_WIN_RATE, CHAMP_ITEMS_DIR, CONVERT_DIR


def main():

    champ_items_files = [
        file
        for file in os.listdir(CHAMP_ITEM_PICK_WIN_RATE)
        if os.path.isfile(os.path.join(CHAMP_ITEM_PICK_WIN_RATE, file))
        and file[-4:] == "json"
    ]
    champs = [file[:-5] for file in champ_items_files]
    champs.sort()
    all_champ_items = []
    for f in champ_items_files:
        with open(f"embedding/{f}", "r") as file:
            dict_item = json.load(file)
            all_champ_items.append(list(dict_item.keys()))
    all_items_set = set(itertools.chain.from_iterable(all_champ_items))
    items_wo_duplicate = list(all_items_set)
    items_wo_duplicate.sort()
    idx2item = {i: item for i, item in enumerate(items_wo_duplicate)}
    item2idx = {item: i for i, item in enumerate(items_wo_duplicate)}
    idx2champ = {i: item for i, item in enumerate(champs)}
    champ2idx = {item: i for i, item in enumerate(champs)}

    with open(os.path.join(CONVERT_DIR, "idx2item.json"), "w") as f:
        json.dump(idx2item, f)
    with open(os.path.join(CONVERT_DIR, "item2idx.json"), "w") as f:
        json.dump(item2idx, f)
    with open(os.path.join(CONVERT_DIR, "idx2champ.json"), "w") as f:
        json.dump(idx2champ, f)
    with open(os.path.join(CONVERT_DIR, "champ2idx.json"), "w") as f:
        json.dump(champ2idx, f)

    champ_item_score = {}

    for f in champ_items_files:
        with open(f"{CHAMP_ITEM_PICK_WIN_RATE}/{f}", "r") as file:
            dict_item = json.load(file)
            new_dict = {
                item2idx[item]: math.exp((v[1] + (v[0] ** 2) / 75) / 12) / 100
                for item, v in dict_item.items()
            }  # penalize very low winrate, make high pick rate more important
            champ_item_score[champ2idx[f[:-5]]] = new_dict

    with open(os.path.join(CHAMP_ITEMS_DIR, "champ_item_score.json"), "w") as f:
        json.dump(champ_item_score, f)


main() if __name__ == "__main__" else None
