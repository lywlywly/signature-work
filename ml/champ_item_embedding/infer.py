import argparse

import torch
from .champ_item_embedding import *

net = build_net()
file_path = "champ_item_embedding/champ_item_embedding.pth"
net.load_state_dict(
    torch.load(file_path, map_location=torch.device("cpu")),
)
w1 = net[0].weight.data
w2 = net[1].weight.data


def infer(champ_idx: int, item_idx: int) -> float:
    """
    Cosine similarity.
    """
    if not champ_idx or not item_idx:
        return 0.0
    return (
        (
            torch.sum(w1[champ_idx] * w2[item_idx])
            / (torch.norm(w1[champ_idx]) * torch.norm(w2[item_idx]))
        )
        .cpu()
        .item()
    )


def main():
    parser = argparse.ArgumentParser(description="Champ-item compatability score")
    parser.add_argument("c", type=int, help="Champion index")
    parser.add_argument("i", type=int, help="Item index")
    args = parser.parse_args()

    print(infer(args.c, args.i))


main() if __name__ == "__main__" else None
