"""
python3 -m lol.data_preparation.fetch_opgg_role_html
"""

import os

from lol.data_preparation.common import fetch_html_headless_chrome
from lol import HTML_DIR, roles


def main():
    role_url_template = "https://www.op.gg/champions?position={role}"

    for role in roles:
        fetch_html_headless_chrome(
            role_url_template.format(role=role),
            os.path.join(HTML_DIR, f"{role}.html"),
        )


main() if __name__ == "__main__" else None
