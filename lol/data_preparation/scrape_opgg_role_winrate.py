"""
python3 -m lol.data_preparation.scrape_opgg_role_winrate
"""

import json
import os

from bs4 import BeautifulSoup
from bs4.element import Tag

from lol import roles


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
    os.makedirs("data/roles", exist_ok=True)

    for role in roles:
        d = scrape_role(f"assets/roles/{role}.html")

        with open(f"data/roles/{role}.json", "w") as f:
            json.dump(d, f)


main() if __name__ == "__main__" else None
