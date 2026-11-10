import argparse
import json
import os
import time

import numpy as np
import requests


def summary(values):
    return {
        "mean": round(float(np.mean(values)), 2),
        "p50": round(float(np.percentile(values, 50)), 2),
        "p95": round(float(np.percentile(values, 95)), 2),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--file", default="samples/yes.wav")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    url = args.url.rstrip("/")
    if not url.endswith("/predict"):
        url += "/predict"

    with open(args.file, "rb") as f:
        audio = f.read()

    session = requests.Session()
    server, client = [], []
    for i in range(args.warmup + args.n):
        t0 = time.perf_counter()
        r = session.post(url, files={"file": ("a.wav", audio, "audio/wav")})
        dt = (time.perf_counter() - t0) * 1000
        r.raise_for_status()
        if i >= args.warmup:
            client.append(dt)
            server.append(r.json()["latency_ms"])

    result = {
        "n": args.n,
        "latency_ms": summary(server),
        "client_latency_ms": summary(client),
    }
    print("Latency (сервер):", result["latency_ms"])
    print("Latency (клієнт):", result["client_latency_ms"])
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()