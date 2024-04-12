"""
python3 -m lol.data_preparation.fetch_opgg_champ_build_html
"""

import json
import os
import re

from lol import roles
from lol.data_preparation.common import fetch_html_headless_chrome


def make_item_urls(pos_list: list[str], pos: str):
    names_in_url: list[str] = [
        re.sub(
            r"&.*",
            "",
            name.lower()
            .replace("'", "")
            .replace(" ", "")
            .replace(".", "")
            .replace("wukong", "monkeyking")
            .replace("renataglasc", "renata"),
        )
        for name in pos_list
    ]  # TODO

    urls = [(name, pos, make_url(champ_name=name, pos=pos)) for name in names_in_url]

    return urls


def make_url(champ_name: str, pos: str):
    return "https://www.op.gg/champions/{champ}/items/{pos}".format(
        champ=champ_name, pos=pos
    )


def main():
    urls: list[tuple[str, str, str]] = []
    failed: dict[str, list[str]] = {role: [] for role in roles}

    with open("data/roles/all.json", "r") as f:
        champs = json.load(f)

    for role in roles:
        os.makedirs(f"assets/roles/{role}/", exist_ok=True)
        urls.extend(make_item_urls(champs[role], role))

    for name, pos, url in urls:
        print(name, pos, url)
        try:
            if os.stat(f"assets/roles/{pos}/{name}.html").st_size > 100000:
                print("continue")
                continue
        except FileNotFoundError as e:
            print("file not found")
            pass

        try:
            fetch_html_headless_chrome(url, f"assets/roles/{pos}/{name}.html")
        except Exception as e:
            failed[pos].append(name)

    print(failed)
    with open("failed.json", "w") as f:
        json.dump(failed, f)


main() if __name__ == "__main__" else None
