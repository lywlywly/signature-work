"""
python3 -m lol.data_preparation.item
"""

from functools import reduce
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from lxml import etree
import json
import re
import os

from lol import CHAMP_ITEM_PICK_WIN_RATE, CHAMP_ITEMS_DIR, HTML_DIR, ROLES_DIR

replacements = {
    "'": "",
    " ": "",
    ".": "",
    "wukong": "monkeyking",
    "renataglasc": "renata",
}


def find_item_trs(soup: BeautifulSoup):
    tables = soup.find_all("table")
    item_table = tables[-1]
    assert isinstance(item_table, Tag)
    tbody = item_table.find("tbody")
    assert isinstance(tbody, Tag)
    trs = tbody.find_all("tr")

    return trs


def extract_tr(tr: Tag):
    name_icon_td, pick_rate_td, win_rate_td = tr.findAll("td")
    # assert(all(isinstance(i, Tag) for i in [name_icon_td, pick_rate_td, win_rate_td]))
    # for var in [name_icon_td, pick_rate_td, win_rate_td]:
    #     assert isinstance(var, Tag)
    assert isinstance(name_icon_td, Tag)
    assert isinstance(pick_rate_td, Tag)
    assert isinstance(win_rate_td, Tag)
    strong_text_0 = name_icon_td.find("strong")
    strong_text_1 = pick_rate_td.find("strong")
    assert isinstance(strong_text_0, Tag)
    assert isinstance(strong_text_1, Tag)

    return strong_text_0.text, strong_text_1.text, win_rate_td.text


def main():
    with open(os.path.join(ROLES_DIR, "roles_highest.json"), "r") as f:
        all = json.load(f)

    for pos, champs in all.items():
        for champ in champs:
            c = reduce(
                lambda acc, kv: acc.replace(*kv),
                replacements.items(),
                re.sub(r"&.*", "", champ.lower()),
            )
            html = os.path.join(HTML_DIR, pos, f"{c}.html")
            print(html)

            with open(html, "r") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content)

            trs = find_item_trs(soup=soup)

            item_dict: dict[str, list[float]] = dict()

            for tr in trs:
                assert isinstance(tr, Tag)
                extracted_tr = extract_tr(tr)
                item_dict[extracted_tr[0]] = [
                    float(extracted_tr[1][:-2]),
                    float(extracted_tr[2][:-2]),
                ]

            with open(
                os.path.join(CHAMP_ITEM_PICK_WIN_RATE, f"{champ}.json"), "w"
            ) as f:
                json.dump(item_dict, f)


main() if __name__ == "__main__" else None
