import os
import sys

sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import numpy as np
import torch
import torch.nn as nn

from features import positionToFeatures, NUM_FEATURES

SCORE_SCALE = 1000.0
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ValueNetwork:
    def __init__(self, sizes=(NUM_FEATURES, 128, 32, 1), seed=42):
        torch.manual_seed(seed)
        self.sizes = list(sizes)

        layers = []
        for inSize, outSize in zip(sizes[:-1], sizes[1:]):
            layers.append(nn.Linear(inSize, outSize))
            layers.append(nn.ReLU())
        layers[-1] = nn.Tanh()
        self.model = nn.Sequential(*layers).to(DEVICE)

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)

    def toTensor(self, X):
        return torch.as_tensor(np.asarray(X, dtype=np.float32), device=DEVICE)

    def predict(self, X):
        self.model.eval()
        with torch.no_grad():
            output = self.model(self.toTensor(X))
        return output.reshape(-1).cpu().numpy() * SCORE_SCALE

    def trainStep(self, X, targets, learningRate=1e-3, beta1=0.9, beta2=0.999, eps=1e-8):
        self.model.train()
        for group in self.optimizer.param_groups:
            group["lr"] = learningRate
            group["betas"] = (beta1, beta2)
            group["eps"] = eps

        X = self.toTensor(X)
        y = self.toTensor(targets).reshape(-1, 1) / SCORE_SCALE

        output = self.model(X)
        loss = torch.mean((output - y) ** 2)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return float(loss.item())

    def save(self, path):
        torch.save({"sizes": self.sizes, "state_dict": self.model.state_dict()}, path)

    @classmethod
    def load(cls, path):
        checkpoint = torch.load(path, map_location=DEVICE)
        net = cls(sizes=checkpoint["sizes"])
        net.model.load_state_dict(checkpoint["state_dict"])
        return net


def makeEvalFn(network):
    def evaluateNN(position):
        features = positionToFeatures(position).reshape(1, -1)
        score = float(network.predict(features)[0])
        return score if position.sideToMove == 0 else -score

    return evaluateNN
