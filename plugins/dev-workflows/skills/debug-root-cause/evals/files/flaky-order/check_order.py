"""Two startup schedules from a reported CI failure; no wall-clock sleeps."""

import argparse
import random
import sys


def run(order):
    cache = {}

    def load():
        cache["ready"] = True

    def serve():
        return cache.get("ready", False)

    if order == "load-first":
        load()
        return serve()
    result = serve()
    load()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", choices=["load-first", "serve-first"])
    args = parser.parse_args()
    order = args.order or random.choice(["load-first"] * 4 + ["serve-first"])
    ok = run(order)
    print(f"order={order} ready={ok}")
    sys.exit(0 if ok else 1)
