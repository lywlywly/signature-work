import json

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
CHAMP_SIZE = 167
ITEM_SIZE = 141
EMBED_SIZE = 10


def skip_gram(champ, item, embed_v, embed_u):
    v = embed_v(champ)
    u = embed_u(item)
    pred = torch.matmul(v, u.permute(0, 2, 1))
    return pred


class SigmoidBCELoss(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, inputs, target, weight):
        assert inputs.shape == target.shape
        batch_size = inputs.shape[0]
        all_losses = nn.functional.binary_cross_entropy_with_logits(
            inputs, target, reduction="none"
        )
        avg_loss = torch.sum(weight * all_losses) / batch_size
        return avg_loss


def build_net():
    net = nn.Sequential(
        nn.Embedding(num_embeddings=CHAMP_SIZE, embedding_dim=EMBED_SIZE),
        nn.Embedding(num_embeddings=ITEM_SIZE, embedding_dim=EMBED_SIZE),
    )
    net = net
    return net


class CustomDataset(Dataset):
    def __init__(self, _weight):
        weight_cvt_to_int_idx = {
            int(k): {int(_k): _v for _k, _v in v.items()} for k, v in _weight.items()
        }
        weight_sorted = dict(sorted(weight_cvt_to_int_idx.items(), key=lambda x: x[0]))
        self.weight_items = [list(v.items()) for v in weight_sorted.values()]
        self.length = sum([len(v) for v in weight_sorted.values()])
        champ_item = {
            int(k): set(int(k) for k in v.keys()) for k, v in weight_sorted.items()
        }
        all_item_set = set(range(141))
        self.champ_not_item = {k: list(all_item_set - v) for k, v in champ_item.items()}

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        c = index // 30
        i = index % 30
        item = self.weight_items[c][i]
        return c, item[0], item[1]


def build_dataloader():
    with open("weight.json", "r") as f:
        weight = json.load(f)

    dataset = CustomDataset(weight)
    batch_size = 5
    shuffle = True
    num_workers = 1
    dataloader = DataLoader(
        dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers
    )
    return dataloader


def init_weights(module):
    if type(module) == nn.Embedding:
        nn.init.xavier_uniform_(module.weight)


def train(net: nn.Sequential, dataloader, loss):
    lr, num_epochs = 0.001, 10
    net.apply(init_weights)
    net = net
    optimizer = torch.optim.Adam(net.parameters(), lr=lr)

    target = torch.tensor([[1.0] * 5])
    losses = []
    for i in range(num_epochs):
        _losses = []
        print(i + 1)
        for batch in dataloader:
            optimizer.zero_grad()
            champ, item, weight = [data for data in batch]
            pred = skip_gram(champ.reshape(-1, 1), item.reshape(-1, 1), net[0], net[1])
            l = loss(pred, target.reshape(-1, 1, 1), weight)
            l.backward()
            optimizer.step()
            _losses.append(l.item())

        losses.append(sum(_losses) / len(_losses))

    return losses
