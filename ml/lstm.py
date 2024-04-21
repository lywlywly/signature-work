import pickle

import torch
import torch.nn as nn
from sklearn.discriminant_analysis import StandardScaler
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class LSTM(nn.Module):
    def __init__(self, input_size=7, hidden_size=50, out_size=1):
        super().__init__()
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size)
        self.linear = nn.Linear(hidden_size, out_size)
        self.hidden = (torch.zeros(1, 1, hidden_size), torch.zeros(1, 1, hidden_size))

    def forward(self, seq):
        lstm_out, self.hidden = self.lstm(seq.view(len(seq), 1, -1), self.hidden)
        pred = self.linear(lstm_out.view(len(seq), -1))
        return torch.sigmoid(pred[-1])


def input_data(seq, target, ws=5):
    out = []
    L = len(seq)
    for i in range(L - ws):
        window = seq[i : i + ws]
        out.append((window, target))

    return out


def load_standard_scaler():
    with open("standard_scaler.pkl", "rb") as f:
        stand_scalar: StandardScaler = pickle.load(f)
    return stand_scalar


def load_model():
    model = LSTM()
    checkpoint = torch.load("lstm.pth", map_location=torch.device("cpu"))
    model.load_state_dict(checkpoint["model_state_dict"])
    return model


stand_scalar = load_standard_scaler()
model = load_model()


def infer(input):
    input = stand_scalar.transform(input)
    tensor = torch.tensor(input)
    return _infer(model, tensor)


def _infer(model, input):
    result = model(input).detach().item()

    return result
