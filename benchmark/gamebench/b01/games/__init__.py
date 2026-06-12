"""Game registry: collects GAME dicts from b1/games/ and b1/holdout/."""

import importlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HOLDOUT = os.path.join(os.path.dirname(HERE), "holdout")


def _collect(folder, pkg):
    games = {}
    for f in sorted(os.listdir(folder)):
        if f.endswith(".py") and not f.startswith("_"):
            mod = importlib.import_module(f"{pkg}.{f[:-3]}")
            g = mod.GAME
            games[g["game"]] = g
    return games


def registry():
    games = _collect(HERE, "benchmark.gamebench.b01.games")
    games.update(_collect(HOLDOUT, "benchmark.gamebench.b01.holdout"))
    return games
