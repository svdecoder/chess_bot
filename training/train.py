import os
import sys
import glob
import argparse

sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from network import ValueNetwork


def loadDataset(pattern):
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No data files matched: {pattern}")

    allX, allY = [], []
    for f in files:
        data = np.load(f)
        allX.append(data["X"])
        allY.append(data["y"])
        print(f"Loaded {data['X'].shape[0]} positions from {f}")

    return np.concatenate(allX, axis=0), np.concatenate(allY, axis=0)


def train(dataPattern, outPath, epochs=20, batchSize=256, learningRate=1e-3,
          valSplit=0.1, resumeFrom=None, seed=0, updatePST=False):
    X, y = loadDataset(dataPattern)
    n = X.shape[0]
    print(f"Total positions: {n}")

    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    X, y = X[perm], y[perm]

    valCount = int(n * valSplit)
    XVal, yVal = X[:valCount], y[:valCount]
    XTrain, yTrain = X[valCount:], y[valCount:]

    network = ValueNetwork.load(resumeFrom) if resumeFrom else ValueNetwork()

    numBatches = max(1, len(XTrain) // batchSize)
    for epoch in range(1, epochs + 1):
        epochPerm = rng.permutation(len(XTrain))
        XTrain, yTrain = XTrain[epochPerm], yTrain[epochPerm]

        totalLoss = 0.0
        for b in range(numBatches):
            batchX = XTrain[b * batchSize:(b + 1) * batchSize]
            batchY = yTrain[b * batchSize:(b + 1) * batchSize]
            totalLoss += network.trainStep(batchX, batchY, learningRate=learningRate)
        trainLoss = totalLoss / numBatches

        if valCount > 0:
            valPred = network.predict(XVal)
            valLoss = float(np.mean(((valPred - yVal) / 1000.0) ** 2))
            print(f"epoch {epoch:3d}  train MSE {trainLoss:.5f}  val MSE {valLoss:.5f}")
        else:
            print(f"epoch {epoch:3d}  train MSE {trainLoss:.5f}")

    os.makedirs(os.path.dirname(outPath) or ".", exist_ok=True)
    network.save(outPath)
    print(f"Saved trained network to {outPath}")

    if updatePST:
        from updatePst import updateLearnedPST
        updateLearnedPST(network)

    return network


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the value network on self-play data.")
    parser.add_argument("--data", type=str, default="training/data/*.npz")
    parser.add_argument("--out", type=str, default="training/weights.pt")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--resume-from", type=str, default=None)
    parser.add_argument("--update-pst", action="store_true")
    args = parser.parse_args()

    train(
        dataPattern=args.data,
        outPath=args.out,
        epochs=args.epochs,
        batchSize=args.batch_size,
        learningRate=args.lr,
        resumeFrom=args.resume_from,
        updatePST=args.update_pst,
    )
