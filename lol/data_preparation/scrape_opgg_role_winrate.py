"""
python3 -m lol.data_preparation.scrape_opgg_role_winrate
"""

import json
import os

from bs4 import BeautifulSoup
from bs4.element import Tag

from lol import ROLES_DIR, HTML_DIR, roles


def find_rank_tbody(soup: BeautifulSoup):
    tbodys = soup.find_all("tbody")
    assert len(tbodys) == 1
    tbody = tbodys[0]
    assert isinstance(tbody, Tag)
    return tbody


def extract_champ_wr_dict(rows: list[Tag]):
    result: dict[str, float] = dict()
    filtered_ad = list(filter(lambda x: "ad" not in x.td["class"][0], rows))  # type: ignore

    for _ in filtered_ad:
        tds = _.find_all("td")
        champion_name = tds[1].a.strong.text
        win_rate = float(tds[4].text[:-1])
        pick_rate = float(tds[5].text[:-1])
        result[champion_name] = [win_rate, pick_rate]

    return result


def scrape_role(html_path: str):
    with open(html_path, "r") as d:
        html_content = d.read()

    soup = BeautifulSoup(html_content, "html.parser")
    tbody = find_rank_tbody(soup)
    rows = tbody.find_all("tr")

    return extract_champ_wr_dict(rows)


def main():
    for role in roles:
        d = scrape_role(os.path.join(HTML_DIR, f"{role}.html"))

        with open(os.path.join(ROLES_DIR, f"{role}.json"), "w") as f:
            json.dump(d, f)

        pos_champ_dict: dict[str, list[str]] = {}
        pos_champ_wr_dict: dict[str, dict[str, list[float]]] = {}
        for role in roles:
            with open(os.path.join(ROLES_DIR, f"{role}.json"), "r") as f:
                d: dict[str, list[float]] = json.load(f)
                pos_champ_dict[role] = list(d.keys())
                pos_champ_wr_dict[role] = d

        with open(os.path.join(ROLES_DIR, "pos_champ_dict_opgg.json"), "w") as f:
            json.dump(pos_champ_dict, f)

        with open(os.path.join(ROLES_DIR, "pos_champ_wr_dict_opgg.json"), "w") as f:
            json.dump(pos_champ_wr_dict, f)

        champion_positions = {}
        for position, champions in pos_champ_wr_dict.items():
            for champion, stats in champions.items():
                pick_rate = stats[1]
                if champion not in champion_positions:
                    champion_positions[champion] = (position, pick_rate)
                else:
                    _, max_pick_rate = champion_positions[champion]
                    if pick_rate > max_pick_rate:
                        champion_positions[champion] = (position, pick_rate)

        result = {}
        for champion, (position, pick_rate) in champion_positions.items():
            result.setdefault(position, {})[champion] = [
                pos_champ_wr_dict[position][champion][0],
                pick_rate,
            ]

        with open(os.path.join(ROLES_DIR, "roles_highest.json"), "w") as f:
            json.dump(result, f)


main() if __name__ == "__main__" else None
