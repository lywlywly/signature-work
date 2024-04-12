"""
python3 -m lol.data_preparation.fetch_opgg_role_html
"""

import os

from lol import roles
from lol.data_preparation.common import fetch_html_headless_chrome


def main():
    os.makedirs("assets/roles", exist_ok=True)

    role_url_template = "https://www.op.gg/champions?position={role}"

    for role in roles:
        fetch_html_headless_chrome(
            role_url_template.format(role=role), f"assets/roles/{role}.html"
        )


main() if __name__ == "__main__" else None
