"""
python3 -m lol.data_preparation.fetch_opgg_champ_build_html
"""

from functools import reduce
import json
import os
import re

from lol import HTML_DIR, ROLES_DIR, roles
from lol.data_preparation.common import fetch_html_headless_chrome


replacements = {
    "'": "",
    " ": "",
    ".": "",
    "wukong": "monkeyking",
    "renataglasc": "renata",
}


def make_item_urls(pos_list: list[str], pos: str):
    names_in_url: list[str] = [
        reduce(
            lambda acc, kv: acc.replace(*kv),
            replacements.items(),
            re.sub(r"&.*", "", name.lower()),
        )
        for name in pos_list
    ]

    urls = [(name, pos, make_url(champ_name=name, pos=pos)) for name in names_in_url]

    return urls


def make_url(champ_name: str, pos: str):
    return "https://www.op.gg/champions/{champ}/items/{pos}".format(
        champ=champ_name, pos=pos
    )


def main():
    urls: list[tuple[str, str, str]] = []
    failed: dict[str, list[str]] = {role: [] for role in roles}

    with open(os.path.join(ROLES_DIR, "pos_champ_dict_opgg.json"), "r") as f:
        champs = json.load(f)

    for role in roles:
        os.makedirs(os.path.join(HTML_DIR, role), exist_ok=True)
        urls.extend(make_item_urls(champs[role], role))

    for name, pos, url in urls:
        print(name, pos, url)
        html_path = os.path.join(HTML_DIR, pos, f"{name}.html")
        try:
            if os.stat(html_path).st_size > 100000:
                print("continue")
                continue
        except FileNotFoundError as e:
            print("file not found")
            pass

        try:
            fetch_html_headless_chrome(url, html_path)
        except Exception as e:
            print(e)
            failed[pos].append(name)

    print(failed)
    with open("failed.json", "w") as f:
        json.dump(failed, f)


main() if __name__ == "__main__" else None
